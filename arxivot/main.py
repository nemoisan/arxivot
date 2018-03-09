# -*- coding: utf-8 -*-
import configparser
import sys
import slackbot.bot
import slackbot.settings


def main():
    bot = slackbot.bot.Bot()
    bot.run()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f'usage: {sys.argv[0]} config_file_path', file=sys.stderr)
        exit(1)

    settings = configparser.ConfigParser()
    try:
        settings.read(sys.argv[1])
    except FileNotFoundError:
        print(f'config file read error.', file=sys.stderr)
        exit(1)
    slackbot.settings.API_TOKEN = settings.get('channel', 'API_TOKEN')
    slackbot.settings.DEFAULT_REPLY = settings.get('bot', 'DEFAULT_REPLY')
    slackbot.settings.PLUGINS = [settings.get('bot', 'PLUGIN_DIR')]
    print(slackbot.settings.PLUGINS)
    slackbot.settings.DEBUG = True
    main()
