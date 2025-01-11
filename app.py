import telebot

TOKEN = "7648462649:AAHsPnWL7IlsGgtkTNxdHBm3xCmDbFbfjLU"
bot = telebot.TeleBot(TOKEN)

def set_webhook():
    url = "https://your-vercel-project-name.vercel.app/" + TOKEN  # Thay bằng URL chính xác từ Vercel
    bot.remove_webhook()  # Xoá webhook cũ (nếu có)
    bot.set_webhook(url=url)  # Thiết lập webhook mới
    print(f"Webhook set to: {url}")

if __name__ == "__main__":
    set_webhook()
    
