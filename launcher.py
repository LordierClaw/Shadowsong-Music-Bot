from Shadowsong.bot import ShadowsongBot
from keep_alive import keep_alive #to host on replit server

import configparser

def main():
    config = configparser.ConfigParser()
    config.read("config.ini")

    bot = ShadowsongBot()
    if config["HOST"]["HOST_ON_REPLIT"] == "1":
        keep_alive()
    bot.run()

if __name__ == "__main__":
    main()