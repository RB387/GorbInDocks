from gorbin_tools2 import *
import unittest
from time import sleep
from config import MONGO_ADDRESS, DB_NAME, USERS_COL_NAME, FILES_COL_NAME, LINKS_COL_NAME
from pprint import pprint
from os import path, getcwd

class flask_g():
    def __init__(self):
        pass

class begin_remake_test(unittest.TestCase):
    def test1_remake_users(self):
        mt.remake_users('yes')
        size = g.users.count_documents({})

        self.assertEqual(size, 0)

    def test2_remake_files(self):
        mt.remake_files('yes')
        size = g.files.count_documents({})

        self.assertEqual(size, 0)


class mongo_tests(unittest.TestCase):
    def test1_add_simple_user(self):
        self.maxDiff = 1500
        log, pas, mail, status = 'Alina', 'Foxyasha', 'My@cool.sun', 'simple'

        new_simp_user = mt.add_user(log, hash(pas), mail)
        real_get = g.users.find_one({'_id':new_simp_user})

        self.assertEqual(real_get['login'], log)
        self.assertEqual(real_get['pas'], hash(pas))
        self.assertEqual(real_get['email'], mail)
        self.assertEqual(real_get['status'], 'simple')
        self.assertEqual(real_get['deleted'], False)
        
    def test2_add_admin_user(self):
        self.maxDiff = 1500
        log, pas, mail, status = 'Faralaks', 'AlinaLove', 'iam@the.best', 'admin'

        new_admin_user = mt.add_user(log, hash(pas), mail, status)
        real_get = g.users.find_one({'_id':new_admin_user})
        
        self.assertEqual(real_get['login'], log)
        self.assertEqual(real_get['pas'], hash(pas))
        self.assertEqual(real_get['email'], mail)
        self.assertEqual(real_get['status'], status)
        self.assertEqual(real_get['deleted'], False)

    def test31_get_simple_users_false(self):
        self.maxDiff = 1500
        users = [g.users.find_one({'login':'Alina'})]

        func_get = mt.get_simple_users()

        self.assertEqual(users, func_get)

    def test3_get_user(self):
        self.maxDiff = 1500
        log, pas, mail, status = 'Misha', 'DinoMan', 'Misha@mail.ru', 'simple'

        new_user = mt.add_user(log, hash(pas), mail, status)
        real_get = g.users.find_one({'_id':new_user})
        func_get = mt.get_user(log, hash(pas))

        self.assertEqual(real_get['login'], func_get['login'])
        self.assertEqual(real_get['pas'], func_get['pas'])
        self.assertEqual(real_get['status'], func_get['status'])
        self.assertEqual(real_get['deleted'], func_get['deleted'])

    def test4_login_email_existing(self):
        self.maxDiff = 1500
        log, pas, mail, status = 'Masha', 'macdonalds', 'car@gmail.com', 'simple'

        new_user = mt.add_user(log, hash(pas), mail, status)
        owner = g.users.find_one({'login':"Masha"})['_id']
        self.assertEqual(mt.check_login(log), True)
        self.assertEqual(mt.check_email(mail), True)
        self.assertEqual(mt.check_login('nologin'), False)
        self.assertEqual(mt.check_email('nomail'), False)

    def test5_update_user(self):
        self.maxDiff = 1500
        log, pas, mail, status = 'Nastya_Kuz', 'broken_nose', 'foXisCool@hotmail.com', 'admin'
        new_log, new_pas, new_mail = 'Nastya_Bas', 'workISgood', 'goodby_vuz@narod.ru'

        new_user = mt.add_user(log, hash(pas), mail, status)
        mt.update_user(new_user, new_log, hash(new_pas), new_mail)
        real_get = g.users.find_one({'_id':new_user})
        func_get = mt.get_user(new_log, hash(new_pas))

        self.assertEqual(real_get['login'], func_get['login'])
        self.assertEqual(real_get['pas'], func_get['pas'])
        self.assertEqual(real_get['status'], func_get['status'])
        self.assertEqual(real_get['deleted'], func_get['deleted'])

    def test6_del_user(self):
        self.maxDiff = 1500
        log, pas, mail, status = 'Gleb', 'help_me', 'ne_idu@v.vuz', 'simple'
        log2, pas2, mail2 = 'Gleb_Snova', 'Gde_VUZ?', 'sessiu@ne.sdam'

        new_user = mt.add_user(log, hash(pas), mail, status)
        new_user2 = mt.add_user(log2, hash(pas2), mail2, status)
        mt.del_user(user_id=new_user)
        mt.del_user(login=log2)
        real_get = g.users.find_one({'_id':new_user})
        real_get2 = g.users.find_one({'_id':new_user2})
        func_get = mt.get_user(log, hash(pas))
        func_get2 = mt.get_user(log2, hash(pas2))

        self.assertEqual(real_get['deleted'], True)
        self.assertEqual(real_get2['deleted'], True)
        self.assertEqual(func_get, None)
        self.assertEqual(func_get2, None)

    def test71_get_simple_users_true(self):
        self.maxDiff = 1500
        users = [g.users.find_one({'login':'Gleb'}), g.users.find_one({'login':'Gleb_Snova'})]

        func_get = mt.get_simple_users(True)

        self.assertEqual(users, func_get)
    
    def test7_add_file(self):
        self.maxDiff = 1500
        owner = g.users.find_one({'login':'Alina'})['_id']
        name, size, location = 'Kafeshka', 1, '/u_vuza' 

        new_file = mt.add_file(owner, name, size, location)
        real_get = g.files.find_one({'_id':new_file})

        self.assertEqual(real_get['owner'], owner)
        self.assertEqual(real_get['name'], name)
        self.assertEqual(real_get['size'], size)
        self.assertEqual(real_get['location'], location)
        self.assertEqual(real_get['dir'], '/')
        self.assertEqual(real_get['comment'], None)
        self.assertEqual(real_get['tags'], [])
        self.assertEqual(real_get['deleted'], False)

    def test8_add_folder(self):
        self.maxDiff = 1500
        owner = g.users.find_one({'login':'Alina'})['_id']
        name, size, location, comment = 'Metro', 2033, '/u_alinbI', 'tupie avtobusi, dazdravstvuet metro' 

        new_file = mt.add_folder(owner, name, size, location, comment=comment)
        real_get = g.files.find_one({'_id':new_file})

        self.assertEqual(real_get['owner'], owner)
        self.assertEqual(real_get['name'], name)
        self.assertEqual(real_get['size'], size)
        self.assertEqual(real_get['location'], location)
        self.assertEqual(real_get['dir'], '/')
        self.assertEqual(real_get['comment'], comment)
        self.assertEqual(real_get['tags'], [])
        self.assertEqual(real_get['deleted'], False)
        
    def test9_add_file_inside(self):
        self.maxDiff = 1500
        owner = g.users.find_one({'login':'Alina'})['_id']
        directory = g.files.find_one({'name':'Metro'})['_id']
        name, size, location, tags = 'Dom_AlinbI', 576, '/u_alinbi/metro', ['daleko', 'ot', 'moskvbI'] 

        new_file = mt.add_file(owner, name, size, location, directory, tags=tags)
        real_get = g.files.find_one({'_id':new_file})

        self.assertEqual(real_get['owner'], owner)
        self.assertEqual(real_get['name'], name)
        self.assertEqual(real_get['size'], size)
        self.assertEqual(real_get['location'], location)
        self.assertEqual(real_get['dir'], str(directory))
        self.assertEqual(real_get['comment'], None)
        self.assertEqual(real_get['tags'], tags)
        self.assertEqual(real_get['deleted'], False)
        
    def testa_update_file(self):
        self.maxDiff = 1500
        owner = g.users.find_one({'login':'Misha'})['_id']
        name, size, location, comment, tags = 'Pukan_Gorit', 6, '/Matan', 'zachem nam eto nuzno?', ['pamagite'] 
        new_name, new_size, new_tags = 'Pukan_Gorit', 9, ['param_konec']

        new_file = mt.add_file(owner, name, size, location, comment=comment, tags=tags)
        mt.update_file(new_file, new_name, new_size, comment, new_tags)
        real_get = g.files.find_one({'_id':new_file})

        self.assertEqual(real_get['owner'], owner)
        self.assertEqual(real_get['name'], new_name)
        self.assertEqual(real_get['size'], new_size)
        self.assertEqual(real_get['location'], location)
        self.assertEqual(real_get['dir'], '/')
        self.assertEqual(real_get['comment'], comment)
        self.assertEqual(real_get['tags'], new_tags)
        self.assertEqual(real_get['deleted'], False)

    def testb_get_file(self):
        self.maxDiff = 1500
        owner = g.users.find_one({'login':'Faralaks'})['_id']
        name, size, location, comment  = 'Vladya', 1, '/Alina', 'Kto kogo eshche vozmet!'

        new_file = mt.add_file(owner, name, size, location, comment=comment)
        real_get = g.files.find_one({'_id':new_file})
        func_get = mt.get_file(new_file)

        self.assertEqual(real_get['owner'], func_get['owner'])
        self.assertEqual(real_get['name'], func_get['name'])
        self.assertEqual(real_get['size'], func_get['size'])
        self.assertEqual(real_get['location'], func_get['location'])
        self.assertEqual(real_get['dir'], func_get['dir'])
        self.assertEqual(real_get['comment'], func_get['comment'])
        self.assertEqual(real_get['tags'], func_get['tags'])
        self.assertEqual(real_get['deleted'], func_get['deleted'])

    def testc_check_file(self):
        self.maxDiff = 1500
        owner = g.users.find_one({'login':'Masha'})['_id']
        owner2 = g.users.find_one({'login':'Misha'})['_id']
        name, size, location, comment  = 'Dengi', 0, '/Koshelek', 'Ne idu v mak:('

        new_file = mt.add_file(owner, name, size, location, comment=comment)

        self.assertEqual(mt.check_file(owner, name), True)
        self.assertEqual(mt.check_file(owner, 'Mnogo_deneg'), False)
        self.assertEqual(mt.check_file(owner2, name), False)

    def testd_del_file(self):
        self.maxDiff = 1500
        owner = g.users.find_one({'login':'Faralaks'})['_id']
        name, size, location  = 'Microvolnovka', 1, '/vuz/stolovaya'

        new_file = mt.add_file(owner, name, size, location)
        mt.del_file(new_file)
        real_get = g.files.find_one({'_id':new_file})

        self.assertEqual(mt.check_file(owner, name), False)
        self.assertEqual(real_get['deleted'], True)

    def teste_get_user_files(self):
        self.maxDiff = 1500
        owner = g.users.find_one({'login':'Alina'})['_id']
        directory = g.files.find_one({'name':'Metro'})['_id']
        name, size, location  = 'Dom_Foxyashi', 1, '/u_alinbi/metro'

        new_file = mt.add_file(owner, name, size, location, directory=directory)
        real_get = list(g.files.find({'location':'/u_alinbi/metro'}))

        self.assertEqual(mt.get_user_files(owner, directory), real_get)

    def testf_add_comment_tags(self):
        self.maxDiff = 1500
        owner = g.users.find_one({'login':'Misha'})['_id']
        name, size, location, comment, tags  = 'wow', 835, '/blizzard/wow', 'Umiraet', ['minecraft', 'jivet', 'vechno']

        new_file = mt.add_file(owner, name, size, location)
        mt.add_comment(new_file, comment)
        mt.add_tags(new_file, tags)
        real_get = g.files.find_one({'_id':new_file})
        
        self.assertEqual(real_get['comment'], comment)
        self.assertEqual(real_get['tags'], tags)

    def testg_del_tags(self):
        self.maxDiff = 1500
        old_file = g.files.find_one({'name':'wow'})['_id']
        tags  = ['vechno']

        mt.del_tags(old_file, tags)
        real_get = g.files.find_one({'_id':old_file})
        
        self.assertEqual(real_get['tags'], ['minecraft', 'jivet'])


    def testq_get_simple_users_false(self):
        self.maxDiff = 1500
        users = list(g.users.find({'status':'simple'}))

        func_get = mt.get_simple_users('all')

        self.assertEqual(users, func_get)


class remake_test_end(unittest.TestCase):
    def test1_remake_users(self):
        mt.remake_users('yes')
        size = g.users.count_documents({})

        self.assertEqual(size, 0)

    def test2_remake_files(self):
        mt.remake_files('yes')
        size = g.files.count_documents({})

        self.assertEqual(size, 0)


if __name__ == '__main__':
    g = flask_g()
    mt = mongo_tools(g)

    unittest.main()