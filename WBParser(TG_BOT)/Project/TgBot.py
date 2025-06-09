import telebot
from telebot import TeleBot
import logging
import os
from Project.WBParser import WBParser
from config import TOKEN, DEBUG
from dotenv import load_dotenv
import traceback

load_dotenv()

debug=DEBUG
WBP = WBParser(show_window=debug, debug=debug)

if debug:
    telebot.logger.setLevel(logging.DEBUG)
else:
    telebot.logger.setLevel(logging.WARNING)
    
logging.basicConfig(
    level=logging.WARNING if not DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()] 
)

bot = TeleBot(TOKEN)
logger = logging.getLogger(__name__)
logger.info("TelegramBot - Starting")



def anti_fail(func):
    def wrapper(*args, **kwargs):
        try:
            logger.debug(f"Триггер {func.__name__}")
            func(*args, **kwargs)
        except Exception:
            logger.warning(
                traceback.format_exc()
                )
    return wrapper


@bot.message_handler(commands=['start'])
@anti_fail
def start(message):
    bot.send_message(message.chat.id, "Отправьте ссылку на товар.")
    


@bot.message_handler()
@anti_fail
def find_positions(message):
    if "http" in message.text:
        try:
            if WBP.is_busy():
                bot.send_message(message.chat.id, "Бот пока занят")
            else:
                bot.send_message(message.chat.id, "Проверяю ключевые слова.")
                results = WBP.run(message.text)
                if results:
                    answer = []
                    for key_data in results:
                        answer.append("{:20} \t\t {:5}".format(key_data[0], key_data[1] if key_data[1] is not None else 'Нет' ))
                    bot.send_message(message.chat.id, "\n".join(answer))
                    
        except Exception as e:
            logger.debug(traceback.format_exc())
            bot.send_message(message.chat.id, "При обработке запроса произошла ошибка.")
    else:
        bot.send_message(message.chat.id, "Это не ссылка.")
    