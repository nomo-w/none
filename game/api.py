from game.longmen_config import *
from game.all_config import *
import requests
import time
import psycopg2
import json
import hashlib
import random


class MyError(Exception):
    def __init__(self, error_info):
        self.errorinfo = error_info

    def __str__(self):
        return self.errorinfo


class GAME_API:
    @classmethod
    def my_requests(cls, url, headers=DEFAULT_HEADERS, params={}, method=None, is_json=True, param_type='data'):
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
                resp = requests.get(url, headers=headers, params=params)
            elif method == 'post':
                if param_type == 'json':
                    resp = requests.post(url, headers=headers, json=params)
                elif param_type == 'data':
                    resp = requests.post(url, headers=headers, data=params)
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
    def handle_httpresponse(result, status=-1, orderid=None, other=dict()):
        '''处理返回结果'''
        return_dic = {'result': result, 'status': RETURN_STATUS['not good']}
        if status == 0:
            return_dic['status'] = RETURN_STATUS['good']
        if other:
            for i in other:
                return_dic[i] = other[i]
        if orderid != None:
            return_dic['orderId'] = orderid
        return return_dic

    @staticmethod
    def handle_orderNo(user):
        '''生成订单号 当前日期20190826 + 4位随机数'''
        ymd = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        stp = str(random.randrange(1000, 9999))
        return user + ymd + stp

    @staticmethod
    def sign_(data):
        sign = hashlib.md5(data.encode('utf-8')).hexdigest()
        return sign

    def handle_return_zsq(func):
        def inner(*args, **kwargs):
            return_value = func(*args, **kwargs)
            if return_value['result']['status'] != OK_STATUS:
                raise MyError(json.dumps(args[0].handle_httpresponse(return_value['result']['message'])))
            return args[0].handle_httpresponse(return_value['result']['data'], 0)
        return inner

    @classmethod
    @handle_return_zsq
    def getGameKindList(cls, url=GET_GAME_TYPE_API, headers=DEFAULT_HEADERS, clientcode=CLIENTCODE):
        '''获取游戏种类'''
        headers['Content-Type'] = CONTENT
        origin_sign = 'clientCode={c}&key={k}'.format(c=clientcode, k=MD5KEY)
        sign = cls.sign_(origin_sign)
        param = {'clientCode': CLIENTCODE, 'signature': sign}
        resp = cls.my_requests(url, headers, param, 'post', param_type='json')
        return resp

    @classmethod
    @handle_return_zsq
    def queryVendor(cls, gameKindCode, url=GET_GAME_VENDOR_API, headers=DEFAULT_HEADERS, clientcode=CLIENTCODE):
        '''根据游戏种类获取游戏厂商'''
        headers['Content-Type'] = CONTENT
        origin_sign = 'clientCode={c}&gameKindCode={g}&key={k}'.format(c=clientcode, g=gameKindCode, k=MD5KEY)
        sign = cls.sign_(origin_sign)
        param = {
            'clientCode': clientcode,
            'gameKindCode': gameKindCode,
            'signature': sign
        }
        resp = cls.my_requests(url, headers, param, 'post', param_type='json')
        return resp

    @classmethod
    @handle_return_zsq
    def getGameCode(cls, url=GET_GAME_CODE_API, headers=DEFAULT_HEADERS, clientcode=CLIENTCODE, **kwargs):
        '''查询游戏代码'''
        headers['Content-Type'] = CONTENT
        origin_sign = 'clientCode={c}&key={k}'.format(c=clientcode, k=MD5KEY)
        sign = cls.sign_(origin_sign)
        param = {'clientCode': clientcode, 'signature': sign, **kwargs} \
            if kwargs else {'clientCode': CLIENTCODE, 'signature': sign}
        resp = cls.my_requests(url, headers, param, 'post', param_type='json')
        return resp

    @classmethod
    @handle_return_zsq
    def queryBalance(cls, user, headers=DEFAULT_HEADERS, vendorCode=None,
                         clientcode=CLIENTCODE, url=GET_PLAYER_BALANCE_API):
        '''获取用户钱包余额'''
        headers['Content-Type'] = CONTENT
        timestamp = int(time.time())
        origin_sign = 'clientCode={c}&username={u}&timestamp={t}&key={k}'.\
            format(c=clientcode, u=user, t=timestamp, k=MD5KEY)
        sign = cls.sign_(origin_sign)
        param = {
            'clientCode': clientcode,
            'username': user,
            'timestamp': timestamp,
            'signature': sign
        }
        resp = cls.my_requests(url, headers, param, 'post', param_type='json')
        return resp

    @classmethod
    @handle_return_zsq
    def recharge_withdraw(cls, url, balance, user, orderNo=None,
                          clientcode=CLIENTCODE, headers=DEFAULT_HEADERS):
        if orderNo == None:
            orderNo = cls.handle_orderNo(user)

        timestamp = int(time.time())
        origin_sign = 'clientCode={c}&username={u}&orderNum={o}&money={m}&timestamp={t}&key={k}'. \
            format(c=clientcode, u=user, o=orderNo, m=balance, t=timestamp, k=MD5KEY)
        sign = cls.sign_(origin_sign)
        headers['Content-Type'] = CONTENT
        param = {
            'clientCode': clientcode,
            'username': user,
            'orderNum': orderNo,
            'money': balance,
            'timestamp': timestamp,
            'signature': sign
        }

        resp = cls.my_requests(url, headers, param, 'post', param_type='json')
        return resp

    @classmethod
    @handle_return_zsq
    def get_game(cls, username, vendorCode, client_ip, clientcode=CLIENTCODE, gameCode=None,
                 terminalType=None, headers=DEFAULT_HEADERS, url=GET_GAME_API):
        '''获取游戏连接'''
        origin_sign = 'clientCode={c}&vendorCode={v}&username={u}&clientIp={i}&key={k}'. \
            format(c=clientcode, v=vendorCode, u=username, i=client_ip, k=MD5KEY)
        sign = cls.sign_(origin_sign)
        param = {
            'username': username,
            'vendorCode': vendorCode,
            'clientCode': clientcode,
            'clientIp': client_ip,
            'signature': sign
        }
        if gameCode:
            param['gameCode'] = gameCode
        if terminalType:
            param['terminalType'] = terminalType

        headers['Content-Type'] = CONTENT
        resp = cls.my_requests(url, headers, params=param, method='post', param_type='json')
        return resp

    @classmethod
    @handle_return_zsq
    def getVendorBalance(cls, username, vendorcode, client_ip, headers=DEFAULT_HEADERS,
                            clientcode=CLIENTCODE, url=GET_BALANCE_BY_VENDOR_API):
        '''查询用户在游戏商的余额, 暂时不需要启用, 后面有一键查询所有游戏商的余额接口'''
        headers['Content-Type'] = CONTENT
        # vendor_set = cls.getAllVendor()
        origin_sign = 'clientCode={c}&vendorCode={v}&username={u}&clientIp={i}&key={k}'.\
            format(c=clientcode, v=vendorcode, u=username, i=client_ip, k=MD5KEY)
        sign = cls.sign_(origin_sign)
        param = {
            'clientCode': clientcode,
            'vendorCode': vendorcode,
            'username': username,
            'clientIp': client_ip,
            'signature': sign
        }
        resp = cls.my_requests(url, headers, param, 'post', param_type='json')
        return resp

    @classmethod
    @handle_return_zsq
    def getAllPlayerBalance(cls, username, client_ip, headers=DEFAULT_HEADERS,
                            clientcode=CLIENTCODE, url=GET_ALL_BALANCE_API):
        '''一键查询用户在所有游戏商的余额'''
        headers['Content-Type'] = CONTENT
        # vendor_set = cls.getAllVendor()
        origin_sign = 'clientCode={c}&username={u}&clientIp={i}&key={k}'.\
            format(c=clientcode, u=username, i=client_ip, k=MD5KEY)
        sign = cls.sign_(origin_sign)
        param = {
            'clientCode': clientcode,
            'username': username,
            'clientIp': client_ip,
            'signature': sign
        }
        resp = cls.my_requests(url, headers, param, 'post', param_type='json')
        return resp

    @classmethod
    @handle_return_zsq
    def withdraw_one_vendor(cls, vendorcode, username, money, client_ip, ordernum=None,
            clientcode=CLIENTCODE, headers=DEFAULT_HEADERS, url=PLAYERWITHDRAW_API):
        '''单个厂商金额到钱包'''
        if ordernum == None:
            ordernum = cls.handle_orderNo(username)

        headers['Content-Type'] = CONTENT
        origin_sign = 'clientCode={c}&vendorCode={v}&username={u}&orderNum={o}&money={m}&clientIp={i}&key={k}'.\
            format(c=clientcode, v=vendorcode, u=username, o=ordernum, m=money, i=client_ip, k=MD5KEY)
        sign = cls.sign_(origin_sign)
        param = {
            'clientCode': clientcode,
            'vendorCode': vendorcode,
            'username': username,
            'orderNum': ordernum,
            'money': money,
            'clientIp': client_ip,
            'signature': sign
        }
        resp = cls.my_requests(url, headers, param, 'post', param_type='json')
        return resp

    @classmethod
    @handle_return_zsq
    def getBetRecords(cls, vendorCode, user=None, clientcode=CLIENTCODE,
                      headers=DEFAULT_HEADERS, url=GET_BETRECORDS_API, **kwargs):

        headers['Content-Type'] = CONTENT
        origin_sign = 'clientCode={c}&key={k}'.format(c=clientcode, k=MD5KEY)
        sign = cls.sign_(origin_sign)
        param = {'clientCode': clientcode, 'vendorCode': vendorCode, 'signature': sign, **kwargs} \
            if kwargs else {'clientCode': clientcode, 'vendorCode': vendorCode, 'signature': sign}
        if user:
            param['username'] = user


        resp = cls.my_requests(url, headers, param, 'post', param_type='json')
        return resp

    @classmethod
    def getAllVendors(cls):
        '''获取所有游戏厂商'''
        _ = list()
        # 获取所有游戏种类
        game_type = cls.getGameKindList()
        for i in game_type['result']:
            # 循环所有游戏类型获取对应的游戏厂商
            vendor_data = cls.queryVendor(i['code'])
            for i1 in vendor_data['result']:
                # 将游戏厂商加入到列表
                _.append(i1['vendorCode'])
        return set(_)

    @classmethod
    def withdraw_all_vendor(cls, username, client_ip):
        '''将所有游戏厂商的余额下分到南阳钱包'''
        # 获取所有的厂商的余额
        all_balance = cls.getAllPlayerBalance(username, client_ip)
        for i in all_balance['result']:

            if i['seamlessWallet'] == 0:
                try:
                    resp = cls.withdraw_one_vendor(i['vendorCode'], username, i['freeMoney'], client_ip)
                except MyError as e:

                    continue


