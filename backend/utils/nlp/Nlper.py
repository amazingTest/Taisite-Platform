import requests
import json
import numpy as np


class Nlper:

    def __init__(self, bert_client):
        self.bert_client = bert_client

    def get_text_similarity(self, base_text, compaired_text, algorithm='cosine', magic_cut=True):
        if isinstance(algorithm, str) and algorithm.lower() == 'cosine':
            arrays = self.bert_client.encode([base_text, compaired_text])
            magic_array = (arrays[0] + arrays[1]) / np.pi
            arrays = [arrays[0] - magic_array, arrays[1] - magic_array] if magic_cut else arrays
            norm_1 = np.linalg.norm(arrays[0])
            norm_2 = np.linalg.norm(arrays[1])
            dot_product = np.dot(arrays[0], arrays[1])
            similarity = round(0.5 + 0.5 * (dot_product / (norm_1 * norm_2)), 2)
            return similarity

    @staticmethod
    # 翻译函数，word 需要翻译的内容
    def translate(word):
        # 有道词典 api
        url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=null'
        # 传输的参数，其中 i 为需要翻译的内容
        key = {
            'type': "AUTO",
            'i': word,
            "doctype": "json",
            "version": "2.1",
            "keyfrom": "fanyi.web",
            "ue": "UTF-8",
            "action": "FY_BY_CLICKBUTTON",
            "typoResult": "true"
        }
        # key 这个字典为发送给有道词典服务器的内容
        response = requests.post(url, data=key)
        # 判断服务器是否相应成功
        if response.status_code == 200:
            # 然后相应的结果
            return json.loads(response.text)['translateResult'][0][0]['tgt']
        else:
            print("有道词典调用失败")
            # 相应失败就返回空
            return None


if __name__ == '__main__':
    pass




