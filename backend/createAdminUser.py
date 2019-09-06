from utils.mango import *
from utils import common
import config as configuration
import pymongo.errors as database_errors

if __name__ == '__main__':
    config = configuration.Config()
    conn, db = connect(config.get_mongo_default_db_name(),
                       ip=config.get_mongo_host(),
                       port=int(config.get_mongo_port()),
                       username=config.get_mongo_username(),
                       password=config.get_mongo_password())

    user_name = 'admin'
    random_pass_word = common.get_random_key()
    nick_name = '系统管理员'

    administrator_info = {
        'username': user_name,
        'password': random_pass_word,
        'nickName': nick_name
    }

    if db['adminUser'].find_one({'username': user_name}):
        print('您已经创建过管理员用户啦! / you have already created adminUser account!')
    else:
        try:
            db['adminUser'].insert(administrator_info)
        except database_errors.DuplicateKeyError as e:
            print('您已经创建过管理员用户啦! / you have already created adminUser account!')
        else:
            print('管理员账号创建成功~ / adminUser has been successfully created~')
            print('username: %s, password: %s' % (user_name, random_pass_word))
            print('请记录并妥善保管好账号密码~ / please take good care of your account~')
