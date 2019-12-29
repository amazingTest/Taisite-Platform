# mongo的ORM库
# 宗旨：
# API尽量贴合mongo原生pymongo
# 转换pymongo的字典为对象
# 具有简单的校验，
# 可管理index

from pymongo import MongoClient, errors
from bson import ObjectId
import datetime
from utils import common

global connection
global db
connection = None
db = None

# ****** connect *******


def connect(
    database,
    ip='127.0.0.1',
    port=27017,
    username=None,
    password=None,
):
    global connection, db
    connection = MongoClient(
        ip,
        port,
    )
    if username and password:
        connection.admin.authenticate(username, password)
    db = connection.get_database(database)
    return connection, db

# ****** Fields ******


class Field(object):
    _type = object

    def __init__(self, field_name=None, index=False, unique=False, default=None, expected_structure=None):
        self.name = field_name
        self.index = index
        self.unique = unique
        self.expected_structure = expected_structure
        if self.expected_structure:
            self.default = default if Field.is_data_valid(self.expected_structure, default) else None
        else:
            self.default = default

    def __str__(self):
        return self.name

    def field_assert(self, value, name='?'):
        if not isinstance(value, self._type) and not isinstance(value, type(None)):
            raise TypeError('document.{} given not match the field "{}". It\'s class is "{}"'
                            .format(name, self.__class__.__name__, value.__class__.__name__))
        if self.expected_structure and isinstance(self.expected_structure, dict):
            is_valid = Field.is_data_valid(self.expected_structure, value)
            if not is_valid:
                raise TypeError('document.{} given not match the structure "{}"'
                                .format(name, self.expected_structure))

    # 判断 pre_validate_data 符不符合给定的 expected_structure
    @staticmethod
    def is_data_valid(expected_structure, pre_validate_data):
        if not isinstance(expected_structure, dict) or not expected_structure:
            raise TypeError('expected_structure must be valid dict')
        expected_type_range = expected_structure.get('expectedTypeRange')
        if not expected_type_range:
            return True
        expected_value_range = expected_structure.get('expectedValueRange')\
            if expected_structure.get('expectedValueRange') else []
        expected_dict = expected_structure.get('expectedDict') if expected_structure.get('expectedDict') else {}
        if not all(map(lambda x: isinstance(x, type), expected_type_range)) \
                or not isinstance(expected_value_range, list) or not isinstance(expected_dict, dict):
            raise TypeError('expectedType、 expectedRange、 expectedDict  must be type_list、 list、dict ')
        if not type(pre_validate_data) in expected_type_range:
            return False
        if isinstance(pre_validate_data, list):
            for list_piece in pre_validate_data:
                if expected_value_range and not any(map(Field.is_data_valid, expected_value_range,
                                                        common.x2list(len(expected_value_range), list_piece))):
                    return False
        elif isinstance(pre_validate_data, dict):
            for k, v in expected_dict.items():
                if k not in pre_validate_data or not Field.is_data_valid(v, pre_validate_data[k]):
                    return False
        return True

    def get_type(self):
        return self._type

    def set_name(self, name):
        self.name = name


class IntField(Field):
    _type = int


class FloatField(Field):
    _type = float


class StringField(Field):
    _type = str


class ListField(Field):
    _type = list


class DictField(Field):
    _type = dict


class BooleanField(Field):
    _type = bool


class ArrayField(Field):
    _type = list


class ObjectIdField(Field):
    _type = type(ObjectId())


class DateField(Field):
    _type = type(datetime.datetime.utcnow())

# ****** Model Funcs ******

def cls_method_creater(func_name):
    '直接生成pymongo原生方法的包装类方法'
    @classmethod
    def func(cls, *args, **kargs):
        # args[0]为插入字段时，做替换，清除未声明的field
        if func_name in ['insert', 'create']:
            args = (cls.filter_field(args[0]),) + args[1:]
        else:
            cls.filter_field(args[0])
        func_real = getattr(db[cls.Meta.collection], func_name)
        returned = func_real(*args, **kargs)
        return returned
    return func

@classmethod
def find(cls, *args, **kargs):
    cursor = db[cls.Meta.collection].find(*args, **kargs)
    # 可以实现直接返回Model对象，但这样返回字典手动转换，更灵活
    return cursor

@classmethod
def find_one(cls, *args, **kargs):
    data_dict = db[cls.Meta.collection].find_one(*args, **kargs)
    return data_dict

