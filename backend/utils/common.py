import datetime
from bson import ObjectId
import random
import copy
import re
import ast
import time
from dateutil import tz
import pymongo
from utils.sendReportEmail import send_report_email
from tzlocal import get_localzone
import string


def get_offset_between_local_and_utc():
    ts = time.time()
    utc_offset = int((datetime.datetime.fromtimestamp(ts) - datetime.datetime.utcfromtimestamp(ts)).total_seconds() / 3600)
    return utc_offset


def get_offset_between_shanghai_and_utc():
    # localzone = get_localzone()
    shanghai_tz = tz.gettz('Asia/Shanghai')
    utc_tz = tz.tzutc()
    date_time_utc_now = datetime.datetime.utcnow()
    date_time_local_now = date_time_utc_now.astimezone(tz=utc_tz)
    date_time_shanghai_now = date_time_local_now.astimezone(tz=shanghai_tz)
    local_utc_offset = int(date_time_local_now.utcoffset().total_seconds() / 3600)
    shanghai_utc_offset = int(date_time_shanghai_now.utcoffset().total_seconds() / 3600)
    shanghai_local_offset = shanghai_utc_offset - local_utc_offset
    return shanghai_local_offset


def format_response_in_dic(dic, is_format_object_id=True, is_format_datetime=True, is_filter_isDeleted=True, timedelta=None):
    if timedelta is None:
        timedelta = get_offset_between_local_and_utc()
    if not isinstance(dic, dict):
        raise ValueError("input must be a dict!")
    if is_filter_isDeleted:
        if 'isDeleted' in dic and dic["isDeleted"] is True:
            return None
    if is_format_datetime:
        for key, value in dic.items():
            if isinstance(value, dict):
                dic[key] = format_response_in_dic(value)
            if isinstance(value, list):
                for index, value_piece in enumerate(value):
                    if isinstance(value_piece, dict):
                        value_piece = format_response_in_dic(value_piece)
                        value[index] = value_piece
                    elif isinstance(value_piece, datetime.datetime):
                        local_time = (value_piece + datetime.timedelta(hours=timedelta))
                        time_text = local_time.strftime('%Y-%m-%d %H:%M:%S')
                        value[index] = time_text
            if isinstance(value, datetime.datetime):
                local_time = (value + datetime.timedelta(hours=timedelta))
                time_text = local_time.strftime('%Y-%m-%d %H:%M:%S')
                dic[key] = time_text
    if is_format_object_id:
        for key, value in dic.items():
            if isinstance(value, dict):
                dic[key] = format_response_in_dic(value)
            if isinstance(value, list):
                for index, value_piece in enumerate(value):
                    if isinstance(value_piece, dict):
                        value_piece = format_response_in_dic(value_piece)
                        value[index] = value_piece
                    elif isinstance(value_piece, ObjectId):
                        value[index] = str(value_piece)
            if isinstance(value, ObjectId):
                dic[key] = str(value)
    return dic


def get_object_id(from_datetime=None, span_days=0, span_hours=0, span_minutes=0, span_weeks=0):
    '''根据时间手动生成一个objectid，此id不作为存储使用'''
    if not from_datetime:
        from_datetime = datetime.datetime.now()
    from_datetime = from_datetime + datetime.timedelta(days=span_days,
                                                       hours=span_hours,
                                                       minutes=span_minutes,
                                                       weeks=span_weeks)
    return ObjectId.from_datetime(generation_time=from_datetime)


def can_convert_to_int(input):
    try:
        int(input)
        return True
    except BaseException:
        return False


def can_convert_to_str(input):
    try:
        str(input)
        return True
    except BaseException:
        return False


def can_convert_to_float(input):
    try:
        float(input)
        return True
    except BaseException:
        return False


re_escapes = ['\\', '/', '*', '.', '?', '+', '$', '^', '[', ']', '(', ')', '{', '}', '|']


def format_escapes(input, escapes=re_escapes):
    if not isinstance(input, str):
        return input
    else:
        for escape in escapes:
            input = input.replace(escape, '\\' + escape)
        return input


def format_order(raw_order):
    if not isinstance(raw_order, str):
        raise TypeError('raw_order must be str!')
    if 'desc' in raw_order:
        return -1
    elif 'asc' in raw_order:
        return 1
    else:
        return None


