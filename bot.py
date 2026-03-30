import feedparser
import time
import random
import json
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from config import BOT_TOKEN, CHAT_ID, ADMIN_ID, RSS_URLS, FALLBACK_IMAGES

# ----------------- GLOBAL DURUMLAR -----------------
haber_active = True
sent_news_file = "sent_news.json"

bot = Bot(token=BOT_TOKEN)
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# ----------------- Önceden gönderilen haberleri yükle -----------------
try:
    with open(sent_news_file, "r", encoding="utf-8") as f:
        sent_news = set(json.load(f))
except:
    sent_news = set()

# ----------------- HABER GÖNDERME -----------------
def send_news():
    global sent_news
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

━━━━━━━━━━━━━━━
🔥 Takipte kal
"""
                try:
                    bot.send_photo(chat_id=CHAT_ID, photo=image, caption=mesaj)
                    sent_news.add(title)
                except Exception as e:
                    print("Hata gönderimde:", e)

    with open(sent_news_file, "w", encoding="utf-8") as f:
        json.dump(list(sent_news), f, ensure_ascii=False)

# ----------------- ADMIN KOMUTLARI -----------------
def admin_send(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("Yetkin yok!")
        return
    mesaj = " ".join(context.args)
    if mesaj:
        bot.send_message(chat_id=CHAT_ID, text=f"💬 ÖZEL MESAJ\n\n{mesaj}")

def startnews(update: Update, context: CallbackContext):
    global haber_active
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("Yetkin yok!")
        return
    haber_active = True
    update.message.reply_text("📰 Haber akışı başlatıldı.")

def stopnews(update: Update, context: CallbackContext):
    global haber_active
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("Yetkin yok!")
        return
    haber_active = False
    update.message.reply_text("🛑 Haber akışı durduruldu.")

# ----------------- KOMUTLARI EKLE -----------------
dispatcher.add_handler(CommandHandler("send", admin_send))
dispatcher.add_handler(CommandHandler("startnews", startnews))
dispatcher.add_handler(CommandHandler("stopnews", stopnews))

# ----------------- BOT POLLING -----------------
updater.start_polling()
print("💡 Bot başlatıldı. Haber akışı aktif.")

# ----------------- ANA DÖNGÜ -----------------
while True:
    if haber_active:
        send_news()
    time.sleep(60)
