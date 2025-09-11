from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("""
You are an AI assistant tasked with answering questions based on the provided PDF content.
Use the following context and conversation history to generate an accurate and concise response.
If the answer is not in the context, respond with 'I don't know' instead of guessing.

Conversation History: {history}
Context: {context}
Question: {question}
""")