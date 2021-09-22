import bs4, requests, os, logging, re
import threading
import time

from telegram.ext import (
    Updater,
    CommandHandler,
)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


### GLOBAL VARS

# List of recording of seat amounts when necessary
ls = []

# Boolean to track whether the bot is recording
recording = False


### COMMAND HANDLERS

def get_seats_amount():
    
    # Go to the webpage 
    req = requests.get('http://wwwapps.ehabitat.net/rvrcdh/')
    req.raise_for_status()

    # Get capacity via bs4
    soup = bs4.BeautifulSoup(req.text, 'html.parser')
    pic = soup.select('body > div > div:nth-child(1) > div > div > h1')
    text_to_regex = pic[0].text.strip()

    # Use regex to obtain the number of seats
    pic_link_regex = re.compile(r'(\d)+ / (\d)+')
    mo = pic_link_regex.search(text_to_regex)
    return mo.group()


# Check the amount of seats via web-scraping
def check_seats(update, context):
    capacity = get_seats_amount()


# Simple introduction by the bot to the user
def start(update, context):
    name = update.message.from_user.first_name;
    context.bot.send_message(chat_id=update.effective_chat.id, text = """
Hello {}!
/checkseats
""".format(name))


# Start recording
def log(update, context):
    global recording
    recording = True
    global ls
    ls = []


# Command to stop the recording
def stop_log(update, context):
    global recording
    recording = False
    context.bot.send_message(chat_id=update.effective_chat.id, text = ls)


# Thread to print the seats amount at a fixed time and save the result if required
class MyThread (threading.Thread):
    def __init__(self, interval):
        threading.Thread.__init__(self)
        self.interval = interval
    def run(self):
        while True:
            count = get_seats_amount()
            print(count + " at " + time.ctime(time.time()))
            if recording:
                ls.append(count)
                print("appended")
            time.sleep(self.interval)


# MAIN

def main():
    # Constants
    PORT = int(os.environ.get('PORT', 5000))
    INTERVAL_TIME = 60                          # 1 minute per check

    thread2 = MyThread(INTERVAL_TIME)           # Create thread 
    thread2.start()                             # Start thread
    
    # Add bot token to updater, initialise dispatcher
    updater = Updater(token = 'telegram_bot_token_here', use_context = True)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('checkseats', check_seats))
    dispatcher.add_handler(CommandHandler('log', log))
    dispatcher.add_handler(CommandHandler('stoplog', stop_log))

    # Start and set webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path='telegram_bot_token_here')

    updater.bot.setWebhook('https://your-herokuapp-007.herokuapp.com/' + 'telegram_bot_token_here')

    # Set updater to idle
    updater.idle()


if __name__ == '__main__':
    main()


    



