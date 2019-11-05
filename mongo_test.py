from gorbin_tools import *
import unittest
from time import sleep
from config import MONGO_ADDRESS, DB_NAME, USERS_COL_NAME, FILES_COL_NAME, LINKS_COL_NAME

class flask_g():
    def __init__(self):
        client = MongoClient(MONGO_ADDRESS)
        self.db = client[DB_NAME]
        self.MONGO_ADDRESS = MONGO_ADDRESS
        self.DB_NAME = DB_NAME
        self.USERS_COL_NAME = USERS_COL_NAME
        self.FILES_COL_NAME = FILES_COL_NAME
        self.LINKS_COL_NAME = LINKS_COL_NAME

        self.users = self.db['test_users']
        self.files = self.db['test_files']
        self.links = self.db['test_links']


class mongo_test(unittest.TestCase):
    def test_add_user(self):
        log = 'log1'
        pas = 'pas1'
        mail = 'e@ma.il'

        new_user = add_user(g, log, hash(pas), mail)
        get = g.users.find_one({'_id':new_user})
        
        self.assertEqual(get['login'], log)
        self.assertEqual(get['pas'], hash(pas))
        self.assertEqual(get['email'], mail)
        self.assertEqual(get['shared'], [])



        owner = 'log2'
        name = 'name2'
        location = 'C:\\tesk_loc'
        size = 10

        new = add_folder(g, owner, name, size, location)
        get = g.files.find_one({'_id':new})
        NEW = new
        
        self.assertEqual(get['owner'], owner)
        self.assertEqual(get['name'], name)
        self.assertEqual(get['size'], size)
        self.assertEqual(get['location'], location)
        self.assertEqual(get['dir'], '/')
        self.assertEqual(get['shared'], [])

        owner = 'log1'
        name = 'name1'
        location = 'C:\\tesk_loc'
        size = 10
        new = add_file(g, owner, name, size, location, NEW)
        get = g.files.find_one({'_id':new})
        
        self.assertEqual(get['owner'], owner)
        self.assertEqual(get['name'], name)
        self.assertEqual(get['size'], size)
        self.assertEqual(get['location'], location)
        self.assertEqual(get['dir'], NEW)
        self.assertEqual(get['shared'], [])


        lst = [new, NEW]

        link = make_link(g, lst)
        get = g.links.find_one({'_id':link})

        self.assertEqual(get['files'], lst)
        self.assertEqual(get['_id'], link)
        self.assertEqual(get['deleted'], False)
        self.assertEqual(get_linked(g, link), lst)
        self.assertEqual(get_linked(g, '---'), None)

        del_link(g, link)
        self.assertEqual(get_linked(g, link), None)
        self.assertEqual(g.links.find_one({'_id':link})['deleted'], True)

        add_linked(g, new_user, [new, NEW, new, NEW])
        self.assertEqual(get_user_shared(g, new_user), [new, NEW])
        self.assertEqual(get_user_shared(g, new), None)

        del_shared(g, new_user, [new, new])
        self.assertEqual(get_user_shared(g, new_user), [NEW])

        self.assertEqual(check_availability(g, new_user, NEW), True)
        self.assertEqual(check_availability(g, new_user, new), False)





if 0:
    class remake_test(unittest.TestCase):
        def test_remake_users(self):
            remake_users(g, 'yes')
            size = g.users.count_documents({})

            self.assertEqual(size, 0)

        def test_remake_files(self):
            remake_files(g, 'yes')
            size = g.files.count_documents({})

            self.assertEqual(size, 0)

        def test_remake_links(self):
            remake_links(g, 'yes')
            size = g.links.count_documents({})

            self.assertEqual(size, 0)



if __name__ == '__main__':
    g = flask_g()
    remake_users(g, 'yes')
    remake_files(g, 'yes')
    remake_links(g, 'yes')
    unittest.main()

