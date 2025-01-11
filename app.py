from flask import Flask, request
import telebot
import os

TOKEN = "7648462649:AAHsPnWL7IlsGgtkTNxdHBm3xCmDbFbfjLU"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running"

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Thiết lập Webhook (nếu cần)
def set_webhook():
    url = "https://your-vercel-project-name.vercel.app/" + TOKEN  # Cập nhật tên dự án sau khi deploy
    bot.remove_webhook()
    bot.set_webhook(url=url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
    
