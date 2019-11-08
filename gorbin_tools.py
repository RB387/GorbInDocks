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
from hashlib import sha256, sha1
import datetime as dt
import base64
from os import urandom



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
def get_db(g):
    """takes flask.g object, adds a database object (if no exists), MONGO_ADDRESS, DB_NAME, USERS_COL_NAME, FILES_COL_NAME
    as attributes to flask.g and returns a database object"""
    db = getattr(g, 'db', None)
    if db is None:
        from config import MONGO_ADDRESS, DB_NAME, USERS_COL_NAME, FILES_COL_NAME, LINKS_COL_NAME
        g.MONGO_ADDRESS = MONGO_ADDRESS
        g.DB_NAME = DB_NAME
        g.USERS_COL_NAME = USERS_COL_NAME
        g.FILES_COL_NAME = FILES_COL_NAME
        client = MongoClient(g.MONGO_ADDRESS)
        db = g.db = client[g.DB_NAME]
    return db

def get_users_col(g):
    """takes flask.g object, adds a database and users
    collection objects (if no exist) as attributes to flask.g, return users collection object"""
    db = get_db(g)
    users = getattr(g, 'users', None)
    if users is None:
        users = g.users = db[g.USERS_COL_NAME]
    return users

def get_files_col(g):
    """takes flask.g object object, adds a database and files
    collection objects (if no exist) as attributes to flask.g, return files collection object"""
    db = get_db(g)
    files = getattr(g, 'files', None)
    if files is None:
        files = g.files = db[g.FILES_COL_NAME]
    return files

def get_links_col(g):
    """takes flask.g object object, adds a database and links collection objects (if no exist)
    as attributes to flask.g, return files collection object"""
    db = get_db(g)
    links = getattr(g, 'links', None)
    if links is None:
        links = g.links = db[g.LINKS_COL_NAME]
    return links


# Functions for working with users collection
def remake_users(g, yes='no'):
    """takes flask.g object and the second parameter "yes" as confirmation. clear collection, build the indexes"""
    if yes == "yes":
        col = get_users_col(g)
        col.delete_many({})
        col.create_index('login', unique=True)
        col.create_index('email', unique=True)
    else: vprint(("as a confirmation, add \"yes\" with the second parameter"))

def add_user(g, login, pas, email, status='simple'):
    """takes flask.g object, login, password, email. additionally, takes user status simple/admin ('simple' by default).
    adds a user to the collection, returns its unique _id object"""
    col = get_users_col(g)
    _id = col.insert_one({'login':login, 'pas': pas, 'email':email, 'status':status, 'shared':{}, 'create_date':now_stamp(), 'deleted':False}).inserted_id
    return _id

def get_user(g, login, pas):
    """takes flask.g object, login and password, returns data of user in dict
    if such user exists and is not deleted or returns False"""
    col = get_users_col(g)
    user_data = col.find_one({'login':login, 'deleted':False})
    if user_data:
        if user_data['pas'] == pas: return user_data
    return False

def check_login(g, login):
    """takes flask.g object, login, returns True if such login is already used and False if it is not"""
    col = get_users_col(g)
    user_data = col.find_one({'login':login, 'deleted':False})
    if user_data:
        return True
    return False

def check_email(g, email):
    """takes flask.g object, email, returns True if such email is already used and False if it is not"""
    col = get_users_col(g)
    user_data = col.find_one({'email':email, 'deleted':False})
    if user_data:
        return True
    return False 

def del_user(g, _id=None, login=None):
    """takes flask.g object, _id or login, switches deleted flag to Tru for this user"""
    col = get_users_col(g)
    if _id or login:
        col.update_one({'$or':[{'_id':obj_id(_id)}, {'login':login}]}, {'$set':{'deleted':True}})
    else: vprint('could not delete user. did you forget to enter _id or login?')


# Functions for working with files collection
def remake_files(g, yes='no'):
    """takes flask.g object and the second parameter "yes" as confirmation. clear collection.
    optionally takes database and files collection names (\"gorbin\", \"files\" by default)"""
    if yes == "yes":
        col = get_files_col(g)
        col.delete_many({})
        #col.create_index(['owner', 'name'], unique=True)
    else: vprint(("as a confirmation, add \"yes\" with the second parameter"))

def add_file(g, owner, name, size, location, directory='/'):
    """takes flask.g object, owner, name, size, location and _id of the folder in which it is located ('/' for the main directory).
    adds a file to the files collection, returns its unique _id object"""
    col = get_files_col(g)
    directory = obj_id(directory) if directory != '/' else '/'
    _id = col.insert_one({'owner':owner, 'name':name, 'size':size, 'dir':directory, 'type':'file', 'location':location, 'data':now_stamp(), 'comment':None, 'deleted':False}).inserted_id
    return _id

