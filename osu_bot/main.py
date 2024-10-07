import os
import threading
import logging
from osu_bot.osu_bot import OsuBot

def console_input(bot):
    while True:
        message = input()
        if message.lower() == "exit":
            os._exit(0)
        else:
            bot.handle_message(message, None, "Console")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    bot = OsuBot()
    
    input_thread = threading.Thread(target=console_input, args=(bot,))
    input_thread.daemon = True
    input_thread.start()

    try:
        bot.start()
    except KeyboardInterrupt:
        logging.info("Бот остановлен.")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")