import telebot
import hashlib
import secrets
from telebot.types import InputMediaPhoto, InputMediaVideo
from flask import Flask, request
import os

# Thay YOUR_BOT_TOKEN bằng token của bot
TOKEN = "7648462649:AAHsPnWL7IlsGgtkTNxdHBm3xCmDbFbfjLU"
GROUP_CHAT_ID = -1002389087763  # ID nhóm Telegram để lưu file ID
bot = telebot.TeleBot(TOKEN)

# Lưu trữ tạm thời file_id theo phiên gửi
user_sessions = {}
link_mapping = {}  # Lưu ánh xạ từ mã băm -> (message_id, danh sách file)

app = Flask(__name__)

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route('/')
def index():
    return "Bot is running"

# Thiết lập Webhook
def set_webhook():
    # Cập nhật URL của webhook
    url = "https://your-vercel-url.vercel.app/" + TOKEN  # Thay bằng URL ứng dụng Vercel của bạn
    bot.remove_webhook()
    bot.set_webhook(url=url)

# Các hàm xử lý tin nhắn
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

@bot.message_handler(commands=["start"])
def handle_start(message):
    # Thực hiện lệnh từ người dùng
    if len(message.text.split()) > 1:
        token = message.text.split()[1]  # Lấy token từ liên kết
        if token in link_mapping:
            message_id, media_list = link_mapping[token]
            try:
                # Gửi từng file lại cho người dùng
                for file_id, file_type in media_list:
                    if file_type == "Ảnh":
                        bot.send_photo(message.chat.id, file_id)
                    elif file_type == "Video":
                        bot.send_video(message.chat.id, file_id)
                bot.reply_to(message, "Đây là file của bạn!")
            except Exception as e:
                bot.reply_to(message, "Không tìm thấy dữ liệu liên kết. Vui lòng thử lại.")
        else:
            bot.reply_to(message, "Liên kết không hợp lệ hoặc đã hết hạn.")
    else:
        bot.reply_to(message, "👉Đây là bot lưu trữ hình ảnh, video thuộc về @sachkhongchuu \n🗣️Để sử dụng hãy ấn vào đường link mà bạn được cung cấp khi vượt link, có thắc mắc liên hệ ngay @nothinginthissss")

    # Gửi ảnh và tin nhắn chào mừng
    welcome_photo_id = 'AgACAgUAAxkBAAMHZ3-3v62odawYX8suFAJLbKcGOFgAAhLDMRuiu-FXnxWilZ4-6AcBAAMCAAN5AAM2BA'  # File ID của ảnh
    welcome_message = '🥳Chào mừng bạn đến với sách không chữ: https://t.me/addlist/thPNIyIPF8o0ZDBl\n\n👉Tham gia ngay: t.me/sachkhongchuu\n\n😛Mua bot, thuê bot hay có bất cứ vấn đề gì liên hệ @nothinginthissss '

    bot.send_photo(
        message.chat.id, 
        welcome_photo_id,
        caption="🥳 Chào mừng bạn đến với sách không chữ!",
        reply_markup=None,
        protect_content=True  # Ngăn không cho tin nhắn bị chuyển tiếp
    )
    # Gửi tin nhắn chào mừng
    bot.send_message(message.chat.id, welcome_message, protect_content=True)  # Ngăn không cho tin nhắn bị chuyển tiếp

if __name__ == "__main__":
    set_webhook()  # Thiết lập Webhook
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))  # Chạy Flask server
