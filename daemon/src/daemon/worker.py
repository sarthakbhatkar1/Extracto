import asyncio

from daemon.db.azure.base import DBConnection
from daemon.llm.llm_client import LLMClient
from daemon.processors.parse import DoclingParser
from daemon.task_repository import TaskRepository

class ExtractoWorker:

    def __init__(self):
        self.llm = LLMClient()

    async def run_forever(self):
        session = DBConnection().get_session()
        while True:
            task = TaskRepository.fetch_next_task(session)

            if not task:
                await asyncio.sleep(2)
                continue

            try:
                await self.process_task(session, task)
            except Exception as e:
                TaskRepository.fail(session, task, str(e))

    async def process_task(self, session, task):
        #TODO: Redo the logic in process task to work with workflow config

        # Ingestion
        TaskRepository.update_status(session, task, "INGESTING")

        # Load + Parse documents
        TaskRepository.update_status(session, task, "PARSING")
        text = await DoclingParser().parse_documents(task.DOCUMENT_IDS)

        # Extract
        TaskRepository.update_status(session, task, "EXTRACTING")
        extracted = await self.llm.extract(
            text=text,
            schema={}  # fetch from Project.WORKFLOW later
        )

        # Summarize
        TaskRepository.update_status(session, task, "SUMMARIZING")
        summary = await self.llm.summarize(text)

        TaskRepository.succeed(
            session,
            task,
            ai_result=extracted,
            output={"summary": summary}
        )
