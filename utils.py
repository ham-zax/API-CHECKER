# api_checker/utils.py
import requests
from config import TELEGRAM_TOKEN, CHAT_ID
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram message: {e}")

def process_response(data, seen_hostnodes, notify=False):
    new_3995_nodes = []
    if data.get("success"):
        hostnodes = data.get("hostnodes", {})
        for key, hostnode in hostnodes.items():
            cpu_info = hostnode['specs']['cpu']
            if "3995" in cpu_info['type']:
                if key not in seen_hostnodes:
                    seen_hostnodes.add(key)
                    new_3995_nodes.append({**hostnode, 'id': key})
                    message = (
                        f"Hostnode ID: {key}\n"
                        f"Location: {hostnode['location']['city']}, {hostnode['location']['country']}\n"
                        f"CPU: {cpu_info['type']} - Amount: {cpu_info['amount']} - Price: {cpu_info['price']}\n"
                        f"Status: {'Online' if hostnode['status']['online'] else 'Offline'}\n"
                        f"{'='*40}"
                    )
                    if len(message) > 4096:
                        message = message[:4093] + "..."
                    print(message)
                    if notify:
                        send_telegram_message(message)
    else:
        print("API request was not successful")
    return new_3995_nodes

def notify_new_3995(new_3995_nodes):
    print(f"Found {len(new_3995_nodes)} new hostnodes with 3995 CPU:")
    for node in new_3995_nodes:
        node_id = node.get('id', 'Unknown ID')
        print(f"Hostnode ID: {node_id}")

def handle_error(error):
    print(f"An error occurred: {error}")

def list_all_3995_nodes(seen_hostnodes):
    message = "Current hostnodes with 3995 CPU:\n"
    for node_id in seen_hostnodes:
        message += f"Hostnode ID: {node_id}\n"
    if len(message) > 4096:
        message = message[:4093] + "..."
    send_telegram_message(message)

def handle_all_command(update: Update, context: CallbackContext):
    list_all_3995_nodes(context.bot_data['seen_hostnodes'])
    update.message.reply_text("Listing all current 3995 CPUs.")

def start_bot():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.bot_data['seen_hostnodes'] = set()

    dp.add_handler(CommandHandler('all', handle_all_command))

    updater.start_polling()
    updater.idle()
