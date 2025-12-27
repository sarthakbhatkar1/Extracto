import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class LLMClient:
    def __init__(
        self,
        api_key: str = os.getenv("API_KEY"),
        model: str = "gpt-4o-mini",
        temperature: float = 0
    ):
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=temperature
        )

    async def extract(self, text: str, schema: dict) -> dict:
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a strict information extraction engine. "
                "Return ONLY valid JSON strictly matching the provided schema."
            ),
            (
                "human",
                "Schema:\n{schema}\n\nDocument:\n{text}"
            )
        ])

        chain = prompt | self.llm | StrOutputParser()

        return await chain.ainvoke({
            "schema": schema,
            "text": text
        })

    async def summarize(self, text: str, style: str = "concise") -> str:
        system_prompt = (
            "Generate a concise, factual summary."
            if style == "concise"
            else "Generate a detailed, structured summary."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{text}")
        ])

        chain = prompt | self.llm | StrOutputParser()

        return await chain.ainvoke({"text": text})
