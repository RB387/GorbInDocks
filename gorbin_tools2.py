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
import time
from os import urandom, path, mkdir



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

def time2stamp(date, plus = 0):
    return time.mktime((dt.datetime.strptime(date, "%Y-%m-%d") + plus * dt.timedelta(days = 1)).timetuple())

def str_now():
    """returns the current datetime in string like '2019-10-14 18:24:14'"""
    return str(dt.datetime.now())[:-7]

def now():
    """returns the current datetime as datetime object"""
    return dt.datetime.now()


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


# MongoDB adn log functions
class mongo_tools():
    def __init__(self, flask_g):
        self.g = flask_g

    # Useful visible print function
    def vprint(self, *items):
        """takes >= 1 object, prints them line by line for easy view"""
        self.write_log(call_function="vprint", items=items)
        print('\n-----------------------\n')
        for i in items:
            print('\t', i)
        print('\n-----------------------\n')

    def get_db(self):
        """Adds a database object (if no exists), MONGO_ADDRESS, DB_NAME, USERS_COL_NAME, FILES_COL_NAME, LINKS_COL_NAME
        as attributes to flask.g and returns a database object"""
        db = getattr(self.g, 'db', None)
        if db is None:
            from config import MONGO_ADDRESS, DB_NAME, USERS_COL_NAME, FILES_COL_NAME, LINKS_COL_NAME
            self.g.MONGO_ADDRESS = MONGO_ADDRESS
            self.g.DB_NAME = DB_NAME
            self.g.USERS_COL_NAME = USERS_COL_NAME
            self.g.FILES_COL_NAME = FILES_COL_NAME
            self.g.LINKS_COL_NAME = LINKS_COL_NAME
            client = MongoClient(self.g.MONGO_ADDRESS)
            db = self.g.db = client[self.g.DB_NAME]
            self.write_log(call_function="get_db", state="connection done")
        return db

    def get_users_col(self):
        """Adds a database and users collection objects (if no exist) as attributes to flask.g. returns users collection object"""
        db = self.get_db()
        users = getattr(self.g, 'users', None)
        if users is None:
            users = self.g.users = db[self.g.USERS_COL_NAME]
            self.write_log(call_function='get_users_col', state="connection done")
        return users

    def get_files_col(self):
        """Adds a database and files collection objects (if no exist) as attributes to flask.g. returns files collection object"""
        db = self.get_db()
        files = getattr(self.g, 'files', None)
        if files is None:
            files = self.g.files = db[self.g.FILES_COL_NAME]
            self.write_log(call_function='get_files_col', state="connection done")
        return files

    def get_links_col(self):
        """Adds a database and links collection objects (if no exist) as attributes to flask.g. returns links collection object"""
        db = self.get_db()
        links = getattr(self.g, 'links', None)
        if links is None:
            links = self.g.links = db[self.g.LINKS_COL_NAME]
            self.write_log(call_function='get_links_col', state="create connection")
        return links

    def get_log_file(self):
        """Adds a database and logs folder objects (if no exist) as attributes to flask.g. Returns log folder's path"""
        log_file = getattr(self.g, 'log_file', None)
        if log_file is None or log_file.closed:
            from config import  LOG_FOLDER
            if not path.exists(LOG_FOLDER): mkdir(LOG_FOLDER)
            file_name = dt.datetime.now().strftime("log_date_%Y-%m-%d.txt")
            log_file = self.g.log_file = open(path.join(LOG_FOLDER, file_name), "a+")
        return log_file

    def write_log(self, **items):
        """Write down all **arguments to log f ile. Example: write_log(call_function="login='Mike')"""
        line = str_now()
        file = self.get_log_file()
        for item in items.items():
            line += " {}:{}".format(item[0], item[1])
        line += "\n"
        file.write(line)


    # Functions for working with users collection
    def remake_users(self, yes='no'):
        """Takes "yes" as a confirmation. Clears users collection, builds the indexes"""
        self.write_log(call_function='remake_users', yes=yes)
        if yes == "yes":
            u_col = self.get_users_col()
            u_col.delete_many({})
            u_col.create_index('login', unique=True)
            u_col.create_index('email', unique=True)
        else: 
            self.write_log(call_function='remake_users', yes=yes, exception="As a confirmation, add \"yes\" with the parameter")
            raise Exception("As a confirmation, add \"yes\" with the parameter")

    def add_user(self, login: str, pas: bytes, email: str, status='simple'):
        """Takes login, password, email. Additionally, takes user's status simple/admin ('simple' by default).
        Adds a user to the users collection, returns its unique _id object"""
        self.write_log(call_function='add_user', login=login, email=email, status=status)
        u_col = self.get_users_col()
        user_id = u_col.insert_one({'login':login, 'pas':pas, 'email':email, 'status':status, 'shared':{}, 'create_date':now_stamp(), 'deleted':False}).inserted_id
        return user_id

    def get_user(self, login: str, pas: bytes):
        """Takes user's login and user's encrypted password. Returns data of user in dict
        if such user exists and is not deleted or returns None"""
        self.write_log(call_function="get_user", login=login)
        u_col = self.get_users_col()
        user_data = u_col.find_one({'login':login, 'deleted':False})
        if user_data:
            if user_data['pas'] == pas: return user_data
        return None

    def get_user_data(self, login: str):
        """Takes user's login and user's encrypted password. Returns data of user in dict
        if such user exists and is not deleted or returns None"""
        self.write_log(call_function="get_user_data", login=login)
        u_col = self.get_users_col()
        user_data = u_col.find_one({'login':login, 'deleted':False})
        if user_data:
            return user_data
        return None

    def get_user_status(self, login: str):
        """Takes user's login. Returns its status"""
        self.write_log(call_function="get_user_status", login=login)
        u_col = self.get_users_col()
        user_data = u_col.find_one({'login':login, 'deleted':False})['status']
        if user_data:
            return user_data
        return None

    def get_user_id(self, login: str):
        """Takes user's login. Returns its _id"""
        self.write_log(call_function="get_user_id", login=login)
        u_col = self.get_users_col()
        user_data = u_col.find_one({'login':login, 'deleted':False}, {})
        if user_data:
            return user_data['_id']
        return None

    def check_login(self, login: str):
        """Takes user's login. Returns True if such login is already used and False if it is not"""
        self.write_log(call_function="check_login", login=login)
        u_col = self.get_users_col()
        return bool(u_col.find_one({'login':login}, {}))

    def check_email(self, email: str):
        """Takes email. Returns True if such email is already used and False if it is not"""
        self.write_log(call_function="check_email", email=email)
        u_col = self.get_users_col()
        return bool(u_col.find_one({'email':email}, {})) 

    def update_user(self, user_id, login: str, pas: bytes, email: str):
        """Takes unique user's _id, new login, new password, new email. Updates user's data"""
        self.write_log(call_function="update_user", user_id=user_id, login=login, email=email)
        u_col = self.get_users_col()
        u_col.update_one({'_id':obj_id(user_id)}, {'$set':{'login':login, 'pas':pas, 'email':email}})

    def update_user_mail(self, login: str, email: str):
        """Takes unique login, new email. Updates user's data"""
        self.write_log(call_function="update_user_mail", login=login, email=email)
        u_col = self.get_users_col()
        u_col.update_one({'login':login}, {'$set':{'email':email}})

    def update_user_status(self, login: str, status: str):
        """Takes unique login, new status. Updates user's data"""
        self.write_log(call_function="update_user_status", login=login, status=status)
        u_col = self.get_users_col()
        u_col.update_one({'login':login}, {'$set':{'status':status}})

    def update_user_pass(self, login: str, pas: bytes):
        """Takes unique login, new password. Updates user's data"""
        self.write_log(call_function="update_user_pass", login=login)
        u_col = self.get_users_col()
        u_col.update_one({'login':login}, {'$set':{'pas':pas}})

    def del_user(self, user_id=None, login=None):
        """Takes unique user's _id or user's login. Switches deleted flag to Tru for this user"""
        self.write_log(call_function="del_user", user_id=user_id, login=login)
        u_col = self.get_users_col()
        if user_id or login:
            u_col.update_one({'$or':[{'_id':obj_id(user_id)}, {'login':login}]}, {'$set':{'deleted':True}})
        else: 
            self.write_log(call_function="remake_files", exception='Could not delete user. Did you forget to enter user\'s _id or user\'s login?')
            raise Exception('Could not delete user. Did you forget to enter user\'s _id or user\'s login?')


    # Functions for working with files collection
    def remake_files(self, yes='no'):
        """Takes "yes" as a confirmation. Clears files collection"""
        self.write_log(call_function="remake_files", yes=yes)
        if yes == "yes":
            f_col = self.get_files_col()
            f_col.delete_many({})
        else: 
            self.write_log(call_function="remake_files", yes=yes, exception="As a confirmation, add \"yes\" with the parameter")
            raise Exception("As a confirmation, add \"yes\" with the parameter")

    def add_file(self, owner, name: str, size: int, location: str, directory='/', comment=None, tags=[]):
        """Takes file's owner, name, size, location and _id of the folder in which it is located ('/' for the main directory).
        Adds a file to the files collection. Returns its unique _id object"""
        self.write_log(call_function='add_file', owner=owner, name=name, size=size, location=location, directory=directory, comment=comment, tags=tags)
        f_col = self.get_files_col()
        file_id = f_col.insert_one({'owner':owner, 'name':name, 'size':size, 'dir':str(directory), 'location':location, 'comment':comment, 'tags':tags,
            star:False, 'type':'file', 'data':now_stamp(), 'deleted':False, 'fully_deleted':False}).inserted_id
        return file_id

    def add_folder(self, owner, name: str, size: int, location: str, directory='/', comment=None, tags=[]):
        """Takes file's owner, name, size, location and _id of the folder in which it is located ('/' for the main directory).
        Adds a file to the files collection. Returns its unique _id object"""
        self.write_log(call_function='add_folder', owner=owner, name=name, size=size, location=location, directory=directory, comment=comment, tags=tags)
        f_col = self.get_files_col()
        file_id = f_col.insert_one({'owner':owner, 'name':name, 'size':size, 'dir':str(directory), 'location':location, 'comment':comment, 'tags':tags,
            'type':'folder', 'data':now_stamp(), 'deleted':False}).inserted_id
        return file_id

    def update_file(self, file_id, name: str, size: int, comment, tags: list):
        """Takes unique file's _id, new file name, new size, new comment, new list of tags. Updates file's data"""
        self.write_log(call_function='update_file', file_id=file_id, name=name, size=size, comment=comment, tags=tags)
        f_col = self.get_files_col()
        f_col.update_one({'_id':obj_id(file_id)}, {'$set':{'name':name, 'size':size, 'comment':comment, 'tags':tags}})

    def get_file(self, file_id):
        """Takes unique file's _id. Returns file information of this file"""
        self.write_log(call_function='get_file', file_id=file_id)
        f_col = self.get_files_col()
        return f_col.find_one({'_id': obj_id(file_id), 'deleted':False})

    def search_files(self, owner, **kwargs):
        """coded by RB387"""
        self.write_log(call_function='search_files', owner=owner)
        f_col = self.get_files_col()
        result = []
        cols = list(f_col.find({'owner':owner, 'deleted':False}))
        for col in cols:
            match = True
            for arg in kwargs:
                if arg == 'tags':
                    for tag in kwargs[arg]:
                        if tag not in col[arg]:
                            match = False
                            break
                elif arg == 'data':
                    if not ((kwargs[arg][0] <= col[arg]) and (kwargs[arg][1] >= col[arg])):
                        match = False
                elif arg == 'name':
                    if kwargs[arg] not in col[arg]:
                        match = False
            if match:
                result.append(col)
        return result

    def search_files_by_date(self, owner, date_begin, date_end):
        """coded by RB387"""
        self.write_log(call_function='search_user_files_by_date', owner = owner)
        f_col = list(self.get_files_col().find({'owner':owner}))
        result = []
        for col in f_col:
            if (date_begin <= col['data']) and (date_end >= col['data']):
                result.append(col)
        return result

    def get_files_by_tag(self, tag, owner):
        """Takes tag and file's owner. Returns list of files with this tag"""
        self.write_log(call_function='get_files_by_tag', tag=tag, owner=owner)
        f_col = self.get_files_col()
        result = []
        cols = list(f_col.find({'owner':owner, 'deleted':False}))
        for col in cols:
            if tag in col['tags']:
                result.append(col)
        return result
        
    def check_file(self, owner, name: str):
        """Takes unique file's _id, file's owner and file's name. Returns True if such file exists and is not deleted or returns False"""
        self.write_log(call_function='check_file', owner=owner, name=name)
        f_col = self.get_files_col()
        return bool(f_col.find_one({'owner':owner, 'name':name, 'deleted':False}))

    def set_star(self, file_id, value: bool):
        """Takes unique file's _id, new value of star field. Sets new value to the file"""
        self.write_log(call_function='set_star', file_id=file_id, value=value)
        f_col = self.get_files_col()
        f_col.update_one({'_id':obj_id(file_id)}, {'$set':{'star':value}})

    def del_file(self, file_id):
        """Takes unique file's _id. Switches deleted flag to True for this file"""
        self.write_log(call_function='del_file', file_id=file_id)
        f_col = self.get_files_col()
        f_col.update_one({'_id':obj_id(file_id)}, {'$set':{'deleted':True}})

    def revert_file(self, file_id):
        """Takes unique file's _id. Switches deleted flag to False for this file"""
        self.write_log(call_function='revert_file', file_id=file_id)
        f_col = self.get_files_col()
        f_col.update_one({'_id':obj_id(file_id)}, {'$set':{'deleted':False}})

    def del_fully(self, file_id):
        """Takes unique file's _id. Switches fully_deleted flag to Tru for this file"""
        self.write_log(call_function='del_fully', file_id=file_id)
        f_col = self.get_files_col()
        f_col.update_one({'_id':obj_id(file_id)}, {'$set':{'fully_deleted':True}})

    def get_user_files(self, owner, directory):
        """Takes file's owner and directory in which it is located. Returns list of files in this directory.
        if it has no files, it returns []"""
        self.write_log(call_function='get_user_files', owner=owner, directory=directory)
        f_col = self.get_files_col()
        return list(f_col.find({'owner':owner, 'deleted':False, 'dir':str(directory)}))

    def get_user_trash(self, owner):
        """Takes file's owner. Returns list of deleted files. if it has no files, it returns []"""
        self.write_log(call_function='get_user_trash', owner=owner)
        f_col = self.get_files_col()
        return list(f_col.find({'owner':owner, 'deleted':True, 'fully_deleted':False}))

    def add_comment(self, file_id, comment: str):
        """Takes unique file's _id. Adds a comment to this file"""
        self.write_log(call_function='add_comment', file_id=file_id, comment=comment) 
        f_col = self.get_files_col()
        f_col.update_one({'_id':obj_id(file_id)}, {'$set':{'comment':comment}})

    def add_tags(self, file_id, tags: list):
        """Takes unique file's _id and list of tags. Adds tags to this file"""
        self.write_log(call_function='add_tags', file_id=file_id, tags=tags)
        f_col = self.get_files_col()
        for tag in tags:
            f_col.update_one({'_id':obj_id(file_id)}, {'$addToSet':{'tags':tag}})

    def del_tags(self, file_id, tags: list):
        """Takes  unique file's _id and list of tags. Deletes tags from this file"""
        self.write_log(call_function='del_tags', file_id=file_id, tags=tags)
        f_col = self.get_files_col()
        f_col.update_one({'_id':obj_id(file_id)}, {'$pullAll':{'tags':tags}})


    # Functions for working with links collection
    def remake_links(self, yes='no'):
        """Takes "yes" as a confirmation. Clears links collection"""
        self.write_log(call_function="remake_links", yes=yes)
        if yes == "yes":
            l_col = self.get_links_col()
            l_col.delete_many({})
        else: 
            self.write_log(call_function="remake_links", yes=yes, exception="As a confirmation, add \"yes\" with the parameter")
            raise Exception("As a confirmation, add \"yes\" with the parameter")

    def make_link(self, file_ids: list, comment=None):
        """Takes list of file's _id, additionally, the comment (None by default). Adds a new unique link to links collection.
        Returns generated link. If link cannot be added to the collection with a DuplicateKeyError for 5 times, it raised Exception, but this case is impossible!"""
        self.write_log(call_function='make_link', file_ids=file_ids, comment=comment)
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
        self.write_log(call_function='get_linked', link=link) 
        l_col = self.get_links_col()
        f_col = self.get_files_col()
        file_ids = l_col.find_one({'_id':link, 'deleted':False})
        if file_ids != None: return {'files':list(f_col.find({'_id':{'$in':file_ids['files']}})), 'comment':file_ids['comment']}
        return file_ids

    def del_link(self, link: str):
        """Takes the link. Switches deleted flag to Tru for this link"""
        self.write_log(call_function='del_link', link=link)
        l_col = self.get_links_col()
        l_col.update_one({'_id':link}, {'$set':{'deleted':True}})


    # Functions for working with shared files
    def add_shared(self, login: str, user_id, file_ids: list):
        """Takes login of user who shared, current user's _id and list of file's _id which were shared with current user.
        Adds list of file's _id to his shared list"""
        self.write_log(call_function='add_shared', login=login, user_id=user_id, file_ids=file_ids)
        u_col = self.get_users_col()
        for file_id in file_ids:
            u_col.update_one({'_id':obj_id(user_id)}, {'$addToSet':{'shared.'+login:obj_id(file_id)}})

    def get_shared(self, user_id):
        """Takes unique user's _id. Returns dict: keys - logins of users who shared, values - 
        list of file's _id which were shared with current user by this user"""
        self.write_log(call_function='get_shared', user_id=user_id)
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
        self.write_log(call_function='del_shared', login=login, user_id=user_id, file_ids=file_ids)
        u_col = self.get_users_col()
        u_col.update_one({'_id':obj_id(user_id)}, {'$pullAll':{'shared.'+login:list(map(obj_id, file_ids))}})

    def check_availability(self, login: str, user_id, file_id):
        """Takes login of user who shared. current user's _id and unique files's _id. Returns True if this file is available to this user, else returns False"""
        self.write_log(call_function='check_availability', login=login, user_id=user_id, file_id=file_id)
        u_col = self.get_users_col()
        return bool(u_col.find_one({'_id':obj_id(user_id), 'shared.'+login:obj_id(file_id)}, {}))


    #Admin Functions
    def get_simple_users(self, deleted=False):
        """Takes deleted parameter which can be True, False, 'all' (False by default).
        If False: returns list of all non-deleed simple users (no admins).
        If True: returns list of all deleted simple users (no admins).
        Else: returns list of all simple users (no admins)"""
        self.write_log(call_function='get_simple_users', deleted=deleted)
        u_col = self.get_users_col()
        if deleted == True: return list(u_col.find({'status':'simple', 'deleted':True}))
        elif  deleted == False: return list(u_col.find({'status':'simple', 'deleted':False}))
        else: return list(u_col.find({'status':'simple'}))