def format_js_dic_to_python_dic(query_dic):
    if not isinstance(query_dic, dict):
        raise TypeError('query_dic must be dict')
    for key, value in query_dic.items():
        if value == 'true':
            query_dic[key] = True
        if value == 'false':
            query_dic[key] = False
        if str(key)[-2:] == 'Id':
            query_dic[key] = ObjectId(value)
        if str(key) == '_id':
            try:
                query_dic[key] = ObjectId(value)
            except BaseException as e:
                print(e)
    return query_dic


def get_total_num_and_arranged_data(raw_model, query_dic, fuzzy_fields=None):
    query_dic = query_dic.to_dict() if query_dic.to_dict() else {}
    if fuzzy_fields is not None:
        if not isinstance(fuzzy_fields, list):
            raise TypeError('fuzzy_fields need to be list.')
        for fuzzy_field in fuzzy_fields:
            if not isinstance(fuzzy_field, str):
                raise TypeError('fuzzy_field need to be str')
            if fuzzy_field in query_dic and can_convert_to_str(query_dic[fuzzy_field]):
                pre_compiled_str = format_escapes(str(query_dic[fuzzy_field]))
                query_dic[fuzzy_field] = re.compile(pre_compiled_str)
    query_dic = format_js_dic_to_python_dic(query_dic)
    raw_model_copy = copy.deepcopy(raw_model)
    raw_model_data_copy = []

    if not isinstance(raw_model_copy.find(), list):
        try:
            raw_model_data_copy = list(raw_model_copy.find({'isDeleted': {"$ne": True}}))
        except BaseException as e:
            raise TypeError('raw_data cannot convert to list: %s' % e)
    if not isinstance(query_dic, dict):
        raise TypeError('query_dic must be dict')

    skip = int(query_dic.get('skip')) if can_convert_to_int(query_dic.get('skip')) else 0
    size = int(query_dic.get('size')) if can_convert_to_int(query_dic.get('size')) else None
    sort_by = query_dic.get('sortBy')
    order = query_dic.get('order')

    query_dic.pop('skip') if query_dic.get('skip') else None
    query_dic.pop('size') if query_dic.get('size') else None
    query_dic.pop('sortBy') if query_dic.get('sortBy') else None
    query_dic.pop('order') if query_dic.get('order') else None

    if not query_dic == {}:
        query_dic['isDeleted'] = {"$ne": True}
        total_num = len(list(raw_model_copy.find(query_dic)))
    else:
        total_num = len(raw_model_data_copy)
    if sort_by and order and format_order(order):
        sort_query = [(sort_by, format_order(order))]
    else:
        sort_query = None
    query_dic['isDeleted'] = {"$ne": True}

    if skip is 0 and not size:
        if sort_query:
            arranged_data = raw_model_copy.find(query_dic, sort=sort_query)
        else:
            arranged_data = raw_model_copy.find(query_dic)
    else:
        if sort_query:
            arranged_data = raw_model_copy.find(query_dic).sort(sort_query).skip(skip).limit(size)
        else:
            arranged_data = raw_model_copy.find(query_dic).skip(skip).limit(size)

    return total_num, list(map(format_response_in_dic, map(raw_model_copy.filter_field, arranged_data)))


def dict_get(dic, locators, default=None):

    '''

    :param dic: 输入需要在其中取值的原始字典 <dict>
    :param locators: 输入取值定位器, 如:['result', 'msg', '-1', 'status'] <list>
    :param return_str: 是否将返回值转化成str类型 <bool>
    :param default: 进行取值中报错时所返回的默认值 (default: None)
    :return: 返回根据参数locators找出的值

    '''

    if not isinstance(dic, dict):
        if isinstance(dic, str) and len(locators) == 1 and is_slice_expression(locators[0]):
            slice_indexes = locators[0].split(':')
            start_index = int(slice_indexes[0]) if slice_indexes[0] else None
            end_index = int(slice_indexes[-1]) if slice_indexes[-1] else None
            value = dic[start_index:end_index]
            return value
        return default

    if dic == {} or len(locators) < 1:
        return str(dic)  # 用于后续 re.search

    value = None

    for locator in locators:
        locator = locator.replace(' ', '').replace('\n', '').replace('\t', '')
        if not type(value) in [dict, list] and isinstance(locator, str) and not is_slice_expression(locator):
            try:
                value = dic[locator]
            except KeyError:
                return default
            continue
        if isinstance(value, str) and is_slice_expression(locator):
            try:
                slice_indexes = locator.split(':')
                start_index = int(slice_indexes[0]) if slice_indexes[0] else None
                end_index = int(slice_indexes[-1]) if slice_indexes[-1] else None
                value = value[start_index:end_index]
            except KeyError:
                return default
            continue
        if isinstance(value, dict):
            try:
                value = dict_get(value, [locator])
            except KeyError:
                return default
            continue
        if isinstance(value, list) and len(value) > 0:
            if can_convert_to_int(locator):
                try:
                    value = value[int(locator)]
                except IndexError:
                    return default
                continue
            elif is_specific_search_by_dict_value(locator) and all([isinstance(v, dict) for v in value]):
                first_equal_index = locator.index('=')
                last_dot_index = locator.rindex('.')
                matched_key_re = locator[:first_equal_index]  # 字典中存在满足的正则条件的键
                matched_value_re = locator[first_equal_index + 1:last_dot_index]  # matched_key对应的值需要满足的正则条件
                needed_value_key = locator[last_dot_index + 1:]  # 满足正则条件的字典中待取的值的键

                for dic in value:
                    for k, v in dic.items():
                        if re.match(matched_key_re, str(k)) and re.match(matched_value_re, str(v)):
                            needed_value = dic.get(needed_value_key)
                            value = needed_value
                            break
                    else:
                        continue
                    break
                else:
                    return default

                continue
            elif locator == 'random':
                try:
                    value = value[random.randint(0, len(value) - 1)]
                except IndexError:
                    return default
                continue

    return value


