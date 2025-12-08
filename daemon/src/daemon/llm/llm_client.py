import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from daemon.logger.log_utils import Logger


logger = Logger()


class LLMClient:
    def __init__(self, config: Dict[str, Any]):
        self.provider = config.get("provider", "openai")
        self.model_config = config.get(self.provider, {})
        self.model_name = self.model_config.get("model", "gpt-4o-mini")
        self.temperature = self.model_config.get("temperature", 0.1)
        
        self.client = self._init_model()
        logger.info(f"✅ LangChain LLM client initialized: {self.provider}/{self.model_name}")
    
    def _init_model(self):
        """Initialize LangChain chat model based on provider."""
        provider = self.provider
        
        if provider == "openai":
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                api_key=os.getenv("OPENAI_API_KEY"),
                max_retries=3,
            )
        elif provider == "anthropic":
            return ChatAnthropic(
                model=self.model_name,
                temperature=self.temperature,
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
        elif provider == "ollama":
            return ChatOllama(
                model=self.model_name,
                temperature=self.temperature,
                base_url=self.model_config.get("base_url", "http://localhost:11434"),
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: int = 4000,
        **kwargs
    ) -> str:
        """Simple text generation."""
        try:
            model = model or self.model_name
            temp = temperature or self.temperature
            
            # Create simple prompt
            chat_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant."),
                ("user", "{input}")
            ])
            
            chain = chat_prompt | self.client
            response = chain.invoke({
                "input": prompt,
                "max_tokens": max_tokens,
            })
            
            content = response.content
            logger.info(f"✅ LLM generated {len(content)} chars")
            return content
            
        except Exception as e:
            logger.error(f"❌ LLM generation failed: {e}")
            raise RuntimeError(f"LLM generation failed: {e}")
    
    def extract_structured(
        self,
        content: str,
        schema: Dict[str, Any],
        instructions: str = "Extract all data according to the schema. Respond with valid JSON only."
    ) -> Dict[str, Any]:
        """Structured extraction with JSON schema enforcement."""
        try:
            # Dynamic Pydantic model from schema
            class ExtractionSchema(BaseModel):
                pass
            
            # Create parser
            parser = JsonOutputParser(pydantic_object=ExtractionSchema)
            
            prompt = ChatPromptTemplate.from_template("""
                {instructions}

                Schema:
                {schema}

                Content:
                {content}

                {format_instructions}
            """)
            
            chain = prompt | self.client | parser
            result = chain.invoke({
                "instructions": instructions,
                "schema": json.dumps(schema),
                "content": content,
                "format_instructions": parser.get_format_instructions(),
            })
            
            logger.info(f"✅ Structured extraction: {len(result)} fields")
            return result
            
        except Exception as e:
            logger.error(f"❌ Structured extraction failed: {e}")
            # Fallback to simple generation
            return {"raw_response": self.generate(content[:4000]), "error": str(e)}
    
    def summarize(
        self,
        content: str,
        level: str = "executive",
        max_length: int = 300
    ) -> str:
        """Generate summary at specified level."""
        prompt_template = f"""
        Generate a {level} summary (max {max_length} words) of the following document.
        Focus on key points, decisions, and action items.

        Document:
        {{content}}
        """
        
        prompt = PromptTemplate.from_template(prompt_template)
        chain = prompt | self.client
        
        summary = chain.invoke({
            "content": content[:8000]  # Truncate for cost
        }).content
        
        logger.info(f"📝 Generated {level} summary: {len(summary)} chars")
        return summary
    
    def generate_chain(self, steps: List[Dict[str, Any]]) -> Any:
        """Build complex multi-step LLM chain from workflow."""
        # Placeholder for advanced workflow chaining
        logger.info(f"🔗 Building chain with {len(steps)} steps")
        return self
