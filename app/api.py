import os

from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

VLLM_URL = os.getenv(
    "VLLM_URL",
    "http://vllm:8000/v1"
)

MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"

client = OpenAI(
    api_key="dummy",
    base_url=VLLM_URL
)


class ChatRequest(BaseModel):
    prompt: str


@app.get("/")
def root():
    return {"message": "AI API is running"}


@app.post("/chat")
def chat(request: ChatRequest):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": request.prompt}
        ],
        max_tokens=50,
    )

    return {
        "response": response.choices[0].message.content
    }