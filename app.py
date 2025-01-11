from flask import Flask, request
import telebot
import os
import secrets

# Thay YOUR_BOT_TOKEN bằng token của bot của bạn
TOKEN = "7648462649:AAHsPnWL7IlsGgtkTNxdHBm3xCmDbFbfjLU"
GROUP_CHAT_ID = -1002389087763  # ID nhóm Telegram để lưu file ID
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

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
    bot.reply_to(message, "Received your media!")

# Chạy Flask server
if __name__ == "__main__":
    set_webhook()  # Thiết lập Webhook
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))  # Chạy Flask server
