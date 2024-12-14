import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

# Load environment variables
HUGGING_FACE_API_KEY = os.getenv("HUGGING_FACE_API_KEY")
HUGGING_FACE_CHATBOT_MODEL = os.getenv("HUGGING_FACE_CHATBOT_MODEL")
HUGGING_FACE_MUSIC_MODEL = os.getenv("HUGGING_FACE_MUSIC_MODEL")
HUGGING_FACE_VIDEO_MODEL = os.getenv("HUGGING_FACE_VIDEO_MODEL")

# Start Command
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Chatbot", callback_data='chatbot')],
        [InlineKeyboardButton("Generate Image", callback_data='generate_image')],
        [InlineKeyboardButton("Generate Music", callback_data='generate_music')],
        [InlineKeyboardButton("Generate Video", callback_data='generate_video')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Welcome to RON AI Bot! Choose a feature:", reply_markup=reply_markup)

# Chatbot Feature (using Hugging Face API)
def chatbot(update: Update, context: CallbackContext):
    user_input = ' '.join(context.args)
    if not user_input:
        update.message.reply_text("Please type a message after /chatbot to start the conversation.")
        return

    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}
    payload = {"inputs": user_input}
    url = f"https://api-inference.huggingface.co/models/{HUGGING_FACE_CHATBOT_MODEL}"
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        chatbot_response = response.json().get("generated_text", "I'm not sure how to respond to that.")
        update.message.reply_text(chatbot_response)
    else:
        update.message.reply_text("Chatbot is currently unavailable. Try again later.")

# Music Generation (using Hugging Face MusicGen)
def generate_music(update: Update, context: CallbackContext):
    prompt = ' '.join(context.args)
    if not prompt:
        update.message.reply_text("Please provide a music description after /generate_music.")
        return

    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}
    payload = {"inputs": prompt}
    url = f"https://api-inference.huggingface.co/models/{HUGGING_FACE_MUSIC_MODEL}"
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        music_url = response.json().get("generated_audio", [])[0]
        update.message.reply_audio(audio=music_url)
    else:
        update.message.reply_text("Music generation is currently unavailable.")

# Video Generation (using Hugging Face Video Model)
def generate_video(update: Update, context: CallbackContext):
    prompt = ' '.join(context.args)
    if not prompt:
        update.message.reply_text("Please provide a video description after /generate_video.")
        return

    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}
    payload = {"inputs": prompt}
    url = f"https://api-inference.huggingface.co/models/{HUGGING_FACE_VIDEO_MODEL}"
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        video_url = response.json().get("generated_video", [])[0]
        update.message.reply_video(video=video_url)
    else:
        update.message.reply_text("Video generation is currently unavailable.")

# Main Function
def main():
    updater = Updater(os.getenv("TELEGRAM_BOT_TOKEN"))
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("chatbot", chatbot))
    dispatcher.add_handler(CommandHandler("generate_music", generate_music))
    dispatcher.add_handler(CommandHandler("generate_video", generate_video))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
