"""
daemon/worker.py - Main daemon worker for Extracto document processing pipeline
Handles task polling, locking, document processing, LLM orchestration, and result persistence.
"""

import time
import json
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from daemon.common.config.config_store import ConfigStore
from daemon.db.azure.base import DBConnection
from daemon.db.model import (
    Task, WorkflowConfig, Document
)

from daemon.utils.util import TaskStatumEnum
from daemon.logger.log_utils import Logger
from daemon.common.storage.s3_file_manager import S3FileManager as StorageClient  # Your Extracto common package
from daemon.llm.llm_client import LLMClient  # LLM service integration
from daemon.utils.util import validate_json_against_schema


logger = Logger()
config = ConfigStore()
storage = StorageClient(config.storage)  # Azure/S3/local
llm_client = LLMClient(config.llm)  # OpenAI/Anthropic/etc.


class TaskStatusEnum(Enum):  # Extend your existing enum
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    PARSING = "Parsing"
    EXTRACTING = "Extracting"
    SUMMARIZING = "Summarizing"
    VALIDATING = "Validating"
    COMPLETED = "Success"
    FAILURE = "Failure"


def get_session() -> Session:
    """Get a new DB session."""
    return DBConnection().get_session()


def fetch_and_lock_pending_task(session: Session) -> Optional[Task]:
    """Atomically fetch and lock a NOT_STARTED task for processing."""
    try:
        task: Task = (
            session.query(Task)
            .filter(Task.STATUS == TaskStatusEnum.NOT_STARTED.value)
            .order_by(Task.MODIFIED_AT.desc())
            .with_for_update(skip_locked=True)
            .first()
        )
        if not task:
            return None

        task.STATUS = TaskStatusEnum.IN_PROGRESS.value
        task.MODIFIED_AT = datetime.utcnow()
        session.commit()
        logger.info(f"✅ Locked task {task.ID} for processing")
        return task
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Error locking task: {e}")
        return None


def load_workflow_config(session: Session, workflow_id: str) -> WorkflowConfig:
    """Load workflow configuration for the task."""
    workflow = session.query(WorkflowConfig).filter(
        WorkflowConfig.ID == workflow_id
    ).first()
    if not workflow:
        raise RuntimeError(f"WorkflowConfig not found: {workflow_id}")
    return workflow


def load_documents(session: Session, document_ids: List[str]) -> List[Document]:
    """Load documents associated with the task."""
    if not document_ids:
        raise RuntimeError("No document IDs in task")
    
    docs = session.query(Document).filter(
        Document.ID.in_(document_ids)
    ).all()
    if len(docs) != len(document_ids):
        raise RuntimeError(f"Missing documents: expected {len(document_ids)}, got {len(docs)}")
    return docs


def fetch_document_content(doc: Document) -> Dict[str, Any]:
    """Fetch document binary from storage and return metadata + content."""
    try:
        content = storage.download(doc.STORAGE_PATH)
        metadata = {
            "name": doc.NAME,
            "type": doc.TYPE,
            "size_bytes": len(content),
            "folder": doc.FOLDER_NAME,
        }
        logger.info(f"📄 Fetched {doc.NAME} ({len(content)} bytes)")
        return {"metadata": metadata, "content": content}
    except Exception as e:
        raise RuntimeError(f"Failed to fetch {doc.NAME}: {e}")


def parse_document_content(content: bytes, doc_type: str) -> Dict[str, Any]:
    """Parse document into structured text (PDF/DOCX/TXT/etc.)."""
    # TODO: Implement with pdfplumber, docx, PyMuPDF, etc.
    # For now, simple text extraction stub
    text = content.decode('utf-8', errors='ignore')[:10000]  # Truncate for demo
    pages = text.split('\n\n')[:10]  # Mock page splitting
    
    result = {
        "raw_text": text,
        "pages": [{"page_num": i, "content": page} for i, page in enumerate(pages)],
        "word_count": len(text.split()),
        "language": "en",  # TODO: langdetect
    }
    logger.info(f"📖 Parsed {doc_type}: {len(pages)} pages, {result['word_count']} words")
    return result


def extract_structured_data(
    parsed_doc: Dict[str, Any], 
    workflow: WorkflowConfig
) -> Dict[str, Any]:
    """Run LLM extraction according to workflow schema."""
    schema = workflow.WORKFLOW.get("extraction_schema", {})
    
    prompt = f"""
    Extract structured data from this document according to the following JSON schema:
    {json.dumps(schema, indent=2)}
    
    Document content:
    {parsed_doc['raw_text'][:4000]}
    
    Respond ONLY with valid JSON matching the schema.
    """
    
    response = llm_client.generate(
        prompt=prompt,
        model=workflow.WORKFLOW.get("model", "gpt-4o-mini"),
        temperature=0.1,
        max_tokens=2000,
    )
    
    # Validate and repair if needed
    extracted = validate_json_against_schema(response, schema)
    logger.info(f"🔍 Extracted {len(extracted)} entities")
    return extracted


