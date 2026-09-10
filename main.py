import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ==========================================
# ضع المفاتيح الخاصة بك هنا مباشرة بين التنصيص
# ==========================================
TELEGRAM_BOT_TOKEN = "8814545062:AAFsCB6AcG8QFXDeSrXjNgqUCRIBq9GCx2A"
GEMINI_API_KEY = "AQ.Ab8RN6KGm0YPnwiN9KThdpwuAfAE_2ESJT_EK__c2dBYzOvqFw"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

SYSTEM_PROMPT = """
أنت خبير متقدم لإنشاء المحتوى بالذكاء الاصطناعي.
عند استقبال أي موضوع، قدم الإجابة بالترتيب التالي:
1. **السيناريو والنص (Text Generation):** الحوار أو النص كاملاً.
2. **أوامر توليد الصور (Prompts):** باللغة الإنجليزية لأدوات Midjourney / DALL-E.
3. **التعليق الصوتي (Text-to-Speech):** النص مخصص لأدوات ElevenLabs.
4. **توجيهات الفيديو:** حركة الكاميرا لأدوات Runway / InVideo.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً بك! أرسل لي أي فكرة وسأخرج لك خطة المحتوى والـ Prompts كاملة.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text
    status_msg = await update.message.reply_text("⏳ جاري تحضير المحتوى والسيناريو...")

    # رابط API الرسمي المستقر لـ Gemini
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY.strip()}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": f"{SYSTEM_PROMPT}\n\nطلب المستخدم: {user_prompt}"}]
        }]
    }

    try:
        res = requests.post(url, json=payload, headers=headers)
        res_json = res.json()

        if "candidates" in res_json and len(res_json["candidates"]) > 0:
            reply_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
        elif "error" in res_json:
            error_details = res_json['error'].get('message', 'مفتاح غير صالح')
            reply_text = f"❌ خطأ من Google: {error_details}"
        else:
            reply_text = "❌ لم يتم استلام استجابة صحيحة من الذكاء الاصطناعي."

        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=status_msg.message_id)
        await update.message.reply_text(reply_text)

    except Exception as e:
        logging.error(f"Error: {e}")
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=status_msg.message_id,
            text=f"❌ حدث خطأ أثناء الاتصال بالخادم: {e}"
        )

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN.strip()).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ البوت يعمل بنجاح...")
    app.run_polling()

if __name__ == '__main__':
    main()
