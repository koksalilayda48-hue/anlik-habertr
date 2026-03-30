# bot.py
import feedparser
import time
import random
import json
import os
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# ----------------- ENVIRONMENT VARIABLES -----------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

# RSS haber kaynakları
RSS_URLS = [
    "https://www.trtspor.com.tr/rss.xml",
    "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr"
]

# Görsel yoksa kullanılacak fallback görseller
FALLBACK_IMAGES = [
    "https://via.placeholder.com/600x400?text=SON+DAKIKA",
    "https://via.placeholder.com/600x400?text=SPOR+HABER",
    "https://via.placeholder.com/600x400?text=GUNDEME+BOMBA"
]

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
                    bot.send_photo(chat_id=CHAT_ID, photo=image, caption=mesaj)
                    sent_news.add(title)
                except Exception as e:
                    print("Hata gönderimde:", e)

    # Gönderilenleri kaydet
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
    time.sleep(60)  # 1 dakika bekle