@classmethod
def insert(cls, *args, **kargs):
    args = (cls.filter_field(args[0]),) + args[1:]
    _id = db[cls.Meta.collection].insert(*args, **kargs)
    return _id

@classmethod
def create(cls, **kargs):
    kargs = cls.filter_field(kargs)
    _id = db[cls.Meta.collection].insert(kargs)
    return _id

@classmethod
def update(cls, *args, **kargs):
    # cls.filter_field(args[0])
    # TODO pymongo的update使用多重字典，无法直接做检查
    returned = db[cls.Meta.collection].update(*args, **kargs)
    return returned

@classmethod
def remove(cls, *args, **kargs):
    # cls.filter_field(args[0])
    # TODO pymongo的remove使用多重字典，无法直接做检查
    returned = db[cls.Meta.collection].remove(*args, **kargs)
    return returned


# ****** Model ******

class Model(object):
    find = find
    find_one = find_one
    insert = cls_method_creater('insert')
    create = create
    update = cls_method_creater('update')
    remove = cls_method_creater('remove')
    insert_many = cls_method_creater('insert_many')
    insert_one = cls_method_creater('insert_one')
    index_information = cls_method_creater('index_information')
    update_many = cls_method_creater('update_many')
    ensure_index = cls_method_creater('ensure_index')
    drop_indexes = cls_method_creater('drop_indexes')
    drop_index = cls_method_creater('drop_index')
    delete_one = cls_method_creater('delete_one')
    delete_many = cls_method_creater('delete_many')
    create_indexes = cls_method_creater('create_indexes')
    create_index = cls_method_creater('create_index')
    count = cls_method_creater('count')
    aggregate = cls_method_creater('aggregate')

    class Meta:
        strict = False
        collection = None
        index = None
        database = db

    # Python3.6及以上
    def __init_subclass__(subcls, **kargs):
        subcls.Meta.collection = subcls.Meta.collection if hasattr(subcls.Meta, 'collection') else subcls.__name__.lower()
        collection = subcls.Meta.database[subcls.Meta.collection]
        # print(dir(collection))
        if hasattr(subcls.Meta, 'index'):
            for index in subcls.Meta.index:
                try:
                    collection.create_index([index])
                except errors.OperationFailure:
                    pass
        for attr_name in dir(subcls):
            field = getattr(subcls, attr_name)
            if isinstance(field, Field):
                try:
                    if field.unique:
                        collection.create_index([(attr_name, -1 if field.index == -1 else 1)], unique=True)
                    elif field.index:
                        collection.create_index([(attr_name, -1 if field.index == -1 else 1)])
                except errors.OperationFailure:
                    pass

    def __init__(self, *args, **kargs):
        if args and not kargs and type(args[0]) == dict:
            dict_data = args[0]
            kargs = (lambda **kargs: kargs)(**dict_data)
        # print(dir(self))
        for attr_name in dir(self):
            # print('1: %s' % attr_name)
            field = self.__getitem__(attr_name)
            if isinstance(field, Field):
                if not field.name:
                    field.set_name(attr_name)
                if attr_name in kargs:
                    kargs_v = kargs[attr_name]
                    field.field_assert(kargs_v, attr_name)
                    self.__setitem__(attr_name, kargs_v)
                else:
                    if hasattr(self.__class__.Meta, 'strict') and self.__class__.Meta.strict:
                        raise AttributeError('Model.{} not exists in real document'.format(attr_name))
                    else:
                        self.__setitem__(attr_name, None)


    def __getitem__(self, k):
        # import traceback
        # s = traceback.extract_stack()
        # print ('%s Invoked me!' % s[-2][2])
        # print(k)
        return getattr(self, k)


    def __setitem__(self, k, v):
        setattr(self, k, v)

    @classmethod
    def dict2obj(cls, data_dict):
        return cls(**data_dict)

    @classmethod
    def filter_field(cls, field_dict, use_set_default=False):
        new_dict = {}
        if use_set_default:
            for attr_name in dir(cls):
                field = getattr(cls, attr_name)
                if isinstance(field, Field):
                    if field.default is not None and field.name is not None:
                        new_dict[field.name] = field.default
        for key in field_dict: # 执行这步的时候报错
            val = field_dict[key]
            if not hasattr(cls, key) or not isinstance(getattr(cls, key), Field):
                continue
            getattr(cls, key).field_assert(val, key)
            new_dict[key] = val
        return new_dict
