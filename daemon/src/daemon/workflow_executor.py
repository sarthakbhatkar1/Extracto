from daemon.constants.enums import StepMethod
from daemon.processors.ingest import IngestingProcessor
from daemon.processors.parse import DoclingParser
from daemon.processors.extract import ExtractingProcessor
from daemon.processors.summarize import SummarizingProcessor


class WorkflowExecutor:
    def __init__(self, session):
        self.session = session
        self.ingestor = IngestingProcessor()
        self.parser = DoclingParser()
        self.extractor = ExtractingProcessor()
        self.summarizer = SummarizingProcessor()

    async def execute(self, task, workflow: dict):
        context = {}

        for step in workflow.get("steps", []):
            if not step.get("enabled", True):
                continue

            method = StepMethod(step["method"])
            config = step.get("config", {})

            if method == StepMethod.INGESTING:
                context["paths"] = self.ingestor.ingest(task, self.session)

            elif method == StepMethod.PARSING:
                context["text"] = self.parser.parse_documents(
                    task, context["paths"]
                )

            elif method == StepMethod.EXTRACTING:
                context["extracted"] = await self.extractor.run(
                    task, context["text"], config
                )

            elif method == StepMethod.SUMMARIZING:
                context["summary"] = await self.summarizer.run(
                    task, context["text"], config
                )

        task.AI_RESULT = context.get("extracted", {})
        task.OUTPUT = {
            "summary": context.get("summary")
        }

        self.session.commit()