def add_folder(g, owner, name, size, location, directory='/'):
    """takes flask.g object, owner, name, size, location and _id of the folder in which it is located ('/' for the main directory).
    adds a folder to the files collection, returns its unique _id object"""
    col = get_files_col(g)
    directory = obj_id(directory) if directory != '/' else '/'
    _id = col.insert_one({'owner':owner, 'name':name, 'size':size, 'dir':directory, 'type':'folder', 'location':location, 'data':now_stamp(), 'comment':None, 'deleted':False}).inserted_id
    return _id

def get_file(g, file_id):
    """takes flask.g object, id. returns file information by id"""
    col = get_files_col(g)
    return col.find_one({'_id': obj_id(file_id), 'deleted':False})

def check_file(g, owner, name):
    """takes flask.g object, owner and name, returns True if such file exists and is not deleted or returns False"""
    col = get_files_col(g)
    if col.count({'owner':owner, 'name':name, 'deleted':False}) >= 1: return True
    else: return False

def del_file(g, _id):
    """takes flask.g object and _id of file, switches deleted flag to Tru for this file"""
    col = get_files_col(g)
    col.update_one({'_id':obj_id(_id)}, {'$set':{'deleted':True}})

def get_user_files(g, owner):
    """takes flask.g object and owner of files, return iterable object with files of this owner.
    if it has no files, the returned object will have a length of 0"""
    col = get_files_col(g)
    return col.find({'owner':owner, 'deleted':False})

def add_comment(g, file_id, comment):
    """takes flask.g object and unique file's _id. add a comment to this file"""
    col = get_files_col(g)
    col.update_one({'_id':obj_id(file_id)}, {'$set':{'comment':comment}})


# Functions for working with links collection
def remake_links(g, yes='no'):
    """takes flask.g object and the second parameter "yes" as confirmation. clear collection.
    optionally takes database and files collection names (\"gorbin\", \"links\" by default)"""
    if yes == "yes":
        col = get_links_col(g)
        col.delete_many({})
    else: vprint(("as a confirmation, add \"yes\" with the second parameter"))


def make_link(g, file_ids, comment=None):
    """takes flask.g object and list _id of files/folders that will be available at this link, additionally, the comment
    (None by default). return a unique link"""
    col = get_links_col(g)
    link = base64.b64encode(sha1(urandom(64)).digest()).decode('utf-8').replace('/', 's')
    try: 
        col.insert_one({'_id':link, 'files':list(map(obj_id, file_ids)), 'comment':comment, 'deleted':False}).inserted_id
    except DuplicateKeyError:
        link = make_link(g, file_ids, comment)
    return link

def get_linked(g, link):
    """takes flask.g object and unique link. return dict {'files':list _id of files/folders, 'comment':comment to this list (may be None)}. if such link does not exist or deleted, return None"""
    col = get_links_col(g)
    f_col = get_files_col(g)
    file_ids = col.find_one({'_id':link, 'deleted':False})
    if file_ids != None: return {'files':list(f_col.find({'_id':{'$in':file_ids['files']}})), 'comment':file_ids['comment']}
    return file_ids

def del_link(g, link):
    """takes flask.g object and the link, switches deleted flag to Tru for this file"""
    col = get_links_col(g)
    col.update_one({'_id':link}, {'$set':{'deleted':True}})


# Functions for working with shared files
def get_user_shared(g, user_id):
    """takes flask.g object and unique user's _id. return dict: keys - logins of users who shared, values - 
    list _id of files which were shared with him by this user"""
    col = get_users_col(g)
    f_col = get_files_col(g)
    ret = {}
    files = col.find_one({'_id':user_id, 'deleted':False}, {'_id':0, 'shared':1})
    if files != None:
        ret = {}
        for log, lst in files['shared'].items():
	        if lst != []: ret[log] = list(f_col.find({'_id':{'$in': lst}}))
        return ret
    return None

def add_linked(g, login, user_id, file_ids):
    """takes flask.g object,  login of user who shared. current user's _id and list _id of files/folders which were shared with him. adds to his shared list files from list"""
    col = get_users_col(g)
    for file_id in file_ids:
        col.update_one({'_id':obj_id(user_id)}, {'$addToSet':{'shared.'+login:obj_id(file_id)}})

def del_shared(g, login, user_id, file_ids):
    """takes flask.g object, login of user who shared. current user's _id and list _id of files/folders which were shared with him. delete them from his shared list"""
    col = get_users_col(g)
    col.update_one({'_id':obj_id(user_id)}, {'$pullAll':{'shared.'+login:list(map(obj_id, file_ids))}})

def check_availability(g, login: str, user_id, file_id):
    """takes flask.g object,  login of user who shared. current user's _id and unique files's/folder's _id. return True if this file is available to this user, else return False"""
    col = get_users_col(g)
    checked = col.find_one({'_id':obj_id(user_id), 'shared.'+login:obj_id(file_id)}, {})
    if checked != None: return True
    return False
