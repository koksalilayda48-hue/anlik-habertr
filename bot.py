import feedparser
import random
import json
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ENV
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

RSS_URLS = [
    "https://www.trtspor.com.tr/rss.xml",
    "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr"
]

FALLBACK_IMAGES = [
    "https://via.placeholder.com/600x400?text=SON+DAKIKA",
    "https://via.placeholder.com/600x400?text=SPOR+HABER",
    "https://via.placeholder.com/600x400?text=GUNDEME+BOMBA"
]

sent_news_file = "sent_news.json"
haber_active = True

# Önceki haberler
try:
    with open(sent_news_file, "r", encoding="utf-8") as f:
        sent_news = set(json.load(f))
except:
    sent_news = set()

# ---------------- HABER ----------------
async def send_news(app):
    global sent_news

    try:
        for rss_url in RSS_URLS:
            feed = feedparser.parse(rss_url)

            for entry in feed.entries[:5]:
                title = entry.title

                if title not in sent_news:
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
"""

                    await app.bot.send_photo(
                        chat_id=CHAT_ID,
                        photo=image,
                        caption=mesaj
                    )

                    sent_news.add(title)

        with open(sent_news_file, "w", encoding="utf-8") as f:
            json.dump(list(sent_news), f, ensure_ascii=False)

    except Exception as e:
        print("HATA AMA BOT DEVAM EDİYOR:", e)

# ---------------- LOOP ----------------
async def news_loop(app):
    while True:
        if haber_active:
            await send_news(app)
        await asyncio.sleep(60)

# ---------------- ADMIN ----------------
async def admin_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    mesaj = " ".join(context.args)
    if mesaj:
        await context.bot.send_message(chat_id=CHAT_ID, text=mesaj)

async def startnews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global haber_active
    if update.effective_user.id == ADMIN_ID:
        haber_active = True
        await update.message.reply_text("Açıldı")

async def stopnews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global haber_active
    if update.effective_user.id == ADMIN_ID:
        haber_active = False
        await update.message.reply_text("Kapandı")

# ---------------- MAIN ----------------
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("send", admin_send))
    app.add_handler(CommandHandler("startnews", startnews))
    app.add_handler(CommandHandler("stopnews", stopnews))

    print("🔥 Bot çalışıyor")

    asyncio.create_task(news_loop(app))

    await app.run_polling()

# ---------------- RUN ----------------
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
