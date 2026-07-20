import os
import logging
from pymongo import MongoClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# --- KONFIGURASI ---
MONGO_URI = "mongodb+srv://mktsosmed55_db_user:ACILV0ZqBfqKANbU@mamabasah.amgjqtl.mongodb.net/?appName=MAMABASAH"
TOKEN = "8223621284:AAEmWfgckgpHmebwaLNG5OZGKmEwOhdUMoc"
ADMIN_ID = 8765325815

# --- SERVER PENGAMAN (Agar Render tidak error "No open ports") ---
app_web = Flask(__name__)
@app_web.route('/')
def home():
    return "Bot is active"

def run_web():
    app_web.run(host='0.0.0.0', port=10000)

Thread(target=run_web).start()

# --- LOGGING ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- KONEKSI DATABASE ---
client = MongoClient(MONGO_URI)
db = client['bot_database']
video_coll = db['videos']

# --- FUNGSI ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args and args[0].startswith("vid"):
        video_data = video_coll.find_one({"vid_id": args[0]})
        if video_data:
            context.user_data['target_vid'] = video_data['file_id']
            
    text = "✨ Selamat Datang! Klik tombol di bawah untuk verifikasi akses konten."
    keyboard = [
        [InlineKeyboardButton("🔗 JOIN SUSU NASIONAL REBORN", url="https://t.me/susukentaltobrud")],
        [InlineKeyboardButton("🔗 JOIN DINASTI 138 X MAMA BASAH", url="https://t.me/DINASTI138XMAMABASAH")],
        [InlineKeyboardButton("🔗 JOIN SUSU BERUANG", url="https://t.me/BERUANGNYEPONG")],
        [InlineKeyboardButton("✅ VERIFIKASI SEKARANG", callback_data="check_verif")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def check_verif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    file_id = context.user_data.get('target_vid')
    
    if file_id:
        await query.message.reply_video(video=file_id)
        await query.answer("✅ Berhasil!", show_alert=True)
    else:
        await query.answer("❌ Link tidak valid atau sudah kadaluarsa.", show_alert=True)

async def handle_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    file_id = update.message.video.file_id
    count = video_coll.count_documents({}) + 1
    new_id = f"vid{count}"
    
    video_coll.insert_one({"vid_id": new_id, "file_id": file_id})
    await update.message.reply_text(f"✅ Tersimpan di Cloud!\nLink: https://t.me/KoleksiVideoo_bot?start={new_id}")

if __name__ == '__main__':
    print("Mencoba menjalankan bot...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_verif, pattern="check_verif"))
    app.add_handler(MessageHandler(filters.VIDEO, handle_upload))
    
    print("Bot sudah jalan!")
    app.run_polling()
