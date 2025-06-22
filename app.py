import os
import uuid
import json
from dotenv import load_dotenv
from datetime import datetime

import chainlit as cl

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
PINECONE_REGION = os.getenv("PINECONE_ENV")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")

# Initialize Gemini LLM and Embeddings
llm = ChatGoogleGenerativeAI(api_key=GOOGLE_API_KEY, model="gemini-1.5-flash")
embedder = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index if it doesn't exist
if PINECONE_INDEX not in [idx.name for idx in pc.list_indexes()]:
    pc.create_index(
        name=PINECONE_INDEX,
        dimension=768,  # Gemini embedding size
        metric="cosine",
        spec=ServerlessSpec(
            cloud=PINECONE_CLOUD,
            region=PINECONE_REGION
        )
    )
index = pc.Index(PINECONE_INDEX)

SYSTEM_PROMPT = (
    "You are a helpful, supportive, and empathetic therapy chatbot. "
    "Always respond with kindness and understanding. "
    "Do not provide medical advice or make diagnoses. "
    "Encourage users to seek professional help if they mention serious issues."
)

def sanitize_metadata_value(val):
    # Pinecone only accepts str, int, float, bool, or list of str
    if val is None:
        return ""
    if isinstance(val, (str, int, float, bool)):
        return val
    return str(val)

def store_message(user_id, session_id, speaker, text, timestamp):
    embedding = embedder.embed_query(text)
    vector_id = str(uuid.uuid4())
    metadata = {
        "user_id": sanitize_metadata_value(user_id),
        "session_id": sanitize_metadata_value(session_id),
        "timestamp": sanitize_metadata_value(timestamp),
        "speaker": sanitize_metadata_value(speaker),
        "text": sanitize_metadata_value(text)
    }
    index.upsert([(vector_id, embedding, metadata)])

def semantic_retrieve(user_id, query_text, top_k=5):
    query_vector = embedder.embed_query(query_text)
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        filter={"user_id": {"$eq": sanitize_metadata_value(user_id)}},
        include_metadata=True
    )
    sorted_results = sorted(
        [match["metadata"] for match in results["matches"]],
        key=lambda x: x.get("timestamp", "")
    )
    return sorted_results

@cl.on_chat_start
async def on_chat_start():
    await cl.Message("Welcome to the Therapy Bot! Please enter your user ID:").send()
    user_id_msg = await cl.AskUserMessage("Enter your user ID (or username):").send()

    # Corrected extraction: use 'output' field
    if isinstance(user_id_msg, dict):
        user_id = user_id_msg.get("output")
    else:
        user_id = str(user_id_msg).strip()

    if user_id:
        session_id = str(uuid.uuid4())
        cl.user_session.set("user_id", user_id)
        cl.user_session.set("session_id", session_id)
        cl.user_session.set("chat_history", [])
        await cl.Message(f"Hello, {user_id}! How can I help you today?").send()
    else:
        await cl.Message("No user ID provided. Please type your user ID as your first chat message.").send()

@cl.on_message
async def on_message(message: cl.Message):
    user_id = cl.user_session.get("user_id")
    session_id = cl.user_session.get("session_id")
    chat_history = cl.user_session.get("chat_history") or []
    user_text = message.content
    timestamp = datetime.utcnow().isoformat()

    # If user_id is not set, treat the first message as user_id
    if not user_id:
        user_id = user_text.strip()
        if not user_id:
            await cl.Message("No user ID provided. Please refresh and try again.").send()
            return
        session_id = str(uuid.uuid4())
        cl.user_session.set("user_id", user_id)
        cl.user_session.set("session_id", session_id)
        cl.user_session.set("chat_history", chat_history)
        await cl.Message(f"Hello, {user_id}! How can I help you today?").send()
        return

    # Store the user message in Pinecone
    store_message(user_id, session_id, "user", user_text, timestamp)
    chat_history.append({
        "speaker": "user",
        "text": user_text,
        "timestamp": timestamp
    })

    # Semantic retrieval for relevant context
    relevant_history = semantic_retrieve(user_id, user_text, top_k=5)
    context = "\n".join([f"{h['speaker']}: {h['text']}" for h in relevant_history])
    prompt = (
        SYSTEM_PROMPT + "\n"
        + (context + "\n" if context else "")
        + f"user: {user_text}\nbot:"
    )

    # Get Gemini response
    bot_response = llm.invoke(prompt)
    content = bot_response.content
    if isinstance(content, list):
        content = content[0]

    # Store the bot response in Pinecone
    bot_timestamp = datetime.utcnow().isoformat()
    store_message(user_id, session_id, "bot", content, bot_timestamp)
    chat_history.append({
        "speaker": "bot",
        "text": content,
        "timestamp": bot_timestamp
    })

    # Update session chat history
    cl.user_session.set("chat_history", chat_history)

    # Send the response back to the user
    await cl.Message(content).send()

