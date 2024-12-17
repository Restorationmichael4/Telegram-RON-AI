import logging
import json
import random
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Use Render's disk storage path or default to the current directory
DISK_PATH = os.getenv("DISK_PATH", "./")
COURSES_FILE = os.path.join(DISK_PATH, "courses.json")
CHATS_FILE = os.path.join(DISK_PATH, "anonymous_chats.json")

# Load or initialize JSON data
def load_json(file_path, default_data):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_data

def save_json(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

# Load initial data
courses = load_json(COURSES_FILE, [])
anonymous_chats = load_json(CHATS_FILE, {})

# Start command
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_html(
        rf"Hi {user.mention_html()}! Welcome to the Anonymous Chat and Learning Bot. Use /help to see available commands."
    )

# Help command
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "/post [course_name] - Post a course\n"
        "/read - Read available courses\n"
        "/find - Find an anonymous chat partner\n"
        "/leave - Leave the anonymous chat\n"
        "/ask [question] - Ask a question"
    )

# Post a course
def post_course(update: Update, context: CallbackContext) -> None:
    course_name = ' '.join(context.args)
    if course_name:
        courses.append(course_name)
        save_json(COURSES_FILE, courses)  # Save courses to JSON
        update.message.reply_text(f"Course '{course_name}' has been posted!")
    else:
        update.message.reply_text("Please provide a course name.")

# Read available courses
def read_courses(update: Update, context: CallbackContext) -> None:
    if courses:
        update.message.reply_text("Available courses:\n" + "\n".join(courses))
    else:
        update.message.reply_text("No courses available.")

# Find an anonymous chat partner
def find_partner(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    if user_id not in anonymous_chats:
        eligible_users = [uid for uid in anonymous_chats if uid != user_id]
        if eligible_users:
            partner_id = random.choice(eligible_users)
            anonymous_chats[user_id] = partner_id
            anonymous_chats[partner_id] = user_id
            save_json(CHATS_FILE, anonymous_chats)  # Save chat state to JSON
            update.message.reply_text(f"You are now chatting with user {partner_id}.")
        else:
            update.message.reply_text("No partners available. Please wait for someone to join.")
    else:
        update.message.reply_text("You are already in a chat. Use /leave to exit.")

# Leave an anonymous chat
def leave_chat(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    if user_id in anonymous_chats:
        partner_id = anonymous_chats[user_id]
        del anonymous_chats[user_id]
        if partner_id in anonymous_chats and anonymous_chats[partner_id] == user_id:
            del anonymous_chats[partner_id]
        save_json(CHATS_FILE, anonymous_chats)  # Save chat state to JSON
        update.message.reply_text("You have left the chat.")
    else:
        update.message.reply_text("You are not in a chat.")

# Ask a question
def ask_question(update: Update, context: CallbackContext) -> None:
    question = ' '.join(context.args)
    if question:
        update.message.reply_text(f"You asked: {question}. Please wait for a response.")
    else:
        update.message.reply_text("Please provide a question.")

# Main function to run the bot
def main() -> None:
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
    updater = Updater(os.getenv("7975644638:AAFrZ1FxLMZlaGE98is3wzZqBWnp_9ErNnY"))
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("post", post_course))
    dispatcher.add_handler(CommandHandler("read", read_courses))
    dispatcher.add_handler(CommandHandler("find", find_partner))
    dispatcher.add_handler(CommandHandler("leave", leave_chat))
    dispatcher.add_handler(CommandHandler("ask", ask_question))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
