
import os
import logging
from fastapi import FastAPI
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from openai import OpenAI

logging.basicConfig(level=logging.INFO)

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

SYSTEM_PROMPT = """
你是 Nova，一个全能个人AI助手。

你的任务：
1. 记住用户提供的个人背景和工作进度。
2. 协助外汇、黄金和美股市场分析。
3. 协助MT5 EA开发。
4. 协助GitHub和Vercel项目管理。
5. 协助工程管理和文件整理。

交易规则：
- 单笔风险不超过1%。
- 杠杆不超过10倍。
- 不直接执行实盘交易。
- 重大经济数据公布前提醒风险。
- 不编造实时市场价格。

回答使用简体中文，步骤清晰。
"""

@app.get("/")
async def home():
    return {
        "name": "Nova Personal AI Agent",
        "status": "running"
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "你好，我是 Nova Personal AI Agent。\n"
        "你可以直接发送消息与我交流。"
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not client:
        await update.message.reply_text(
            "AI 尚未配置，请设置 OPENAI_API_KEY。"
        )
        return

    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=SYSTEM_PROMPT,
            input=update.message.text
        )

        answer = response.output_text
        await update.message.reply_text(answer[:4000])

    except Exception:
        logging.exception("AI request failed")
        await update.message.reply_text(
            "暂时无法连接 AI，请稍后再试。"
        )

async def run_bot():
    if not TELEGRAM_TOKEN:
        logging.error("Missing TELEGRAM_BOT_TOKEN")
        return

    bot = Application.builder().token(TELEGRAM_TOKEN).build()

    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
    )

    await bot.initialize()
    await bot.start()
    await bot.updater.start_polling()

