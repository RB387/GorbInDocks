from gorbin_tools import *
import unittest
from time import sleep
from config import MONGO_ADDRESS, DB_NAME, USERS_COL_NAME, FILES_COL_NAME

class flask_g():
    def __init__(self):
        client = MongoClient(MONGO_ADDRESS)
        self.db = client[DB_NAME]
        self.MONGO_ADDRESS = MONGO_ADDRESS
        self.DB_NAME = DB_NAME
        self.USERS_COL_NAME = USERS_COL_NAME
        self.FILES_COL_NAME = FILES_COL_NAME

        self.users = self.db['test_users']
        self.files = self.db['test_files']



class mongo_test(unittest.TestCase):
    def test_add_user(self):
        log = 'log1'
        pas = 'pas1'
        mail = 'e@ma.il'

        new = add_user(g, log, hash(pas), mail)
        get = g.users.find_one({'_id':new})
        
        self.assertEqual(get['login'], log)
        self.assertEqual(get['pas'], hash(pas))
        self.assertEqual(get['email'], mail)


    def test_remake_user(self):
        remake_users(g, 'yes')
        size = g.users.count_documents({})

        self.assertEqual(size, 0)


if __name__ == '__main__':
    g = flask_g()
    unittest.main()

