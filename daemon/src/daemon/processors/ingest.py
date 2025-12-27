from typing import List
from pathlib import Path

from sqlalchemy.orm import Session

from daemon.constants.enums import StepMethod
from daemon.utils.status_utils import start_step, complete_step, fail_step
from daemon.db.model import Document


class IngestingProcessor:
    def ingest(self, task, session: Session) -> List[str]:
        """
        Resolves document IDs to local file paths.
        """
        try:
            start_step(task, StepMethod.INGESTING)

            document_paths = []

            documents = (
                session.query(Document)
                .filter(Document.ID.in_(task.DOCUMENT_IDS))
                .all()
            )

            if not documents:
                raise ValueError("No documents found for ingestion")

            for doc in documents:
                path = doc.STORAGE_PATH.get("path")
                if not path:
                    raise ValueError(f"Missing storage path for document {doc.ID}")

                file_path = Path(path)
                if not file_path.exists():
                    raise FileNotFoundError(f"File not found: {file_path}")

                document_paths.append(str(file_path))

            complete_step(task, StepMethod.INGESTING)
            return document_paths

        except Exception as e:
            fail_step(task, StepMethod.INGESTING, str(e))
            raise