def is_specific_search_by_dict_value(expression):
    if re.match(r'(.)+=(.)+\.(.)+', expression):
        return True
    else:
        return False


def is_slice_expression(expression):
    if re.match('(-?\d+)?:(-?\d+)?', expression):
        return True
    else:
        return False


def resolve_global_var(pre_resolve_var, global_var_dic, global_var_regex='\${.*?}',
                       match2key_sub_string_start_index=2, match2key_sub_string_end_index=-1):

    '''
    :param pre_resolve_var: 准备进行解析的变量<str>
    :param global_var_dic: 全局变量字典<dict>
    :param global_var_regex: 识别全局变量正则表达式<str>
    :param match2key_sub_string_start_index: 全局变量表达式截取成全局变量字典key值字符串的开始索引<int>
    :param match2key_sub_string_end_index: 全局变量表达式截取为成局变量字典key值字符串的结束索引<int>
    :return: 解析后的变量<str>
    '''

    if not isinstance(pre_resolve_var, str):
        raise TypeError('pre_resolve_var must be str！')

    if not isinstance(global_var_dic, dict):
        raise TypeError('global_var_dic must be dict！')

    if not isinstance(global_var_regex, str):
        raise TypeError('global_var_regex must be str！')

    if not isinstance(match2key_sub_string_start_index, int):
        raise TypeError('match2key_sub_string_start_index must be int！')

    if not isinstance(match2key_sub_string_end_index, int):
        raise TypeError('match2key_sub_string_end_index must be int！')

    re_global_var = re.compile(global_var_regex)

    def global_var_repl(match_obj):
        start_index = match2key_sub_string_start_index
        end_index = match2key_sub_string_end_index
        match_value = global_var_dic.get(match_obj.group()[start_index:end_index])
        # 将一些数字类型转成str，否则re.sub会报错, match_value可能是0！
        match_value = str(match_value) if match_value is not None else match_value
        return match_value if match_value else match_obj.group()

    resolved_var = re.sub(pattern=re_global_var, string=pre_resolve_var, repl=global_var_repl)
    return resolved_var


# {'firstArg': '2', 'operator': '-', 'secondArg': '1', 'judgeCharacter': '<', 'expectResult': '1'}
def get_numbers_compared_result(expression):
    '''

    :param expression: for example: {'firstArg': '2', 'operator': '-', 'secondArg': '1', 'judgeCharacter': '<', 'expectResult': '1'} <dic>
    :return: <boolean>
    '''
    if not isinstance(expression, dict):
        raise TypeError('表达式必须是字典类型!')
    if not can_convert_to_float(expression.get('firstArg')) or not can_convert_to_float(expression.get('secondArg')) \
            or not can_convert_to_float(expression.get('expectResult')):
        raise TypeError('数值一: 「%s」 、 数值二: 「%s」 、 期待结果: 「%s」 必须全部为数字!'
                        % (expression.get('firstArg'), expression.get('secondArg'), expression.get('expectResult')))
    if not expression.get('operator') in ['+', '-', '*', '/']:
        raise TypeError('运算符不合法!')
    if not expression.get('judgeCharacter') in ['<', '>', '<=', '>=', '==']:
        raise TypeError('判断符不合法!')

    first_arg = expression.get('firstArg')
    operator = expression.get('operator')
    second_arg = expression.get('secondArg')
    judge_character = expression.get('judgeCharacter')
    expect_result = expression.get('expectResult')

    expression_str = "{}{}{}{}{}".format(first_arg, operator, second_arg, judge_character, expect_result)
    result = eval(expression_str)
    returned_expression_str = expression_str.replace('==', '=')  # TODO 暂时无任何后遗症

    return returned_expression_str, result


