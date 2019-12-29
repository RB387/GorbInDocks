from flask import g
from sys import platform
from config import BOT_TOKEN, TELEGRAM_PATH, CONFIG_PATH, SETUP
from threading import Thread
import gorbin_tools2
import file_tools
import os
import json
import telebot
import telegram_bot

def dump(path, data):
    '''Function to dump json files

        arguments:
        path -- path to json file
        data -- data to dump

        returns nothing
    '''
    with open(path, 'w') as outfile:
        json.dump(data, outfile)


def open_config(path, config=False):
    '''Function to open json files

        arguments:
        path -- path to json file
        file (False by default) -- if such file have config structure

        returns json file data
    '''
    if os.path.exists(path):
        with open(path) as json_data_file:
            return json.load(json_data_file)
    else:
        if config:
            dump_data = {"max_file_size": 10485760, "max_files_count": 5, "tags": ['Hello']}
        else:
            dump_data = {}
        dump(path, dump_data)
        return dump_data

#Open configs       
settings = open_config(CONFIG_PATH, config=True)
user_data = open_config(TELEGRAM_PATH)
#Initialize libraries
gt = gorbin_tools2.mongo_tools(g)
ft = file_tools.file_tools(settings, gt)
bot = telebot.TeleBot(BOT_TOKEN)

if __name__ == '__main__':
    from application import app
    app.config.from_object('config')
    #if setup==true in config
    if SETUP:
        with app.app_context():
            #Configure database
            gt.remake_files('yes')
            gt.remake_users('yes')
            gt.remake_links('yes')
            #add default admin user
            gt.add_user(login = 'admin', pas = gorbin_tools2.hash('admin00'), email = 'xd@yolo.com', status='admin')

    print(app.debug)
    if BOT_TOKEN:
        tele_bot = Thread(target=telegram_bot.run, daemon=True)
        tele_bot.start()
    app.run()
    if BOT_TOKEN:
        tele_bot.join()
    