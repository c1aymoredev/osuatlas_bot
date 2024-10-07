import irc.bot
import logging
from config import IRC_SERVER, IRC_PORT, IRC_NICKNAME, IRC_PASSWORD

class IRCClient(irc.bot.SingleServerIRCBot):
    def __init__(self, bot):
        super().__init__(
            [(IRC_SERVER, IRC_PORT, IRC_PASSWORD)],
            IRC_NICKNAME,
            IRC_NICKNAME
        )
        self.bot = bot
        
    def start(self):
        self._connect()
        super().start()

    def on_welcome(self, connection, event):
        logging.info(f"Бот {connection.get_nickname()} подключился к IRC серверу.")

    def on_pubmsg(self, connection, event):
        self.bot.handle_message(event.arguments[0], connection, event.source.nick, is_private=False)

    def on_privmsg(self, connection, event):
        self.bot.handle_message(event.arguments[0], connection, event.source.nick, is_private=True)

    def on_action(self, connection, event):
        self.bot.handle_message(event.arguments[0], connection, event.source.nick, is_private=False)

    def send_message(self, connection, target: str, message: str, is_private: bool):
        if connection:
            if is_private:
                connection.privmsg(target, message)
            else:
                connection.privmsg(self.channel, message)
        else:
            print(f"Отправлено сообщение для {target}: {message}")