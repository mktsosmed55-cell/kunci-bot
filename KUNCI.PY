import os
import logging
from pymongo import MongoClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- KONFIGURASI ---
MONGO_URI = "mongodb+srv://mktsosmed55_db_user:ACILV0ZqBfqKANbU@mamabasah.amgjqtl.mongodb.net/?appName=MAMABASAH"
TOKEN = "8223621284:AAEmWfgckgpHmebwaLNG5OZGKmEwOhdUMoc"
ADMIN_ID = 8765325815

# --- LOGGING ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- KONEKSI DATABASE ---
client = MongoClient(MONGO_URI)
db = client['bot_database']
video_coll = db['videos']
session_coll = db['user_sessions']  # Koleksi baru untuk menyimpan sesi permanen

# --- FUNGSI ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    user_id = update.effective_user.id
    
    if args and args[0].startswith("vid"):
        video_data = video_coll.find_one({"vid_id": args[0]})
        if video_data:
            # Simpan secara permanen ke MongoDB berdasarkan User ID
            session_coll.update_one(
                {"user_id": user_id},
                {"$set": {"target_vid": video_data['file_id']}},
                upsert=True
            )
            
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
    user_id = query.from_user.id
    
    # Ambil data video dari MongoDB berdasarkan User ID
    user_session = session_coll.find_one({"user_id": user_id})
    
    if user_session and "target_vid" in user_session:
        file_id = user_session["target_vid"]
        await query.message.reply_video(video=file_id)
        await query.answer("✅ Berhasil!", show_alert=True)
    else:
        await query.answer("❌ Silakan klik link /start dari video terlebih dahulu.", show_alert=True)

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
