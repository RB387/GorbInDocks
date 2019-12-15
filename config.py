from os import path, getcwd
SECRET_KEY = '1337' # key to secret sessions. keep it a complete secret!
UPLOAD_FOLDER = path.join(getcwd(), 'data') # ./data as default. Folder with loaded files. You can enter your path
ZIP_FOLDER = path.join(getcwd(), 'temp_data') # ./temp_data as default. Folder with zipped files. You can enter your path
LOG_FOLDER = path.join(getcwd(), 'logs') # ./logs as default. Folder with logs. You can enter your path
DB_NAME = 'gorbin' # name of Mongo database
USERS_COL_NAME = 'users' # name of the users collection 
FILES_COL_NAME = 'files' # name of the files collection
LINKS_COL_NAME = 'links' # name of the links collection
MONGO_ADDRESS = 'mongodb://localhost:27017/' # MongoDB address
