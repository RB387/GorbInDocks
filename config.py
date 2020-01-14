from os import path, getcwd
###############
DEBUG = False # 
PORT = 5000   #
###############
SECRET_KEY = 'secretkeydonthackplease' # key to secret sessions. keep it a complete secret!
UPLOAD_FOLDER = path.join(getcwd(), 'data') # ./data as default. Folder with loaded files. You can enter your path
ZIP_FOLDER = path.join(getcwd(), 'temp_data') # ./temp_data as default. Folder with zipped files. You can enter your path
LOG_FOLDER = path.join(getcwd(), 'logs') # ./logs as default. Folder with logs. You can enter your path
CONFIG_PATH = path.join(getcwd(), 'settings.json') # path to json config file
TELEGRAM_PATH = path.join(getcwd(), 'telegram_users.json') # path to telegram json database
DB_NAME = 'gorbin' # name of Mongo database
USERS_COL_NAME = 'users' # name of the users collection 
FILES_COL_NAME = 'files' # name of the files collection
MONGO_ADDRESS = 'mongodb://localhost:27017/' # MongoDB address
BOT_TOKEN = None #Telegram bot token
