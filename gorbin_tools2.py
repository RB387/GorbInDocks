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
class mongo_tools():
    def __init__(self, flask_g):
        self.g = flask_g

    def get_db(self):
        """Adds a database object (if no exists), MONGO_ADDRESS, DB_NAME, USERS_COL_NAME, FILES_COL_NAME, LINKS_COL_NAME
        as attributes to flask.g and returns a database object"""
        db = getattr(self, 'db', None)
        if db is None:
            from config import MONGO_ADDRESS, DB_NAME, USERS_COL_NAME, FILES_COL_NAME, LINKS_COL_NAME
            self.g.MONGO_ADDRESS = MONGO_ADDRESS
            self.g.DB_NAME = DB_NAME
            self.g.USERS_COL_NAME = USERS_COL_NAME
            self.g.FILES_COL_NAME = FILES_COL_NAME
            self.g.LINKS_COL_NAME = LINKS_COL_NAME
            client = MongoClient(self.g.MONGO_ADDRESS)
            db = self.g.db = client[self.g.DB_NAME]
        return db

    def get_users_col(self):
        """Adds a database and users collection objects (if no exist) as attributes to flask.g. returns users collection object"""
        db = self.get_db()
        users = getattr(self.g, 'users', None)
        if users is None:
            users = self.g.users = db[self.g.USERS_COL_NAME]
        return users

    def get_files_col(self):
        """Adds a database and files collection objects (if no exist) as attributes to flask.g. returns files collection object"""
        db = self.get_db()
        files = getattr(self.g, 'files', None)
        if files is None:
            files = self.g.files = db[self.g.FILES_COL_NAME]
        return files

    def get_links_col(self):
        """Adds a database and links collection objects (if no exist) as attributes to flask.g. returns links collection object"""
        db = self.get_db()
        links = getattr(self.g, 'links', None)
        if links is None:
            links = self.g.links = db[self.g.LINKS_COL_NAME]
        return links


    # Functions for working with users collection
    def remake_users(self, yes='no'):
        """Takes "yes" as a confirmation. Clears users collection, builds the indexes"""
        if yes == "yes":
            u_col = self.get_users_col()
            u_col.delete_many({})
            u_col.create_index('login', unique=True)
            u_col.create_index('email', unique=True)
        else: Exception("As a confirmation, add \"yes\" with the parameter")

    def add_user(self, login: str, pas: bytes, email: str, status='simple'):
        """Takes login, password, email. Additionally, takes user's status simple/admin ('simple' by default).
        Adds a user to the users collection, returns its unique _id object"""
        u_col = self.get_users_col()
        user_id = u_col.insert_one({'login':login, 'pas':pas, 'email':email, 'status':status, 'shared':{}, 'create_date':now_stamp(), 'deleted':False}).inserted_id
        return user_id

    def get_user(self, login: str, pas: bytes):
        """Takes user's login and user's encrypted password. Returns data of user in dict
        if such user exists and is not deleted or returns None"""
        u_col = self.get_users_col()
        user_data = u_col.find_one({'login':login, 'deleted':False})
        if user_data:
            if user_data['pas'] == pas: return user_data
        return None

    def get_user_status(self, login: str):
        u_col = self.get_users_col()
        user_data = u_col.find_one({'login':login, 'deleted':False})['status']
        if user_data:
            return user_data
        return None

    def get_user_id(self, login):
        u_col = self.get_users_col()
        user_data = u_col.find_one({'login':login, 'deleted':False})
        if user_data:
            return user_data['_id']
        return None

    def check_login(self, login: str):
        """Takes user's login. Returns True if such login is already used and False if it is not"""
        u_col = self.get_users_col()
        return bool(u_col.find_one({'login':login}, {}))

    def check_email(self, email: str):
        """Takes email. Returns True if such email is already used and False if it is not"""
        u_col = self.get_users_col()
        return bool(u_col.find_one({'email':email}, {})) 

    def update_user(self, user_id, login, pas, email):
        """Takes unique user's _id, new login, new password, new email. Updates user's data"""
        u_col = self.get_users_col()
        u_col.update_one({'_id':obj_id(user_id)}, {'$set':{'login':login, 'pas':pas, 'email':email}})

    def del_user(self, user_id=None, login=None):
        """Takes unique user's _id or user's login. Switches deleted flag to Tru for this user"""
        u_col = self.get_users_col()
        if user_id or login:
            u_col.update_one({'$or':[{'_id':obj_id(user_id)}, {'login':login}]}, {'$set':{'deleted':True}})
        else: Exception('Could not delete user. Did you forget to enter user\'s _id or user\'s login?')


    # Functions for working with files collection
    def remake_files(self, yes='no'):
        """Takes "yes" as a confirmation. Clears files collection"""
        if yes == "yes":
            f_col = self.get_files_col()
            f_col.delete_many({})
        else: Exception("As a confirmation, add \"yes\" with the parameter")

    def add_file(self, owner, name: str, size: int, location: str, directory='/', comment=None, tags=[]):
        """Takes file's owner, name, size, location and _id of the folder in which it is located ('/' for the main directory).
        Adds a file to the files collection. Returns its unique _id object"""
        f_col = self.get_files_col()
        file_id = f_col.insert_one({'owner':owner, 'name':name, 'size':size, 'dir':str(directory), 'location':location, 'comment':comment, 'tags':tags,
            'type':'file', 'data':now_stamp(), 'deleted':False}).inserted_id
        return file_id

    def add_folder(self, owner, name: str, size: int, location: str, directory='/', comment=None, tags=[]):
        """Takes file's owner, name, size, location and _id of the folder in which it is located ('/' for the main directory).
        Adds a file to the files collection. Returns its unique _id object"""
        f_col = self.get_files_col()
        file_id = f_col.insert_one({'owner':owner, 'name':name, 'size':size, 'dir':str(directory), 'location':location, 'comment':comment, 'tags':tags,
            'type':'folder', 'data':now_stamp(), 'deleted':False}).inserted_id
        return file_id

    def update_file(self, file_id, name: str, size: int, comment, tags: list):
        """Takes unique file's _id, new file name, new size, new comment, new list of tags. Updates file's data"""
        f_col = self.get_files_col()
        f_col.update_one({'_id':obj_id(file_id)}, {'$set':{'name':name, 'size':size, 'comment':comment, 'tags':tags}})

    def get_file(self, file_id):
        """Takes unique file's _id. Returns file information of this file"""
        f_col = self.get_files_col()
        return f_col.find_one({'_id': obj_id(file_id), 'deleted':False})

    def get_files_by_tag(self, tag, owner):
        f_col = self.get_files_col()
        result = []
        cols = list(f_col.find({'owner':owner, 'deleted':False}))
        for col in cols:
            if tag in col['tags']:
                result.append(col)
        return result
        
    def check_file(self, owner, name: str):
        """Takes unique file's _id, file's owner and file's name. Returns True if such file exists and is not deleted or returns False"""
        f_col = self.get_files_col()
        return bool(f_col.find_one({'owner':owner, 'name':name, 'deleted':False}))

    def del_file(self, file_id):
        """Takes unique file's _id. Switches deleted flag to Tru for this file"""
        f_col = self.get_files_col()
        f_col.update_one({'_id':obj_id(file_id)}, {'$set':{'deleted':True}})

    def get_user_files(self, owner, directory):
        """Takes file's owner and directory in which it is located. Returns list of files in this directory.
        if it has no files, it returns []"""
        f_col = self.get_files_col()
        return list(f_col.find({'owner':owner, 'deleted':False, 'dir':str(directory)}))

    def add_comment(self, file_id, comment: str):
        """Takes unique file's _id. Adds a comment to this file"""
        f_col = self.get_files_col()
        f_col.update_one({'_id':obj_id(file_id)}, {'$set':{'comment':comment}})

    def add_tags(self, file_id, tags: list):
        """Takes unique file's _id and list of tags. Adds tags to this file"""
        f_col = self.get_files_col()
        for tag in tags:
            f_col.update_one({'_id':obj_id(file_id)}, {'$addToSet':{'tags':tag}})

    def del_tags(self, file_id, tags: list):
        """Takes  unique file's _id and list of tags. Deletes tags from this file"""
        f_col = self.get_files_col()
        f_col.update_one({'_id':obj_id(file_id)}, {'$pullAll':{'tags':tags}})


    # Functions for working with links collection
    def remake_links(self, yes='no'):
        """Takes "yes" as a confirmation. Clears links collection"""
        if yes == "yes":
            l_col = self.get_links_col()
            l_col.delete_many({})
        else: Exception("As a confirmation, add \"yes\" with the parameter")

    def make_link(self, file_ids: list, comment=None):
        """Takes list of file's _id, additionally, the comment (None by default). Adds a new unique link to links collection.
        Returns generated link. If link cannot be added to the collection with a DuplicateKeyError for 5 times, it raised Exception, but this case is impossible!"""
        l_col = self.get_links_col()
        retracts = 0
        success_writen = False
        while not success_writen:
            link = base64.b64encode(sha1(urandom(64)).digest()).decode('utf-8').replace('/', 's')
            try:
                l_col.insert_one({'_id':link, 'files':list(map(obj_id, file_ids)), 'comment':comment, 'deleted':False})
                success_writen = True
                break
            except DuplicateKeyError:
                retracts += 1
            if retracts >= 5: break
        if success_writen: return link
        raise Exception('NEVER WAS AND HERE AGAIN!!!\nError on link generation, sharing failed')

    def get_linked(self, link: str):
        """Takes unique link. Returns dict {'files':list of file's _id, 'comment':comment to this list (may be None)}.
        If such link does not exist or deleted, returns None"""
        l_col = self.get_links_col()
        f_col = self.get_files_col()
        file_ids = l_col.find_one({'_id':link, 'deleted':False})
        if file_ids != None: return {'files':list(f_col.find({'_id':{'$in':file_ids['files']}})), 'comment':file_ids['comment']}
        return file_ids

    def del_link(self, link: str):
        """Takes the link. Switches deleted flag to Tru for this link"""
        l_col = self.get_links_col()
        l_col.update_one({'_id':link}, {'$set':{'deleted':True}})


    # Functions for working with shared files
    def add_shared(self, login: str, user_id, file_ids: list):
        """Takes login of user who shared, current user's _id and list of file's _id which were shared with current user.
        Adds list of file's _id to his shared list"""
        u_col = self.get_users_col()
        for file_id in file_ids:
            u_col.update_one({'_id':obj_id(user_id)}, {'$addToSet':{'shared.'+login:obj_id(file_id)}})

    def get_shared(self, user_id):
        """Takes unique user's _id. Returns dict: keys - logins of users who shared, values - 
        list of file's _id which were shared with current user by this user"""
        u_col = self.get_users_col()
        f_col = self.get_files_col()
        ret = {}
        files = u_col.find_one({'_id':user_id, 'deleted':False}, {'_id':0, 'shared':1})
        if files != None:
            ret = {}
            for log, lst in files['shared'].items():
                if lst != []: ret[log] = list(f_col.find({'_id':{'$in': lst}}))
            return ret
        return None

    def del_shared(self, login: str, user_id, file_ids: list):
        """Takes login of user who shared, current user's _id and list of file's _id which were shared with current user.
        Deletes list of file's _id from his shared list"""
        u_col = self.get_users_col()
        u_col.update_one({'_id':obj_id(user_id)}, {'$pullAll':{'shared.'+login:list(map(obj_id, file_ids))}})

    def check_availability(self, login: str, user_id, file_id):
        """Takes login of user who shared. current user's _id and unique files's _id. Returns True if this file is available to this user, else returns False"""
        u_col = self.get_users_col()
        return bool(u_col.find_one({'_id':obj_id(user_id), 'shared.'+login:obj_id(file_id)}, {}))


    #Admin Functions
    def get_simple_users(self, deleted=False):
        """Takes deleted parameter which can be True, False, 'all' (False by default).
        If False: returns list of all non-deleed simple users (no admins).
        If True: returns list of all deleted simple users (no admins).
        Else: returns list of all simple users (no admins)"""
        u_col = self.get_users_col()
        if deleted == True: return list(u_col.find({'status':'simple', 'deleted':True}))
        elif  deleted == False: return list(u_col.find({'status':'simple', 'deleted':False}))
        else: return list(u_col.find({'status':'simple'}))