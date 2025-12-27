from daemon.constants.enums import StepMethod
from daemon.status_utils import start_step, complete_step, fail_step
from daemon.llm.llm_client import LLMClient


class ExtractingProcessor:
    def __init__(self):
        self.llm = LLMClient()

    async def run(self, task, text: str, config: dict) -> dict:
        try:
            start_step(task, StepMethod.EXTRACTING)

            schema = config.get("schema")
            if not schema:
                raise ValueError("Extraction schema missing in workflow config")

            result = await self.llm.extract(text, schema)

            complete_step(task, StepMethod.EXTRACTING)
            return result

        except Exception as e:
            fail_step(task, StepMethod.EXTRACTING, str(e))
            raise
