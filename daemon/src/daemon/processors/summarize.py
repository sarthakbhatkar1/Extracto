from daemon.constants.enums import StepMethod
from daemon.status_utils import start_step, complete_step, fail_step
from daemon.llm.llm_client import LLMClient


class SummarizingProcessor:
    def __init__(self):
        self.llm = LLMClient()

    async def run(self, task, text: str, config: dict) -> str:
        try:
            start_step(task, StepMethod.SUMMARIZING)

            style = config.get("style", "concise")
            summary = await self.llm.summarize(text, style)

            complete_step(task, StepMethod.SUMMARIZING)
            return summary

        except Exception as e:
            fail_step(task, StepMethod.SUMMARIZING, str(e))
            raise
