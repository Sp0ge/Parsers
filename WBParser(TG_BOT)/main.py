import logging
from Project.TgBot import bot, WBP

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        logger.warning("\n\n Application Starting \n\n")
        bot.polling(non_stop=True)
    except KeyboardInterrupt:
        logger.warning("\n\n Exit \n\n")
        WBP.stop()
        quit()
        