class Postgresql:
    def __init__(self, db='mypay', us='mypguser', pa='mypguser', ho='127.0.0.1', po='5432'):
        # 连接数据库
        self.conn = psycopg2.connect(
            database=db,
            user=us,
            password=pa,
            host=ho,
            port=po
        )
        # 创建游标对象
        self.cur = self.conn.cursor()
        self.create_sql = "INSERT INTO {table} {key} VALUES {value};"
        # self.select_sql = 'SELECT "pkNo" from {table} WHERE "pkNo"=\'{value}\';'
        self.select_sql = 'SELECT "pkNo" from {table} WHERE {key}=\'{value}\';'
        self.update_sql = 'UPDATE {table} SET balance={balance} WHERE "pkNo"=\'{pkno}\';'

    def create_(self, data, tb=USER_TB):
        '''增加数据'''
        _ = data if isinstance(data, dict) else json.loads(data)

        if tb == USER_TB:
            key = '("pkNo", username, create_date, is_active)'
            value = (
                _['user_id'],
                _['user_name'],
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                _['status']
            )
        elif tb == USER_BALANCE_TB:
            key = '(balance,"pkNo")'
            value = (
                _['balance'],
                _['user_id']
            )
        elif tb == USER_BET_TB:
            key = '(longmen_data,vendor_data,user_id)'
            value = (
                _['username'],
                json.dumps(_['longmen_data']),
                json.dumps(_['vendor_data'])
            )

        value_len = '('
        for i in value:
            value_len += '%s,'
        value_len = value_len[:-1] + ')'

        sql = self.create_sql.format(table=tb, key=key, value=value_len)
        self.cur.execute(sql, value)

    def select_(self, data, tb=USER_TB, key='"pkNo"'):
        sql = self.select_sql.format(value=data, table=tb, key=key)
        self.cur.execute(sql)
        value = self.cur.fetchall()
        return value

    def update_(self, data, tb=USER_TB):
        _ = data if isinstance(data, dict) else json.loads(data)
        sql = self.update_sql.format(balance=_['balance'], pkno=_['user_id'], table=tb)
        self.cur.execute(sql)

    def commit_(self):
        self.conn.commit()

    def close_(self):
        self.cur.close()
        self.conn.close()


if __name__ == '__main__':
    w = GAME_API.sign_('accountid=80000004&amount=1000&notifyurl=http://93.157.63.50:8088/callback/&orderid=test123456789WEIXIN&type=WEIXIN&authtoken=BF8B6694AD7A46F08796AFD1B01E820C')
    print(w.upper())