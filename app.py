from flask import Flask, request
import telebot
import os
import secrets
from telebot.types import InputMediaPhoto, InputMediaVideo

# Thay YOUR_BOT_TOKEN bằng token của bot của bạn
TOKEN = "7648462649:AAHsPnWL7IlsGgtkTNxdHBm3xCmDbFbfjLU"
GROUP_CHAT_ID = -1002389087763  # ID nhóm Telegram để lưu file ID
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# Lưu trữ tạm thời file_id theo phiên gửi
user_sessions = {}
link_mapping = {}

# Route chính để kiểm tra trạng thái bot
@app.route('/')
def index():
    return "Bot is running"

# Webhook route
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    print("Webhook data received:", json_str)  # Ghi log để kiểm tra webhook
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Thiết lập Webhook
def set_webhook():
    url = "https://vui-vui.vercel.app/" + TOKEN  # Thay bằng URL của bạn trên Vercel
    bot.remove_webhook()
    bot.set_webhook(url=url)

# Xử lý lệnh /start
@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.reply_to(message, "Bot is running and ready to interact!")

# Xử lý các loại tin nhắn (hình ảnh, video)
@bot.message_handler(content_types=["photo", "video"])
def handle_media(message):
    user_id = message.from_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = []
    
    if message.content_type == "photo":
        file_id = message.photo[-1].file_id
        user_sessions[user_id].append((file_id, "Ảnh"))
    elif message.content_type == "video":
        file_id = message.video.file_id
        user_sessions[user_id].append((file_id, "Video"))
    bot.reply_to(message, "Received your media!")

# Xử lý lệnh /okay
@bot.message_handler(commands=["okay"])
def handle_ok(message):
    user_id = message.from_user.id
    if user_id not in user_sessions or not user_sessions[user_id]:
        bot.reply_to(message, "Đéo có file!")
        return

    # Tạo danh sách file ID
    media_list = user_sessions[user_id]
    message_text = "Đã lưu các file:\n"
    for idx, (file_id, file_type) in enumerate(media_list, start=1):
        message_text += f"File {idx} ({file_type})\n"

    # Chuyển tiếp từng file vào nhóm
    for file_id, file_type in media_list:
        if file_type == "Ảnh":
            bot.send_photo(GROUP_CHAT_ID, file_id)
        elif file_type == "Video":
            bot.send_video(GROUP_CHAT_ID, file_id)

    # Gửi thông báo vào nhóm
    sent_message = bot.send_message(GROUP_CHAT_ID, message_text)

    # Tạo mã băm duy nhất dựa trên message_id
    random_token = secrets.token_hex(16)  # Sinh chuỗi ngẫu nhiên 32 ký tự
    link_mapping[random_token] = (sent_message.message_id, media_list)
    user_link = f"https://t.me/{bot.get_me().username}?start={random_token}"

    # Gửi liên kết cho người dùng
    bot.reply_to(message, f"Đây là đường link của mày🫵:\n\n{user_link}")

    # Xóa phiên của người dùng
    user_sessions[user_id] = []

# Chạy Flask server
if __name__ == "__main__":
    set_webhook()  # Thiết lập Webhook
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))  # Chạy Flask server
