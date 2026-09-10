import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

SYSTEM_PROMPT = """
أنت خبير لإنشاء المحتوى بالذكاء الاصطناعي.
عند استقبال أي موضوع، قدم:
1. السيناريو والنص (Text Generation).
2. أوامر توليد الصور بالإنجليزية (Midjourney / DALL-E / Leonardo Prompts).
3. نص التعليق الصوتي وإرشادات الصوت (ElevenLabs / Murf).
4. تعليمات تحريك الفيديو (Runway / HeyGen / InVideo).
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً بك! أرسل لي أي فكرة وسأخرج لك خطة المحتوى والـ Prompts كاملة.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text
    status_msg = await update.message.reply_text("⏳ جاري تحضير المحتوى والسيناريو...")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": f"{SYSTEM_PROMPT}\n\nطلب المستخدم: {user_prompt}"}]
        }]
    }

    try:
        res = requests.post(url, json=payload, headers=headers)
        res_json = res.json()
        
        if "candidates" in res_json:
            reply_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            reply_text = "❌ حدث خطأ في الاستجابة، يرجى التأكد من مفتاح Gemini API Key."

        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=status_msg.message_id)
        await update.message.reply_text(reply_text)

    except Exception as e:
        logging.error(f"Error: {e}")
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=status_msg.message_id,
            text="❌ حدث خطأ أثناء الاتصال بالخادم."
        )

def main():
    if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
        print("CRITICAL ERROR: Tokens missing in Environment Variables!")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot is running successfully...")
    app.run_polling()

if __name__ == '__main__':
    main()
