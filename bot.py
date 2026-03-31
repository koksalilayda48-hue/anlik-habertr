import feedparser
import random
import json
import os
import asyncio
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ----------------- ENVIRONMENT VARIABLES -----------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

# RSS haber kaynakları
RSS_URLS = [
    "https://www.trtspor.com.tr/rss.xml",
    "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr"
]

# Görsel yoksa fallback
FALLBACK_IMAGES = [
    "https://via.placeholder.com/600x400?text=SON+DAKIKA",
    "https://via.placeholder.com/600x400?text=SPOR+HABER",
    "https://via.placeholder.com/600x400?text=GUNDEME+BOMBA"
]

sent_news_file = "sent_news.json"

# Önceden gönderilen haberleri yükle
try:
    with open(sent_news_file, "r", encoding="utf-8") as f:
        sent_news = set(json.load(f))
except:
    sent_news = set()

haber_active = True

# ----------------- HABER GÖNDERME -----------------
async def send_news(app):
    global sent_news
    for rss_url in RSS_URLS:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:5]:
            title = entry.title
            if title not in sent_news:
                # Görsel bul
                image = None
                if "media_content" in entry:
                    image = entry.media_content[0].get("url")
                elif "links" in entry:
                    for link in entry.links:
                        if link.type.startswith("image"):
                            image = link.href
                            break
                if not image:
                    image = random.choice(FALLBACK_IMAGES)

                mesaj = f"""🚨 SON DAKİKA

{title}

📌 Gelişme devam ediyor...

━━━━━━━━━━━━━━━
🔥 Takipte kal
"""
                try:
                    await app.bot.send_photo(chat_id=CHAT_ID, photo=image, caption=mesaj)
                    sent_news.add(title)
                except Exception as e:
                    print("Hata gönderimde:", e)

    with open(sent_news_file, "w", encoding="utf-8") as f:
        json.dump(list(sent_news), f, ensure_ascii=False)

# ----------------- ADMIN KOMUTLARI -----------------
async def admin_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Yetkin yok!")
        return
    mesaj = " ".join(context.args)
    if mesaj:
        await context.bot.send_message(chat_id=CHAT_ID, text=f"💬 ÖZEL MESAJ\n\n{mesaj}")

async def startnews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global haber_active
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Yetkin yok!")
        return
    haber_active = True
    await update.message.reply_text("📰 Haber akışı başlatıldı.")

async def stopnews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global haber_active
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Yetkin yok!")
        return
    haber_active = False
    await update.message.reply_text("🛑 Haber akışı durduruldu.")

# ----------------- BOT BAŞLAT -----------------
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Komutlar
    app.add_handler(CommandHandler("send", admin_send))
    app.add_handler(CommandHandler("startnews", startnews))
    app.add_handler(CommandHandler("stopnews", stopnews))

    # Haber akışı döngüsü
    async def news_loop():
        while True:
            if haber_active:
                await send_news(app)
            await asyncio.sleep(60)

    # Başlat
    asyncio.create_task(news_loop())
    print("💡 Bot başlatıldı. Haber akışı aktif.")
    await app.run_polling()

# ----------------- RUN -----------------
if __name__ == "__main__":
    asyncio.run(main())
