#!/usr/bin/python3
from flask import g
from sys import platform
from config import BOT_TOKEN, TELEGRAM_PATH, CONFIG_PATH, PORT
from threading import Thread
import gorbin_tools2
import file_tools
import os
import json
import telebot
import telegram_bot

def run(PORT):
    """Runs the flask server according to the platform"""
    if platform != "darwin" and platform != "win32":
        app.run(host="0.0.0.0")
    else:
        app.run(port=PORT)

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
        file (False by default) -- if such file has config structure

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
    if BOT_TOKEN:
        # if you have online app, rewrite bot as webhook instead
        tele_bot = Thread(target=telegram_bot.run, daemon=True)
        tele_bot.start()
        run(PORT)
        tele_bot.join()
    else:
        run(PORT)
    