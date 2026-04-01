import feedparser
import random
import json
import os
import time
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

RSS_URLS = [
    "https://www.trtspor.com.tr/rss.xml",
    "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr"
]

FALLBACK_IMAGES = [
    "https://via.placeholder.com/600x400?text=SON+DAKIKA",
    "https://via.placeholder.com/600x400?text=SPOR+HABER"
]

sent_news_file = "sent_news.json"
haber_active = True

bot = Bot(token=BOT_TOKEN)
updater = Updater(token=BOT_TOKEN, use_context=True)
dp = updater.dispatcher

try:
    with open(sent_news_file, "r") as f:
        sent_news = set(json.load(f))
except:
    sent_news = set()

def send_news():
    global sent_news
    try:
        for rss_url in RSS_URLS:
            feed = feedparser.parse(rss_url)

            for entry in feed.entries[:5]:
                title = entry.title

                if title not in sent_news:
                    image = random.choice(FALLBACK_IMAGES)

                    msg = f"🚨 SON DAKİKA\n\n{title}"

                    bot.send_photo(chat_id=CHAT_ID, photo=image, caption=msg)
                    sent_news.add(title)

        with open(sent_news_file, "w") as f:
            json.dump(list(sent_news), f)

    except Exception as e:
        print("HATA:", e)

def loop():
    while True:
        if haber_active:
            send_news()
        time.sleep(60)

def admin_send(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return
    text = " ".join(context.args)
    if text:
        bot.send_message(chat_id=CHAT_ID, text=text)

def startnews(update: Update, context: CallbackContext):
    global haber_active
    if update.effective_user.id == ADMIN_ID:
        haber_active = True
        update.message.reply_text("Açıldı")

def stopnews(update: Update, context: CallbackContext):
    global haber_active
    if update.effective_user.id == ADMIN_ID:
        haber_active = False
        update.message.reply_text("Kapandı")

dp.add_handler(CommandHandler("send", admin_send))
dp.add_handler(CommandHandler("startnews", startnews))
dp.add_handler(CommandHandler("stopnews", stopnews))

updater.start_polling()

print("🔥 Bot çalışıyor")

loop()
