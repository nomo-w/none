from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import MD5
import base64
import hashlib
import requests
import json
import time
import random
from .all_config import *
# 屏蔽告警信息
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class MyError(Exception):
    def __init__(self, error_info):
        self.errorinfo = error_info

    def __str__(self):
        return self.errorinfo


class API(object):
    @classmethod
    def my_requests(cls, url, headers=DEFAULT_HEADERS, params={}, method=None, is_json=True, verify=False):
        '''
        发送requests的请求
        :param url: 目标url
        :param headers: 请求头
        :param params: 请求参数
        :param method: 请求方法
        :param is_json: 是否返回json数据
        :return: 返回响应参数
        '''
        try:
            if method == 'get':
                resp = requests.get(url, headers=headers, params=params, verify=verify)
            elif method == 'post':
                resp = requests.post(url, headers=headers, data=params, verify=verify)
            else:
                # should be never run
                resp = eval("requests.%s(url, headers=headers, params=params)" % method)
        except Exception as e:
            raise MyError(json.dumps(cls.handle_httpresponse('Content [%s] failed. Failed reason [%s]' % (url, e))))
        if resp.status_code != 200:
            raise MyError(json.dumps(cls.handle_httpresponse(
                'Content [%s] failed. Response status code [%s]' % (url, resp.status_code))))
        return cls.handle_httpresponse(resp.json(), 0) if is_json else cls.handle_httpresponse(resp.text, 0)

    @staticmethod
    def sign_(data, sign_method, key=None, charset='utf-8'):
        '''
        私钥签名,使用utf-8编码
        :param message: 需要签名的数据
        :param private_key_file: rsa私钥文件的位置
        :return: 签名后的字符串
        '''
        if sign_method == 'MD5withRSA':
            priKey = RSA.importKey(key)
            signer = PKCS1_v1_5.new(priKey)
            hash_obj = MD5.new(data.encode(charset))
            signature = base64.b64encode(signer.sign(hash_obj))
            signature = signature.decode(charset)
        elif sign_method == 'MD5':
            signature = hashlib.md5(data.encode(charset)).hexdigest()
        return signature

    @classmethod
    def verify_(cls, signature, data, sign_method, key=None, charset='utf-8'):
        '''
        公钥验签,使用utf-8编码
        :param signature: 经过签名处理的数据
        :param data: 需要验证的数据
        :param publickey_path: rsa公钥文件的位置
        :return: bool值
        '''
        if sign_method == 'MD5withRSA':
            public_keyBytes = base64.b64decode(key)
            pubKey = RSA.importKey(public_keyBytes)
            h = MD5.new(data.encode(charset))
            verifier = PKCS1_v1_5.new(pubKey)
            _ = verifier.verify(h, base64.b64decode(signature))
        elif sign_method == 'MD5':
            sign = cls.sign_(data, sign_method, key, charset)
            _ = [False, True][sign == signature]
        return _

    @staticmethod
    def handle_orderNo():
        '''生成订单号 当前日期时间20190826090315 + 4位随机数'''
        ymd = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        stp = str(random.randrange(1000, 9999))
        return ymd + stp

    @classmethod
    def do_pay(cls, params, url, headers, request_method='post'):
        # 发送支付请求
        resp = cls.my_requests(url, headers=headers, method=request_method, params=params)
        if resp['result']['code'] == '1000000':
            return cls.handle_httpresponse(resp['result']['data'], 0, params['orderNo'])
        else:
            raise MyError(json.dumps(cls.handle_httpresponse(resp['result']['msg'])))

    @classmethod
    def handle_param(cls, params_obj, amount, orderNo=None, bank_code=None):
        # 生成订单号
        if orderNo == None:
            orderNo = cls.handle_orderNo()

        channel = params_obj.LOCAL_CODE[bank_code]  # 支付通道
        character = params_obj.SIGN_CHATSET         # 字符编码
        sign = params_obj.SIGN                      # 签名格式
        prikey = params_obj.PRIKEY                  # 加密私钥
        param = params_obj.PARAMS                   # 所需参数
        vendor = params_obj.NAME                    # 厂商名
        notifyurl = CALLBACK                        # 回调地址
        memcode = params_obj.MEMCODE                # 商户id
        sign_method = params_obj.SIGN_METHOD        # 签名加密方法

        if vendor == '凌云付':
            sign = sign.format(memcode=memcode, channel=channel, amount=amount, orderNo=orderNo)
            sign = cls.sign_(sign, sign_method, prikey, character)
            param['channel'] = channel
            param['amount'] = amount
            param['orderNo'] = orderNo
            param['sign'] = sign
            param['memCode'] = memcode

        elif vendor == '高通':
            sign = sign.format(partner=memcode, channel=channel, amount=amount, orderNo=orderNo, key=prikey)
            sign = cls.sign_(sign, sign_method, prikey, character)
            param = param.format(partner=memcode, bank=channel, money=amount, order=orderNo, sign=sign)
        return param

    @classmethod
    def login_graphql(cls, graphql_url=GRA_URL, headers=DEFAULT_HEADERS):
        # 登录graphql
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        result = cls.my_requests(graphql_url, headers, {"query": LOGIN_GRAPHQL}, 'post')
        token = result['result']
        headers['Authorization'] = token['data']['login']['token']
        return headers

    @staticmethod
    def handle_httpresponse(result, status=-1, orderid=None, other=dict()):
        return_dic = {'result': result, 'status': RETURN_STATUS['not good']}
        if status == 0:
            return_dic['status'] = RETURN_STATUS['good']
        if other:
            for i in other:
                return_dic[i] = other[i]
        if orderid != None:
            return_dic['orderId'] = orderid
        return return_dic

    @classmethod
    def update_order_status(cls, vendor, orderStatus, money, orderNumber):
        headers = cls.login_graphql()
        if vendor == '高通':
            if orderStatus == '1':
                order_status = "confirmed"
            elif orderStatus == '-1':
                order_status = "cancelled"
        elif vendor == '凌云付':
            if orderStatus == '1':
                order_status = "confirmed"
            elif orderStatus == '-1':
                order_status = "cancelled"
        orderinfo = cls.request_graphql(
            headers,
            {"query": UPDATE_ORDER_GRAPHQL % (
                money,
                order_status,
                orderNumber
            )},
            'update_order'
        )
        return orderinfo

    @classmethod
    def request_graphql(cls, headers, param, query_type, url=GRA_URL, method='post'):
        resp = API.my_requests(url, headers, param, method)
        resp = resp['result']['data']
        if query_type == 'user':
            try:
                value = resp['users']['edges'][0]['node']
            except Exception:
                raise MyError(json.dumps(cls.handle_httpresponse('Not found user.')))
        elif query_type == 'bank':
            try:
                value = resp['banks']['edges'][0]['node']
            except Exception:
                raise MyError(json.dumps(cls.handle_httpresponse('Not found bank')))
        elif query_type == 'create_order':
            try:
                value = resp['deposit']['deposit']
            except Exception:
                raise MyError(json.dumps(cls.handle_httpresponse('Create order failed')))
        elif query_type == 'update_order':
            try:
                value = resp['depositApproval']['deposit']
            except Exception:
                raise MyError(json.dumps(cls.handle_httpresponse('Update order failed')))
        elif query_type == 'get_vendor':
            # 查询厂商信息, 厂商号, 厂商私钥
            try:
                value = resp['payVendor']['edges'][0]['node']
            except Exception:
                raise MyError(json.dumps(cls.handle_httpresponse('Query vendor failed')))
        return value