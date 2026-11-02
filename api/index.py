
import os
import logging
import httpx

from fastapi import FastAPI, Request, HTTPException
from openai import AsyncOpenAI

logging.basicConfig(level=logging.INFO)

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

ai = AsyncOpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None


SYSTEM_PROMPT = """
你是 Nova Personal AI Agent。

你负责：
1. 个人工作和长期项目管理。
2. 外汇、黄金和美股分析。
3. MT5 EA策略开发。
4. GitHub和Vercel项目协助。
5. 工程管理和文件整理。

交易规则：
单笔风险不超过1%。
杠杆不超过10倍。
不直接执行实盘交易。
不编造实时市场数据。

使用简体中文回答。
"""


@app.get("/")
async def home():
    return {
        "name": "Nova Personal AI Agent",
        "status": "running"
    }


@app.post("/webhook")
async def telegram_webhook(request: Request):

    if not TOKEN:
        raise HTTPException(
            status_code=500,
            detail="Telegram token missing"
        )

    data = await request.json()

    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    user_text = message.get("text", "")

    if not chat_id or not user_text:
        return {"ok": True}

    if not ai:
        answer = "Nova 已连接，但尚未配置 AI API Key。"
    else:
        try:
            result = await ai.responses.create(
                model=MODEL,
                instructions=SYSTEM_PROMPT,
                input=user_text
            )
            answer = result.output_text or "暂时没有生成回复。"

        except Exception:
            logging.exception("AI error")
            answer = "AI 暂时无法响应，请稍后再试。"

    async with httpx.AsyncClient(timeout=20) as client:
        await client.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": answer[:4000]
            }
        )

    return {"ok": True}
