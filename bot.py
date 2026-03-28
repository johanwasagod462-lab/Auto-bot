import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import requests
from deep_translator import GoogleTranslator

# ---------------- CONFIG (ENV) ----------------
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_API_KEY = os.getenv("AI_API_KEY")

# ---------------- APP ----------------
app = Client("ai_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ---------------- DATA ----------------
chat_enabled = {}   # group_id: True/False
user_memory = {}    # user_id: [messages]

# ---------------- AI FUNCTION ----------------
def ask_ai(messages):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": messages
    }

    res = requests.post(url, headers=headers, json=data)
    return res.json()["choices"][0]["message"]["content"]

# ---------------- TRANSLATE ----------------
def to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except:
        return text

def to_burmese(text):
    try:
        return GoogleTranslator(source='en', target='my').translate(text)
    except:
        return text

# ---------------- ADMIN CONTROL ----------------
@app.on_message(filters.command("on") & filters.group)
async def enable_ai(client, message: Message):
    chat_enabled[message.chat.id] = True
    await message.reply_text("Johan နိုးပါပြီဗျ💕👋")

@app.on_message(filters.command("off") & filters.group)
async def disable_ai(client, message: Message):
    chat_enabled[message.chat.id] = False
    await message.reply_text("Johan အိပ်ပါပြီနော် ချစ်လေး💕👋")

# ---------------- MAIN CHAT ----------------
@app.on_message(filters.text & filters.group)
async def chat_bot(client, message: Message):

    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text

    # check enabled
    if not chat_enabled.get(chat_id, True):
        return

    # ignore commands
    if text.startswith("/"):
        return

    # translate to english
    en_text = to_english(text)

    # user memory
    if user_id not in user_memory:
        user_memory[user_id] = []

    user_memory[user_id].append({"role": "user", "content": en_text})

    # limit memory
    user_memory[user_id] = user_memory[user_id][-6:]

    # ask AI
    try:
        reply_en = ask_ai(user_memory[user_id])
    except Exception as e:
        await message.reply_text("Errorတက်နေပါတယ်ဗျ")
        return

    # save reply to memory
    user_memory[user_id].append({"role": "assistant", "content": reply_en})

    # translate back to Burmese
    reply_mm = to_burmese(reply_en)

    await message.reply_text(reply_mm)

# ---------------- RUN ----------------
print("🤖 AI Bot Running...")
app.run()
