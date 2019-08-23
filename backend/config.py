import os

env_dist = os.environ


class Config:

    _AUTOTEST_PLATFORM_ENV = env_dist.get('AUTOTEST_PLATFORM_ENV', 'dev')
    _AUTOTEST_PLATFORM_MONGO_HOST = env_dist.get('AUTOTEST_PLATFORM_MONGO_HOST', '127.0.0.1')
    _AUTOTEST_PLATFORM_MONGO_PORT = env_dist.get('AUTOTEST_PLATFORM_MONGO_PORT', '27017')
    _AUTOTEST_PLATFORM_MONGO_USERNAME = env_dist.get('AUTOTEST_PLATFORM_MONGO_USERNAME')
    _AUTOTEST_PLATFORM_MONGO_PASSWORD = env_dist.get('AUTOTEST_PLATFORM_MONGO_PASSWORD')
    _AUTOTEST_PLATFORM_MONGO_DEFAULT_DBNAME = env_dist.get('AUTOTEST_PLATFORM_MONGO_DEFAULT_DBNAME', 'taisite')
    _AUTOTEST_PLATFORM_NLP_SERVER_HOST = env_dist.get('AUTOTEST_PLATFORM_NLP_SERVER_HOST', '127.0.0.1')
    _AUTOTEST_PLATFORM_SECRET_KEY = env_dist.get(
        'AUTOTEST_PLATFORM_SECRET_KEY',
        b'\xc2\xf6\xbeK\xa5\xa74\x05\xce\t\xdb\t\xdc\x12\xe9\x82\xa3\xaaw\xb0\xa3~\x93J')

    def get_env(self):
        return self._AUTOTEST_PLATFORM_ENV

    def set_env(self, env):
        self._AUTOTEST_PLATFORM_ENV = env

    def get_mongo_host(self):
        return self._AUTOTEST_PLATFORM_MONGO_HOST

    def set_mongo_host(self, host):
        self._AUTOTEST_PLATFORM_MONGO_HOST = host

    def get_nlp_server_host(self):
        return self._AUTOTEST_PLATFORM_NLP_SERVER_HOST

    def set_nlp_server_host(self, host):
        self._AUTOTEST_PLATFORM_NLP_SERVER_HOST = host

    def get_mongo_port(self):
        return self._AUTOTEST_PLATFORM_MONGO_PORT

    def set_mongo_port(self, port):
        self._AUTOTEST_PLATFORM_MONGO_PORT = port

    def get_mongo_username(self):
        return self._AUTOTEST_PLATFORM_MONGO_USERNAME

    def set_mongo_username(self, username):
        self._AUTOTEST_PLATFORM_MONGO_USERNAME = username

    def get_mongo_password(self):
        return self._AUTOTEST_PLATFORM_MONGO_PASSWORD

    def set_mongo_password(self, password):
        self._AUTOTEST_PLATFORM_MONGO_PASSWORD = password

    def get_mongo_default_db_name(self):
        return self._AUTOTEST_PLATFORM_MONGO_DEFAULT_DBNAME

    def set_mongo_default_db_name(self, db_name):
        self._AUTOTEST_PLATFORM_MONGO_DEFAULT_DBNAME = db_name

    def get_secret_key(self):
        return self._AUTOTEST_PLATFORM_SECRET_KEY

    def set_secret_key(self, secret_key):
        self._AUTOTEST_PLATFORM_SECRET_KEY = secret_key


if __name__ == '__main__':
    config = Config()
    print('AUTOTEST_PLATFORM_ENV: ----------> %s' % config.get_env())
    print('AUTOTEST_PLATFORM_MONGO_HOST: ----------> %s' % config.get_mongo_host())
    print('AUTOTEST_PLATFORM_MONGO_PORT: ----------> %s' % config.get_mongo_port())
    print('AUTOTEST_PLATFORM_NLP_SERVER_HOST: ----------> %s' % config.get_nlp_server_host())
    print('AUTOTEST_PLATFORM_MONGO_USERNAME: ----------> %s' % config.get_mongo_username())
    print('AUTOTEST_PLATFORM_MONGO_PASSWORD: ----------> %s' % config.get_mongo_password())
    print('AUTOTEST_PLATFORM_MONGO_DEFAULT_DBNAME: ----------> %s' % config.get_mongo_default_db_name())
    print('AUTOTEST_PLATFORM_SECRET_KEY: ----------> %s' % config.get_secret_key())
