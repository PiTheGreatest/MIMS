import os
import logging
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from .prompts import DOCTOR_SYSTEM_PROMPT, PATIENT_SYSTEM_PROMPT
from app.services.ai_service import get_relevant_history

logger = logging.getLogger("MIMS_AUDIT")

class MIMSAiAssistant:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="llama-3.3-70b-versatile", 
            openai_api_key=os.environ.get("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small", 
            openai_api_key=api_key
        )
        self.search_tool = TavilySearchResults(k=3)

    async def generate_public_search_response(self, query: str):
        try:
            search_results = await self.search_tool.ainvoke({"query": query})
            system_content = (
                "You are the MIMS Health Navigator. Provide accurate medical information. "
                "1. DO NOT diagnose. 2. Use lists. 3. Include Triage. "
                "4. MANDATORY FOOTER: 'This is information, not a medical diagnosis. Consult a licensed doctor via MIMS.'"
            )
            messages = [
                SystemMessage(content=system_content),
                SystemMessage(content=f"Search Evidence: {search_results}"),
                HumanMessage(content=query)
            ]
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"GROQ_SEARCH_ERROR: {str(e)}")
            return "The Health Navigator is temporarily adjusting. Please try again."

    async def generate_clinical_response(self, role: str, query: str, context: str = ""):
        try:
            query_vector = await self.embeddings.aembed_query(query)
            historical_records = get_relevant_history(query_vector, limit=3)
            history_str = "\n".join([f"- Past Note: {r.note_content}" for r in historical_records])
            system_content = DOCTOR_SYSTEM_PROMPT if role.lower() == "doctor" else PATIENT_SYSTEM_PROMPT
            messages = [
                SystemMessage(content=system_content),
                SystemMessage(content=f"Relevant History:\n{history_str}"),
                SystemMessage(content=f"Current Context: {context}"),
                HumanMessage(content=query)
            ]
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"CLINICAL_GROQ_ERROR: {str(e)}")
            raise e