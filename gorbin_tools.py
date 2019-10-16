###########################################################
#                                                         #
#              Made by Vladislav Faralaks                #
#       especially for the project GorbInDocks            #
#     GitHub: https://github.com/Faralaks/GorbInDocks     #
#                                                         #
###########################################################

from bson.objectid import ObjectId as obj_id
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient
from Crypto.Cipher import AES
from hashlib import sha256
import datetime as dt
import base64


# Lambdas for working with request.form dict
form = lambda key: request.form[key] # takes key, returns value
form_get = lambda key, ret: request.form.get(key, ret) # takes key and ret, returns value if exists or returns ret


# Functions for working with time
def now_stamp():
    """returns the current datetime in timestamp format"""
    return int(dt.datetime.now().timestamp())

def from_stamp(stamp):
    """takes timestamp, returns datetime object"""
    return dt.datetime.fromtimestamp(stamp)

def stamp2str(stamp):
    """takes timestamp, returns datetime in string like '2019-10-14 18:24:14'"""
    return str(dt.datetime.fromtimestamp(stamp))

def str_now():
    """returns the current datetime in string like '2019-10-14 18:24:14'"""
    return str(dt.datetime.now())[:-7]

def now():
    """returns the current datetime as datetime object"""
    return dt.datetime.now()


# Useful visible print function
def vprint(*items):
    """takes >= 1 object, prints them line by line for easy view"""
    print('\n-----------------------\n')
    for i in items:
        print('\t', i)
    print('\n-----------------------\n')

# Functions of encryption, decryption (ECB AES) and hashing (sha256)
def encrypt(message, passphrase):
    """takes message and key, returns the result of the encryption in base64
    IMPORTANT: key must be a multiple of 16. 
    the message will be expanded to a multiple of 16 automatically
    with the addition of spaces to the left of the original message"""
    message = b' '* (16-(len(message) % 16)) + bytes(message, 'utf-8')
    aes = AES.new(passphrase, AES.MODE_ECB)
    return base64.b64encode(aes.encrypt(message))

def decrypt(encrypted, passphrase):
    """takes encrypted message in base64 and key, returns decrypted string without spaces on the left
    IMPORTANT: key must be a multiple of 16. 
    Finaly, the strip function is used to remove the spaces from the left of the message"""
    aes = AES.new(passphrase, AES.MODE_ECB)
    return aes.decrypt(base64.b64decode(encrypted)).lstrip().decode('utf-8')

def hash(message, salt=b'JT7BX67_rVrdEpLlzWbNRV'):
    """takes message and optional byte salt, returns sha256 of (message + salt) with a length of 64.
    the default salt has length 22"""
    return sha256(bytes(message, 'utf-8') + salt).hexdigest()


# MongoDB functions
def get_db(g, dbname, addres='mongodb://localhost:27017/'):
    """requires g object from Flask and the name of database, adds a database object (if no exists)
    as attribute to flask.g and returns a database object 
    optionally takes the mongodb address (localhost by default)"""
    db = getattr(g, 'db', None)
    if db is None:
        client = MongoClient(addres)
        db = g.db = client[dbname]
    return db

def get_users_col(g, dbname, users_col_name, addres='mongodb://localhost:27017/'):
    """requires g object from Flask, names of database and users collection, adds a database and users
    collection objects (if no exist) as attributes to flask.g, return users collection object.
    optionally takes the mongodb address (localhost by default)"""
    db = get_db(g, dbname)
    users = getattr(g, 'users', None)
    if users is None:
        users = g.users = db[users_col_name]
    return users

def get_files_col(g, dbname, files_col_name, addres='mongodb://localhost:27017/'):
    """requires g object from Flask, names of database and files collection, adds a database and files
    collection objects (if no exist) as attributes to flask.g, return files collection object.
    optionally takes the mongodb address (localhost by default)"""
    db = get_db(g, dbname)
    files = getattr(g, 'files', None)
    if files is None:
        files = g.files = db[files_col_name]
    return files


# Functions for working with users collection
def remake_users(g, yes='no', dbname='gorbin', users_col_name='users'):
    """takes flask.g object and the second parameter "yes" as confirmation. clear collection, build the indexes.
    optionally takes database and users collection names (\"gorbin\", \"users\" by default)"""
    if yes == "yes":
        col = get_users_col(g, dbname, users_col_name)
        col.remove()
        col.create_index('login', unique=True)
        col.create_index('email', unique=True)
    else: uprint(("as a confirmation, add \"yes\" with the second parameter"))

def add_user(g, login, pas, email, dbname='gorbin', users_col_name='users'):
    """takes flask.g object, login, password, email. adds a user to the collection, returns its unique _id object.
    optionally takes database and users collection names (\"gorbin\", \"users\" by default)"""
    col = get_users_col(g, dbname, users_col_name)
    _id = col.insert_one({'login':login, 'pas': pas, 'email':email, 'create_date':now_stamp(), 'deleted':False}).inserted_id
    return _id

def check_user(g, login, pas, dbname='gorbin', users_col_name='users'):
    """takes flask.g object, login and password, returns True if such user exists and is not deleted or returns False.
    optionally takes database and users collection names (\"gorbin\", \"users\" by default)"""
    col = get_users_col(g, dbname, users_col_name)
    if col.count({'login':login, 'pas':pas, 'deleted':False}) == 1: return True
    else: return False

def del_user(g, _id=None, login=None, dbname='gorbin', users_col_name='users'):
    """takes flask.g object, _id or login, switches deleted flag to Tru for this user.
    optionally takes database and users collection names (\"gorbin\", \"users\" by default)"""
    col = get_users_col(g, dbname, users_col_name)
    if _id or login:
        col.update_one({'$or':[{'_id':obj_id(_id)}, {'login':login}]}, {'$set':{'deleted':True}})
    else: uprint('could not delete user. did you forget to enter _id or login?')


# Functions for working with files collection
def remake_files(g, yes='no', dbname='gorbin', files_col_name='files'):
    """takes flask.g object and the second parameter "yes" as confirmation. clear collection.
    optionally takes database and files collection names (\"gorbin\", \"files\" by default)"""
    if yes == "yes":
        col = get_files_col(g, dbname, files_col_name)
        col.remove()
        #col.create_index(['owner', 'name'], unique=True)
    else: uprint(("as a confirmation, add \"yes\" with the second parameter"))

def add_file(g, owner, name, size, dbname='gorbin', files_col_name='files'):
    """takes flask.g object, name, size, owner. adds a file to the files collection, returns its unique _id object.
    optionally takes database and files collection names (\"gorbin\", \"files\" by default)"""
    col = get_files_col(g, dbname, files_col_name)
    _id = col.insert_one({'owner':owner, 'name':name, 'size':size, 'data':now_stamp(), 'deleted':False}).inserted_id
    return _id

def check_file(g, owner, name, dbname='gorbin', files_col_name='files'):
    """takes flask.g object, owner and name, returns True if such file exists and is not deleted or returns False.
    optionally takes database and files collection names (\"gorbin\", \"files\" by default)"""
    col = get_files_col(g, dbname, files_col_name)
    if col.count({'owner':owner, 'name':name, 'deleted':False}) >= 1: return True
    else: return False

def del_file(g, _id, dbname='gorbin', files_col_name='files'):
    """takes flask.g object and _id of file, switches deleted flag to Tru for this file.
    optionally takes database and files collection names (\"gorbin\", \"files\" by default)"""
    col = get_files_col(g, dbname, files_col_name)
    col.update_one({'_id':obj_id(_id)}, {'$set':{'deleted':True}})

