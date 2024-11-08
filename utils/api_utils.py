import openai
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import Dict, Any

def validate_api_key(api_key: str) -> bool:
    """Validate OpenAI API key format"""
    return api_key.startswith("sk-")

def initialize_chat_model(model: str, api_key: str, temperature: float = 0.7) -> ChatOpenAI:
    """Initialize ChatOpenAI model with given parameters"""
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        openai_api_key=api_key
    )

def analyze_position(chat_model: ChatOpenAI, prompt_template: str, fen_position: str) -> str:
    """Analyze chess position using the chat model"""
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | chat_model
    response = chain.invoke({"fen_position": fen_position})
    return response.content