def generate_summaries(
    parsed_doc: Dict[str, Any], 
    workflow: WorkflowConfig
) -> Dict[str, Any]:
    """Generate multi-level summaries."""
    levels = workflow.WORKFLOW.get("summaries", ["executive", "detailed"])
    summaries = {}
    
    for level in levels:
        prompt = f"""
        Generate a {level} summary of this document (max 300 words):
        {parsed_doc['raw_text'][:8000]}
        
        Focus on key points, decisions, and action items.
        """
        
        summary = llm_client.generate(
            prompt=prompt,
            model=workflow.WORKFLOW.get("model", "gpt-4o-mini"),
            temperature=0.3,
            max_tokens=500,
        )
        summaries[level] = summary
    
    logger.info(f"📝 Generated {len(summaries)} summary levels")
    return summaries


def process_documents_with_workflow(
    workflow: WorkflowConfig,
    documents: List[Document],
) -> Dict[str, Any]:
    """Full document processing pipeline."""
    results = []
    
    for doc in documents:
        try:
            # 1. Fetch from storage
            doc_data = fetch_document_content(doc)
            
            # 2. Parse/normalize
            parsed = parse_document_content(
                doc_data["content"], 
                doc.TYPE
            )
            
            # Update task status
            # Note: This would need session passed in for real status updates
            
            # 3. Structured extraction
            extracted = extract_structured_data(parsed, workflow)
            
            # 4. Summarization
            summaries = generate_summaries(parsed, workflow)
            
            result = {
                "document_id": str(doc.ID),
                "metadata": doc_data["metadata"],
                "parsed": parsed,
                "extracted": extracted,
                "summaries": summaries,
                "processing_stats": {
                    "tokens_in": len(parsed["raw_text"]) // 4,
                    "processing_time_ms": 0,  # Measure in production
                }
            }
            results.append(result)
            
        except Exception as e:
            logger.error(f"❌ Processing failed for {doc.NAME}: {e}")
            results.append({"document_id": str(doc.ID), "error": str(e)})
    
    total_stats = {
        "workflow_id": str(workflow.ID),
        "documents_processed": len(results),
        "success_count": len([r for r in results if "error" not in r]),
        "total_tokens": sum(r.get("processing_stats", {}).get("tokens_in", 0) for r in results),
    }
    
    logger.info(f"🎉 Workflow {workflow.ID} completed: {total_stats}")
    return {"results": results, "stats": total_stats}


def update_task_result(
    session: Session,
    task: Task,
    ai_result: Dict[str, Any],
    status: str,
    error_message: Optional[str] = None,
) -> None:
    """Persist task results and final status."""
    try:
        task.AI_RESULT = ai_result
        task.OUTPUT = ai_result  # Or transform for customer-facing format
        task.STATUS = status
        task.MODIFIED_AT = datetime.utcnow()
        
        if error_message:
            task.OUTPUT = {"error": error_message}
            logger.error(f"❌ Task {task.ID} FAILED: {error_message}")
        else:
            logger.info(f"✅ Task {task.ID} COMPLETED")
        
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Error updating task {task.ID}: {e}")
        raise


def execute_once():
    """Single execution cycle: poll → process → store."""
    session = get_session()
    try:
        # Lock a task
        task = fetch_and_lock_pending_task(session)
        if not task:
            logger.debug("No pending tasks. Sleeping...")
            time.sleep(30)
            return

        logger.info(f"🚀 Processing task {task.ID}")
        
        # Load dependencies
        workflow = load_workflow_config(session, task.WORKFLOW_ID)
        documents = load_documents(session, task.DOCUMENT_IDS or [])
        
        # Execute full pipeline
        ai_result = process_documents_with_workflow(workflow, documents)
        
        # Persist success
        update_task_result(
            session=session,
            task=task,
            ai_result=ai_result,
            status=TaskStatusEnum.COMPLETED.value,
        )
        
    except Exception as e:
        logger.error(f"💥 Task execution failed: {e}")
        if 'task' in locals():
            try:
                update_task_result(
                    session=session,
                    task=task,
                    ai_result={"error": str(e)},
                    status=TaskStatusEnum.FAILED.value,
                    error_message=str(e),
                )
            except:
                pass
        time.sleep(10)  # Backoff on errors
    finally:
        session.close()


def main():
    """Daemon entrypoint with graceful shutdown."""
    logger.info("🔥 Extracto Daemon starting...")
    
    try:
        while True:
            execute_once()
    except KeyboardInterrupt:
        logger.info("🛑 Daemon received SIGTERM, shutting down gracefully...")
    except Exception as e:
        logger.error(f"💥 Critical daemon error: {e}")
        time.sleep(5)


if __name__ == "__main__":
    main()
