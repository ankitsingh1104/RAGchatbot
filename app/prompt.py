from langchain_core.prompts import PromptTemplate

PROMPT_TEMPLATE = """You are a helpful DevOps assistant. Answer the question using the context below.

CONTEXT:
{retrieved_chunks}

HISTORY:
{chat_history}

QUESTION:
{user_question}

ANSWER:"""

PROMPT = PromptTemplate(
    input_variables=["chat_history", "retrieved_chunks", "user_question"],
    template=PROMPT_TEMPLATE
)