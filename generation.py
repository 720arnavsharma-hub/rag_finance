import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CHAT_HISTORY = []


def expand_query(query):
    return [
        query,
        f"financial document {query}"
    ]


def generate_answer(context, query):
    global CHAT_HISTORY

    CHAT_HISTORY.append({
        "role": "user",
        "content": query
    })

    messages = [
        {
            "role": "system",
            "content": """You are a document analysis assistant.
Answer questions based ONLY on the provided context.
If the answer is not in the context, say: Not found in document.
Be precise and cite specific details from the context when possible.
If asked to find all instances of something (dates, amounts, names), 
list ALL of them you find in the context."""
        },
        {
            "role": "user",
            "content": f"""Context from documents:
{context}

Question: {query}

Answer:"""
        }
    ]

    # Include last 4 exchanges for chat history
    if len(CHAT_HISTORY) > 1:
        history_messages = []
        for msg in CHAT_HISTORY[-4:]:
            history_messages.append(msg)
        messages = [messages[0]] + history_messages + [messages[-1]]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.2,
        max_tokens=1024
    )

    answer = response.choices[0].message.content

    CHAT_HISTORY.append({
        "role": "assistant",
        "content": answer
    })

    return answer


def clear_history():
    global CHAT_HISTORY
    CHAT_HISTORY = []