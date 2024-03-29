import socket
import time
import sys
from bot import MyBot

server = "irc.libera.chat"
port = 6667
channel = "#CSC482"
nickname = "silly-bot"


class IRC:

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(15)

    def connect(self):
        self.socket.connect((server, port))
        self.send(f"USER {nickname} 0 * :{nickname}\r\n")
        self.send(f"NICK {nickname}\r\n")
        self.send(f"JOIN {channel}\r\n")

    def send(self, msg):
        try:
            self.socket.send(msg.encode("utf-8"))
        except Exception as e:
            print("caught ", e)

    def receive(self):
        time.sleep(1)
        return self.socket.recv(2048).decode("utf-8")

    def reset_timer(self, time):
        self.socket.settimeout(time)


if __name__ == "__main__":

    irc = IRC()
    irc.connect()
    bot = MyBot(irc)

    try:
        bot.run()
    except KeyboardInterrupt:
        irc.send("QUIT :I'm outta here!\r\n")
        time.sleep(2)
        sys.exit(0)