def frontend_date_str2datetime(input_str, timedelta=None):
    if timedelta is None:
        timedelta = get_offset_between_local_and_utc()
    pre_date_str = input_str
    #  2019-04-23T16:00:00.000Z  ->  2019-04-23T16:00:00
    if '.' in input_str:
        pre_date_str = pre_date_str[0:input_str.rindex('.')]
    #  input_str -> datetime
    try:
        try:
            date_time = datetime.datetime.strptime(pre_date_str, "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(hours=timedelta)
            return date_time
        except BaseException:
            date_time = datetime.datetime.strptime(pre_date_str, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(
                hours=timedelta)
            return date_time
    except BaseException as e:
        raise TypeError('字符串转日期格式失败！ : %s' % e)


def is_valid_email(email):
    re_email = re.compile(r'^[a-zA-Z0-9\.]+@[a-zA-Z0-9]+\.[a-zA-Z]{3}$')
    if re_email.match(email):
        return True
    else:
        return False


def time_stamp2str(time_stamp, timedelta=None):
    if timedelta is None:
        timedelta = get_offset_between_local_and_utc()
    try:
        if not time_stamp:
            return ''
        local_time = datetime.datetime.utcfromtimestamp(int(time_stamp)) + datetime.timedelta(hours=timedelta)
        time_stamp_str = local_time.strftime('%Y-%m-%d %H:%M:%S')
        return time_stamp_str
    except BaseException as e:
        print('时间戳转字符串格式失败！ : %s' % e)
        return ''


# 2013-10-10 15:40:00:98898934545 <str> ---> 1381419600.988990 <timestamp> ---> 2013-10-10 15:40:00.988990 <datetime>
def str2specific_date_time(time_str, timedelta=None):
    if timedelta is None:
        timedelta = get_offset_between_local_and_utc()
    try:
        # normal_date_time_str = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
        normal_date_time_str, millisecond_str = [time_str[0: time_str.rindex(':')],
                                                 time_str[time_str.rindex(':') + 1:]] \
            if time_str.count(':') > 2 else [time_str, '']
        normal_date_time = datetime.datetime.strptime(normal_date_time_str, "%Y-%m-%d %H:%M:%S")
        millisecond = int(millisecond_str) / pow(10, len(millisecond_str)) if millisecond_str else 0
        time_stamp = normal_date_time.timestamp() + millisecond
        specific_date_time = datetime.datetime.utcfromtimestamp(time_stamp) + datetime.timedelta(hours=timedelta)
        return specific_date_time
    except BaseException as e:
        # raise TypeError('字符串转datetime格式失败！ : %s' % e)
        print('字符串转datetime格式失败！ : %s' % e)
        return datetime.datetime.utcnow()


def is_data_exist(model, info):
    object_id = None
    try:
        object_id = ObjectId(info.get('_id'))
    except BaseException:
        pass
    is_data_exist = False
    try:
        is_data_exist = bool(model.find_one({"_id": object_id})) \
            if object_id is not None else False
    except BaseException as e:
        print(e)
        pass
    return is_data_exist


def x2list(expected_len, raw_material):
    new_list = list()
    for i in range(expected_len):
        new_list.append(raw_material)
    return new_list


# def compare_two_dicts(first_dic, second_dic, ignore_none_value_in_first_dic=False):
#     if not isinstance(first_dic, dict) or not isinstance(second_dic, dict):
#         raise TypeError('first_dic and second_dic must be both dict!')
#     if ignore_none_value_in_first_dic:
#         shared_dicts = {k: first_dic[k] for k in first_dic if k in second_dic
#                         and type(first_dic[k]) == type(second_dic[k]) or first_dic[k] is None}
#     else:
#         shared_dicts = {k: first_dic[k] for k in first_dic if k in second_dic
#                         and type(first_dic[k]) == type(second_dic[k])}
#     return len(shared_dicts) == len(first_dic)


def validate_and_pre_process_import_test_case(case_suite_model, testing_case_model, case_info,
                                              test_case_mapping, table_row_index):
    if not isinstance(case_info, dict):
        raise TypeError('case_info must be dict!')
    _case_info = copy.deepcopy(case_info)
    _is_case_exist = is_data_exist(testing_case_model, _case_info)
    _is_case_suite_exist = is_data_exist(case_suite_model, {'_id': _case_info.get('caseSuiteId')})
    _case_info.pop('_id') if '_id' in _case_info and not _is_case_exist else None
    _case_info.pop('caseSuiteId') if 'caseSuiteId' in _case_info and not _is_case_suite_exist else None
    for key, value in _case_info.items():
        if key == 'caseSuiteName':
            _case_info[key] = str(_case_info[key])
            continue
        case_attribute = getattr(testing_case_model, key)
        attribute_type = case_attribute.get_type()
        try:
            if attribute_type is str:
                _case_info[key] = str(_case_info[key])
                continue
            elif attribute_type is list:
                # TODO 判断优化
                is_transfer_ele2dict = case_attribute.expected_structure and \
                                       isinstance(case_attribute.expected_structure.get('expectedValueRange'), list) \
                                       and all(map(lambda x: x.get('expectedTypeRange') == [dict],
                                                   case_attribute.expected_structure.get('expectedValueRange')))
                if is_transfer_ele2dict:
                    # TODO 判断优化: (默认值可能不是都存在)
                    _case_info[key] = case_attribute.default if not _case_info[key] else\
                        list(map(lambda x: ast.literal_eval(x.replace('\'', '\"')),
                             str(_case_info[key]).strip().split('；')))
            elif attribute_type is dict:
                _case_info[key] = ast.literal_eval(str(_case_info[key]).strip()) \
                    if _case_info[key] else {}
            elif attribute_type is bool:
                _case_info[key] = True if str(_case_info[key]).strip().lower() == 'true' else False
                continue
            elif attribute_type == type(ObjectId()) and _is_case_exist:
                _case_info[key] = ObjectId(_case_info[key])
                continue
            elif attribute_type == type(datetime.datetime.utcnow()):
                _case_info[key] = str2specific_date_time(str(_case_info[key].strip()))
                continue
            elif attribute_type is int:
                _case_info[key] = int(_case_info[key])
                continue
            elif attribute_type is float:
                _case_info[key] = float(_case_info[key])
                continue
            is_valid = is_data_valid(case_attribute.expected_structure, _case_info[key])\
                if case_attribute.expected_structure is not None else True
            if not is_valid:
                # raise TypeError('{} 值不满足 {} 结构'.format(_case_info[key], case_attribute.expected_structure))
                raise TypeError('{} 值不满足 Model 中设定的结构~'.format(_case_info[key]))
        except BaseException as e:
            raise TypeError('表格中第 %s 行的 「%s」 值无法转换为 %s: %s'
                            % (table_row_index, test_case_mapping[key], str(attribute_type.__name__), e))
    return _is_case_exist, _case_info, _is_case_suite_exist


# 判断 pre_validate_data 符不符合给定的 expected_structure
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
        raise TypeError('expectedType、 expectedRange、 expectedDict  must be type_list、 list、dict,'
                        ' we got expected_type_range: %s 、expected_value_range: %s 、expected_dict: %s'
                        % (expected_type_range, expected_value_range, expected_dict))
    if not type(pre_validate_data) in expected_type_range:
        return False
    if isinstance(pre_validate_data, list):
        for list_piece in pre_validate_data:
            if expected_value_range and not any(map(is_data_valid, expected_value_range,
                                                    x2list(len(expected_value_range), list_piece))):
                return False
    elif isinstance(pre_validate_data, dict):
        for k, v in expected_dict.items():
            if k not in pre_validate_data or not is_data_valid(v, pre_validate_data[k]):
                return False
    return True


def send_email(model, project_id, send_data):
    mail_sender = list(model.find({'projectId': ObjectId(project_id)})
                       .sort([('createAt', pymongo.DESCENDING)]).limit(1))[0]
    user_name = mail_sender.get('username')
    pass_word = mail_sender.get('password')

    mail_list = send_data.get('mail_list')
    mail_title = send_data.get('mail_title')
    mail_content = send_data.get('mail_content')

    if send_report_email(user_name, pass_word, mail_list, mail_title, mail_content):
        return {'status': 'ok', 'data': '邮件发送成功'}
    else:
        return {'status': 'failed', 'data': '邮件发送失败'}


def get_random_key(digit_num=16):
    random_unit = string.ascii_letters + string.digits
    key = random.sample(random_unit, digit_num)
    keys = "".join(key)
    return keys


if __name__ == '__main__':
    pass

