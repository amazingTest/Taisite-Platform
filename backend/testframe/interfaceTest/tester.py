import requests
import json
import time
import datetime
import re
from utils import common
import ast
from bson import ObjectId
from threading import Thread

import ssl
ssl._create_default_https_context = ssl._create_unverified_context


def async_test(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


# 基础测试类，负责获取测试用例的参数，请求，验证等信息后，进行测试，测试通过则返回True，不通过则抛出异常 -- 2019-1-7 09:27

# 基础测试类，负责获取测试用例的参数，请求，验证等信息后，进行测试，测试通过则返回{'status': 'ok'} ，
# 不通过则返回{'status': 'failed'} -- 2019-1-11 15:03

class tester:

    def __init__(self, test_case_list, domain, test_result_list=None, max_retries=5, global_vars=None):

        if not isinstance(test_case_list, list):
            raise ValueError('test_case_list must be a list!')

        try:
            from app import nlper
            self.nlper = nlper
        except ImportError as e:
            raise ImportError('nlp模型导入失败！<%s>' % e)

        self.test_case_list = test_case_list
        self.domain = domain
        self.session = requests.Session()

        if isinstance(max_retries, int) and max_retries > 0:
            # 设置连接重试
            a = requests.adapters.HTTPAdapter(max_retries=max_retries)
            self.session.mount('https://', a)
            self.session.mount('http://', a)

        self.test_result_list = test_result_list

        if global_vars is None:
            self.global_vars = {}

    # 异步方便返回测试启动是否成功的提示给前端
    @async_test
    def execute_all_test_and_send_report(self, testing_case_model, test_report_model,
                                         project_id, executor_nick_name, execution_mode):
        test_results = []
        for test_case in self.test_case_list:
            test_start_time = time.time()
            test_start_datetime = datetime.datetime.utcnow()
            test_result = self.execute_single_test(test_case)
            test_end_time = time.time()
            if 'lastManualTestResult' in test_case:
                test_case.pop('lastManualTestResult')
            domain = test_case["domain"] if 'domain' in test_case and isinstance(test_case["domain"], str) and \
                not test_case["domain"].strip() == '' else self.domain
            if 'requestProtocol' in test_case and 'route' in test_case:
                url = '%s://%s%s' % (test_case['requestProtocol'].lower(), domain, test_case['route'])
                test_case["url"] = url
            test_result["testBaseInfo"] = test_case
            test_result["testStartTime"] = test_start_datetime
            test_result["spendingTimeInSec"] = round(test_end_time - test_start_time, 3)
            test_results.append(test_result)

        self.test_result_list = test_results
        self.update_case_info(testing_case_model)
        self.send_report(test_report_model, project_id, executor_nick_name, execution_mode)

    # TODO 方便单个接口调试时同步返回结果，需重构
    def execute_all_test_for_cron_and_single_test(self):
        test_results = []
        for test_case in self.test_case_list:
            test_start_time = time.time()
            test_start_datetime = datetime.datetime.utcnow()
            test_result = self.execute_single_test(test_case)
            test_end_time = time.time()
            if 'lastManualTestResult' in test_case:
                test_case.pop('lastManualTestResult')
            domain = test_case["domain"] if 'domain' in test_case and isinstance(test_case["domain"], str) and \
                not test_case["domain"].strip() == '' else self.domain
            if 'requestProtocol' in test_case and 'route' in test_case:
                url = '%s://%s%s' % (test_case['requestProtocol'].lower(), domain, test_case['route'])
                test_case["url"] = url
            test_result["testBaseInfo"] = test_case
            test_result["testStartTime"] = test_start_datetime
            test_result["spendingTimeInSec"] = round(test_end_time - test_start_time, 3)
            test_results.append(test_result)
        return test_results

    def execute_single_test(self, test_case):
        returned_data = dict()
        returned_data["_id"] = test_case["_id"]
        returned_data["testConclusion"] = []
        if not isinstance(test_case, dict):
            returned_data["status"] = 'failed'
            returned_data["testConclusion"].append('测试用例结构不正确！ ')
            return returned_data

        def validate_test_case(test_case):
            compulsory_key_list = ['requestProtocol', 'route', 'requestMethod']
            return all([compulsory_key in test_case.keys() for compulsory_key in compulsory_key_list])

        if not validate_test_case(test_case):
            returned_data["status"] = 'failed'
            returned_data["testConclusion"].append('测试用例缺失必要参数！ ')
            return returned_data

        if test_case.get('isClearCookie'):
            self.session.cookies.clear()

        session = self.session

        url = None
        method = None
        json_data = None
        headers = dict()
        check_http_code = None
        check_response_data = None
        check_response_number = None
        check_response_similarity = None
        set_global_vars = None  # for example {'status': ['status']}

        domain = test_case["domain"] if 'domain' in test_case and isinstance(test_case["domain"], str) and \
                        not test_case["domain"].strip() == '' else self.domain
        if 'requestProtocol' in test_case and 'route' in test_case:
            test_case['route'] = \
                common.resolve_global_var(pre_resolve_var=test_case['route'], global_var_dic=self.global_vars) \
                    if isinstance(test_case['route'], str) else test_case['route']
            url = '%s://%s%s' % (test_case['requestProtocol'].lower(), domain, test_case['route'])
        if 'requestMethod' in test_case:
            method = test_case['requestMethod']
        if 'requestMethod' in test_case and 'presendParams' in test_case \
            and test_case['requestMethod'].lower() == 'get':
            url += '?'
            for key, value in test_case['presendParams'].items():
                if value is not None:
                    url += '%s=%s&' % (key, value)
            url = url[0:(len(url) - 1)]
        elif 'presendParams' in test_case and isinstance(test_case['presendParams'], dict):
            
            # dict 先转 str，方便全局变量替换
            test_case['presendParams'] = str(test_case['presendParams'])
            
            # 全局替换
            test_case['presendParams'] = common.resolve_global_var(pre_resolve_var=test_case['presendParams'],
                                                                   global_var_dic=self.global_vars)
            
            # 转回 dict
            test_case['presendParams'] = ast.literal_eval(test_case['presendParams'])
            
            json_data = test_case['presendParams']

        if 'headers' in test_case and not test_case['headers'] in ["", None, {}, {'': ''}]:
            if isinstance(test_case['headers'], list):
                for header in test_case['headers']:
                    if not header['name'].strip() == '':
                        headers[header['name']] = \
                            common.resolve_global_var(pre_resolve_var=header['value'], global_var_dic=self.global_vars)\
                            if isinstance(header['value'], str) else headers[header['name']]
            else:
                raise TypeError('headers must be list!')

        if 'setGlobalVars' in test_case and not test_case['setGlobalVars'] in [[], {}, "", None]:
            set_global_vars = test_case['setGlobalVars']

        headers = None if headers == {} else headers

        test_case['cookies'] = []
        for key, value in session.cookies.items():
            cookie_dic = dict()
            cookie_dic['name'] = key
            cookie_dic['value'] = value
            test_case['cookies'].append(cookie_dic)

        try:

            use_json_data = len(list(filter(lambda x: str(x).lower() == 'content-type' and 'json'
                                                      in headers[x], headers.keys() if headers else {}))) > 0

            response = session.request(url=url, method=method, json=json_data, headers=headers, verify=False) if use_json_data\
                else session.request(url=url, method=method, data=json_data, headers=headers, verify=False)

        except BaseException as e:
           returned_data["status"] = 'failed'
           returned_data["testConclusion"].append('请求失败, 错误信息: <%s> ' % e)
           return returned_data

        test_case['headers'] = headers  # 重新赋值生成报告时用

        response_status_code = response.status_code
        returned_data["responseHttpStatusCode"] = response_status_code
        returned_data["responseData"] = response.text

        try:
            response_json = json.loads(response.text) if isinstance(response.text, str) \
                                                         and response.text.strip() else {}
        except BaseException as e:

            if set_global_vars and isinstance(set_global_vars, list):
                for set_global_var in set_global_vars:
                    if isinstance(set_global_var, dict) and isinstance(set_global_var.get('name'), str):
                        name = set_global_var.get('name')
                        query = set_global_var.get('query')
                        value = common.dict_get(response.text, query)
                        self.global_vars[name] = str(value) if value else value

            if 'checkHttpCode' in test_case and not test_case['checkHttpCode'] in ["", None]:
                check_http_code = test_case['checkHttpCode']
            
            if check_http_code and not str(response_status_code) == str(check_http_code):
                returned_data["status"] = 'failed'
                returned_data["testConclusion"].append('响应状态码错误, 期待值: <%s>, 实际值: <%s>。\t'
                                                       % (check_http_code, response_status_code))
                return returned_data
            
            is_check_res_data_valid = isinstance(test_case.get('checkResponseData'), list) and\
                                      len(list(filter(lambda x: str(x.get('regex')).strip() == '',
                                                      test_case.get('checkResponseData')))) < 1
            is_check_res_similarity_valid = isinstance(test_case.get('checkResponseSimilarity'), list) and\
                                            len(list(filter(lambda x: isinstance(x.get('targetSimilarity'), type(None)),
                                                            test_case.get('checkResponseSimilarity')))) < 1
            is_check_res_number_valid = isinstance(test_case.get('checkResponseNumber'), list) and\
                                        len(list(filter(lambda x: str(x.get('expressions').get('expectResult')).strip()
                                                                  == '', test_case.get('checkResponseNumber')))) < 1
            # TODO 目前默认当 is_check_res_similarity_valid 和  is_check_res_number_valid 为真时，返回格式必须可转 json ，可优化
            is_test_failed = is_check_res_data_valid or is_check_res_number_valid or is_check_res_similarity_valid

            returned_data['status'] = 'failed' if is_test_failed else 'ok'

            returned_data["testConclusion"].append('服务器返回格式不是json, 错误信息: %s, 服务器返回为: %s '
                                                   % (e, response.text)) if returned_data.get('status') and \
                                                                    returned_data.get('status') == 'failed' else None
            if returned_data['status'] == 'ok':
                returned_data["testConclusion"].append('测试通过')

            return returned_data

        if set_global_vars and isinstance(set_global_vars, list):
            for set_global_var in set_global_vars:
                if isinstance(set_global_var, dict) and isinstance(set_global_var.get('name'), str):
                    name = set_global_var.get('name')
                    query = set_global_var.get('query')
                    value = common.dict_get(response_json, query)
                    self.global_vars[name] = str(value) if value else value

        if 'checkHttpCode' in test_case and not test_case['checkHttpCode'] in ["", None]:
            check_http_code = test_case['checkHttpCode']

        if 'checkResponseData' in test_case and not test_case['checkResponseData'] in [[], {}, "", None]:
            if not isinstance(test_case['checkResponseData'], list):
                raise TypeError('checkResponseData must be list！')
            for index, crd in enumerate(test_case['checkResponseData']):
                if not isinstance(crd, dict) or 'regex' not in crd or 'query' not in crd or \
                        not isinstance(crd['regex'], str) or not isinstance(crd['query'], list):
                    raise TypeError('checkResponseData is not valid!')

                # TODO 可开启/关闭 全局替换
                test_case['checkResponseData'][index]['regex'] = \
                    common.resolve_global_var(pre_resolve_var=crd['regex'], global_var_dic=self.global_vars) if \
                        crd.get('regex') and isinstance(crd.get('regex'), str) else ''  # 警告！python判断空字符串为False

            check_response_data = test_case['checkResponseData']

        if 'checkResponseSimilarity' in test_case and not test_case['checkResponseSimilarity'] in [[], {}, "", None]:
            if not isinstance(test_case['checkResponseSimilarity'], list):
                raise TypeError('checkResponseSimilarity must be list！')
            for index, crs in enumerate(test_case['checkResponseSimilarity']):
                if not isinstance(crs, dict) or 'baseText' not in crs or 'targetSimilarity' not in crs \
                        or 'compairedText' not in crs or not isinstance(crs['baseText'], str) \
                         or not isinstance(crs['compairedText'], str):
                    raise TypeError('checkResponseSimilarity is not valid!')
                test_case['checkResponseSimilarity'][index]['baseText'] = \
                    common.resolve_global_var(pre_resolve_var=crs['baseText'], global_var_dic=self.global_vars) if \
                        crs.get('baseText') and isinstance(crs.get('baseText'), str) else ''
                test_case['checkResponseSimilarity'][index]['compairedText'] = \
                    common.resolve_global_var(pre_resolve_var=crs['compairedText'], global_var_dic=self.global_vars) if \
                        crs.get('compairedText') and isinstance(crs.get('compairedText'), str) else ''
            check_response_similarity = test_case['checkResponseSimilarity']

        if 'checkResponseNumber' in test_case and not test_case['checkResponseNumber'] in [[], {}, "", None]:
            if not isinstance(test_case['checkResponseNumber'], list):
                raise TypeError('checkResponseNumber must be list！')
            for index, crn in enumerate(test_case['checkResponseNumber']):
                if not isinstance(crn, dict) or 'expressions' not in crn or \
                        not isinstance(crn['expressions'], dict):
                    raise TypeError('checkResponseNumber is not valid!')

                test_case['checkResponseNumber'][index]['expressions']['firstArg'] = \
                    common.resolve_global_var(pre_resolve_var=crn['expressions']['firstArg'],
                                              global_var_dic=self.global_vars) if \
                        crn['expressions'].get('firstArg') and isinstance(crn['expressions'].get('firstArg'),
                                                                          str) else ''

                test_case['checkResponseNumber'][index]['expressions']['secondArg'] = \
                    common.resolve_global_var(pre_resolve_var=crn['expressions']['secondArg'],
                                              global_var_dic=self.global_vars) if \
                        crn['expressions'].get('secondArg') and isinstance(crn['expressions'].get('secondArg'),
                                                                           str) else ''

                test_case['checkResponseNumber'][index]['expressions']['expectResult'] = \
                    common.resolve_global_var(pre_resolve_var=crn['expressions']['expectResult'],
                                              global_var_dic=self.global_vars) if \
                        crn['expressions'].get('expectResult') and isinstance(crn['expressions'].get('expectResult'),
                                                                              str) else ''
            check_response_number = test_case['checkResponseNumber']

        if check_http_code and not str(response_status_code) == str(check_http_code):
            returned_data["status"] = 'failed'
            returned_data["testConclusion"].append('响应状态码错误, 期待值: <%s>, 实际值: <%s>。\t'
                                                   % (check_http_code, response_status_code))
        if check_response_data:
            try:
                for crd in check_response_data:
                    regex = crd['regex']
                    if regex.strip() == '':
                        continue
                    query = crd['query']
                    real_value = common.dict_get(response_json, query)
                    if real_value is None:
                        returned_data["status"] = 'failed'
                        returned_data["testConclusion"].append('未找到正则校验的Json值(查询语句为: %s),   服务器响应为: %s'
                                                               % (query, response_json))
                        return returned_data
                    result = re.search(regex, str(real_value))  # python 将regex字符串取了r''(原生字符串)
                    if not result:
                        returned_data["status"] = 'failed'
                        returned_data["testConclusion"].append('判断响应值错误(查询语句为: %s),    响应值应满足正则: <%s>,\
                                                                    实际值: <%s> (%s)。(正则匹配时会将数据转化成string)\t'
                                                               % (query, regex, real_value, type(real_value)))
            except BaseException as e:
                returned_data["status"] = 'failed'
                returned_data["testConclusion"].append('判断响应值时报错, 错误信息: <%s>。\t' % e)

        if check_response_number:
            try:
                for crn in check_response_number:
                    expressions = crn['expressions']
                    # print(expressions)
                    if '' in expressions.values() or None in expressions.values():
                        continue
                    expressions_str, result = common.get_numbers_compared_result(expressions)
                    if not result:
                        returned_data["status"] = 'failed'
                        returned_data["testConclusion"].append('判断数值错误(判断表达式为: %s)。\t' % expressions_str)
            except BaseException as e:
                returned_data["status"] = 'failed'
                returned_data["testConclusion"].append('判断数值时报错, 错误信息: <%s>。\t ' % e)

        if hasattr(self, 'nlper') and self.nlper and check_response_similarity:
            try:
                for crs in check_response_similarity:
                    base_text = crs['baseText']
                    compaired_text = crs['compairedText']
                    target_similarity = crs['targetSimilarity']
                    if base_text.strip() == '' or compaired_text.strip() == '' or \
                            not common.can_convert_to_float(target_similarity):
                        continue
                    actual_similarity = self.nlper.get_text_similarity(base_text, compaired_text)

                    if float(actual_similarity) < float(target_similarity):
                        returned_data["status"] = 'failed'
                        returned_data["testConclusion"].append('相似度校验未达标！已对比字符串: 「%s」、「%s」, 实际相似度: 「%s」 '
                                                               '预期相似度: 「%s」。\t ' % (base_text, compaired_text,
                                                                              actual_similarity, target_similarity))
            except BaseException as e:
                returned_data["status"] = 'failed'
                returned_data["testConclusion"].append('判断相似度时报错, 模型服务器可能已宕机/断网。具体错误信息: <%s>。\t' % e)

        if returned_data["testConclusion"] == []:
            returned_data["status"] = 'ok'
            returned_data["testConclusion"].append('测试通过')
        else:
            returned_data["status"] = 'failed'
            returned_data["testConclusion"].append('测试不通过！')
        return returned_data

    def update_case_info(self, testing_case_model):
        for index, test_result in enumerate(self.test_result_list):
            test_case_id = test_result["_id"]
            test_result = common.format_response_in_dic(test_result)
            self.test_result_list[index] = test_result
            testing_case_model.update({"_id": ObjectId(test_case_id)},
                               {'$set': {'lastManualTestResult': test_result}})

    def send_report(self, test_report_model, project_id, executor_nick_name, execution_mode):
        test_count = len(self.test_result_list)
        passed_count = len(
            list(filter(lambda x: x == 'ok', [test_result["status"] for test_result in self.test_result_list])))
        failed_count = len(
            list(filter(lambda x: x == 'failed', [test_result["status"] for test_result in self.test_result_list])))
        passed_rate = '%d' % round((passed_count / test_count) * 100, 2) + '%'

        if test_count > 0:
            for test_result in self.test_result_list:
                if 'testBaseInfo' in test_result and 'lastManualTestResult' in test_result['testBaseInfo']:
                    test_result['testBaseInfo'].pop('lastManualTestResult')

            raw_data = {
                "projectId": ObjectId(project_id),
                "testCount": test_count,
                "passCount": passed_count,
                "failedCount": failed_count,
                "passRate": passed_rate,
                "comeFrom": execution_mode,
                "executorNickName": executor_nick_name,
                "testDetail": self.test_result_list,
                "createAt": datetime.datetime.utcnow()
            }
            filtered_data = test_report_model.filter_field(raw_data, use_set_default=True)
            test_report_model.insert(
                filtered_data
            )


if __name__ == '__main__':
    pass






