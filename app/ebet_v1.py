#!/usr/bin/env python
# -*- encoding:utf-8 -*-
'''
@File           : ebet_v1.1.py
@Modify Time    : 2019/5/7 20:56
@Author         : SPARK
@Version        : 1.0
@Contact        : xxx@xxx.com
@License        : (C)Copyright 2019-2020,group-ltd
@Desc           : 游戏接口

'''

import sys,time,json,requests,socket
from urllib import parse
from game_package.game_api.api_base import create_order_no
from game_package.game_api.api_base import get_host_ip
from game_package.game_api.api_base import game_api_fake_data,game_api_basic
#from game_package.game_manager import game_api_basic
import base64
from Crypto import Random
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import MD5
from Crypto.Signature import PKCS1_v1_5
from game_package.game_api.api_base import log
import time
import web
import game_package.game_api.api_base as api_base
from game_package.lang import common
#import game_package.game_manager as game_manager
import game_package.game_api.game_model as game_model
import db
import hashlib
import uuid
from communication.redis import send_ebet_game_record

GAME_TYPE_DEC = {
    1: 'bet', # 下注
    2: 'payout', # 派彩
    3: 'dealer', # 打赏荷官
    6: 'betaward', # 投注奖励
    8: 'matchfee', # 大赛报名
    9: 'matchrefund', # 大赛返还
    11: 'beterr', # 下注错误退还
    14: 'matchaward', # 大赛派彩
    15: 'backmatchaward', # 大赛奖金取回
    23: 'bonuslucky', # 幸运红包
    24: 'bonusquota', # 限量红包
    27: 'withholding', # 预扣
    28: 'refund' # 预扣返还
}

#eg:http://hk.oplive.info:8080/?infoUrl=h5/65299e&username=panda_iftest&accessToken=836108217fd57c4fdaf3d57539ecbb46

'''register or login'''
class registerOrLogin:

    def POST(self, ):
        '''1 get post'''
        params_org = str(web.data(), 'utf-8')
        # print(params_org)
        # username为中文问题，需要解码
        params = parse.unquote(params_org)

        '''2 put post to log'''
        log('ebet_reg', 'registerOrLogin resquest: '+params)
        data = {}
        try:
            params = json.loads(params)
            params_org = json.loads(params_org)
            
            
            
    
            '''3 prepare response data'''
            data['seqNo'] = params['seqNo']
            data['event'] = params['event']
            data['username'] = params_org['username']
            data['nickname'] = params_org['username']
            data['accessToken'] = params['accessToken']
            data['sessionToken'] = params['sessionToken']
            data['subChannelId'] = 0
            data['currency'] = 'CNY'
            data['language'] = 'zh_cn'
    
            '''4 vertify'''
            sep_username = params['username'].split('_')
            platform_pre = sep_username[0]+'_'
            param_username = sep_username[1]
        except Exception as e:
            print(e)
            data['timestamp'] = int(time.time() * 1000)
            data['status'] = 4037
            json_data = json.dumps(data)
            log('ebet_reg', 'registerOrLogin error: param error return: ' + json_data)
            return json_data

        api_info = game_api(param_username,platform_pre)
        user_id = api_info.user_id
        if user_id == False:
            data['timestamp'] = int(time.time() * 1000)
            data['status'] = 4037
            json_data = json.dumps(data)
            log('ebet_reg', 'registerOrLogin error: on user_id return: ' + json_data)
            return json_data
        event = params['event']
        signature = params['signature']
        signn = base64.b64decode(signature)
        rsa_pubKey = RSA.importKey(api_info._pubkey)
        vertifier = PKCS1_v1_5.new(rsa_pubKey)
        wait_sign = params['seqNo']+event+str(params['channelId'])+str(params['timestamp'])+params_org['username']+params['accessToken']
        hash_md5 = MD5.new(wait_sign.encode("utf-8"))
        vertify = vertifier.verify(hash_md5, signn)

        '''5 judge post information'''
        wait_md5 = 'if'+api_info.username
        md5_username = MD5.new(wait_md5.encode("utf-8"))
        if not vertify:  #wrong signature
            data['status'] = 4026
        elif params['channelId'] != int(api_info._merchant_id):  #if channel is not correct
            data['status'] = 1004
        elif params['accessToken'] != md5_username.hexdigest(): # token is not valid
            data['status'] = 410
        else:
            data['status'] = 200
        data['timestamp'] = int(time.time() * 1000)
        '''6 put return data to log'''
        json_data = json.dumps(data)
        log('ebet_reg', 'registerOrLogin return: ' + json_data)
        return json_data

'''synchronization information'''
class syncCredit:
    def POST(self):
        '''1 get post'''
        params_org = str(web.data(), 'utf-8')
        # print(params_org)
        # username为中文问题，需要解码
        params = parse.unquote(params_org)

        '''2 put post to log'''
        # log('ebet_sync', 'syncCredit resquest: '+params)
        data = {}
        try:
            params = json.loads(params)
            params_org = json.loads(params_org)
    
            '''3 prepare response data'''
            data['seqNo'] = params['seqNo']
            data['event'] = params['event']
            data['username'] = params_org['username']
    
            '''4 judge post information'''
            sep_username = params['username'].split('_')
            platform_pre = sep_username[0]+'_'
            param_username = sep_username[1]
            api_info = game_api(param_username,platform_pre)
            user_id = api_info.user_id
            if user_id == False:
                data['money'] = 0
                data['status'] = 4037
                data['timestamp'] = int(time.time() * 1000)
                json_data = json.dumps(data)
                log('ebet_sync', 'syncCredit return'+json_data)
                return json_data
            data['money'] = api_info.balance
            if params['channelId'] != int(api_info._merchant_id):  #channel is not exist
                data['status'] = 1004
            else:
                data['status'] = 200
            data['timestamp'] = int(time.time() * 1000)
    
            '''6 put return data to log'''
            json_data = json.dumps(data)
            # log('ebet_sync', 'syncCredit return:' + json_data)
            return json_data
        except Exception as e:
            print(e)
            log('ebet_sync', 'syncCredit error request: ' + params)

'''balance plus/minus operation'''
class increaseCredit:
    def POST(self):
        '''1 get post'''
        params_org = str(web.data(), 'utf-8')
        # print(params_org)
        # username为中文问题，需要解码
        params = parse.unquote(params_org)
        # params = '{"username":"iftest","channelId":920,"money":-10,"type":1,"platform":3,"currency":"CNY","seqNo":"5ebb985c0f2467db77e76864c70f8b4a","sessionToken":"dc7dc6ef4180310c7a3f9cbd2032af8f","detail":{"tableCode":"D1","tableType":2,"tableSubType":0,"roundCode":"D1-190628144010","betTime":1561704014694,"betList":[{"betType":10,"betMoney":10}],"totalBet":10,"validBet":0},"event":"increaseCredit","timestamp":1561704014733,"signature":"b6mrUCFhI3FPteREYGcjx3HTdu4JJ5wARnM3FbDouFBO0CW8DvDBk02p/YbTSf4sD6aXAomeO0Q+JDI7OTkFTg=="}'
        '''2 put post to log'''
        log('ebet_increase', 'request: ' + params)
        data = {}
        try:
            params = json.loads(params)
            params_org = json.loads(params_org)
        except json.decoder.JSONDecodeError:
            temp_params = json.dumps(eval(params))
            params = json.loads(temp_params)

        '''3 prepare response data'''
        data['seqNo'] = params['seqNo']
        data['event'] = params['event']
        data['username'] = params_org['username']

        '''4 vertify'''
        sep_username = params['username'].split('_')
        platform_pre = sep_username[0]+'_'
        param_username = sep_username[1]
        api_info = game_api(param_username,platform_pre)
        user_id = api_info.user_id
        if user_id == False:
            data['money'] = 0
            data['moneyBefore'] = 0
            data['status'] = 4037
            data['timestamp'] = int(time.time() * 1000)
            json_data = json.dumps(data)
            log('ebet_increase', 'error: no user_id return: ' + json_data)
            return json_data
        data['money'] = float(api_info.balance)+float(params['money'])
        data['moneyBefore'] = api_info.balance
        event = params['event']
        signature = params['signature']
        signn = base64.b64decode(signature)
        rsa_pubKey = RSA.importKey(api_info._pubkey)
        vertifier = PKCS1_v1_5.new(rsa_pubKey)
        wait_sign = params['seqNo'] + event + str(params['channelId']) + str(params['timestamp']) + params_org['username'] +str(params['money'])
        hash_md5 = MD5.new(wait_sign.encode("utf-8"))
        vertify = vertifier.verify(hash_md5, signn)
        # print(params)
        # print(type(params['detail']['betList']['betMoney']))
        # print(type(api_info.balance))
        '''5 judge post information'''
        if not vertify:  # wrong signature
            data['status'] = 4026
        elif params['channelId'] != int(api_info._merchant_id):  #channel is not exist
            data['status'] = 1004
        elif params['type'] in (1, 3, 5, 8, 15, 27):
            if (float(params['money']) + float(api_info.balance)) > 0: # balance not enough
                data['status'] = 200
            else:
                data['status'] = 1003
        else:
            data['status'] = 200
        # -------------------------------------------

        '''6 deal bet,payout,Tips Dealer'''
        # db_game_bet = db.game_bet()
        # print(db_game_bet)
        if params['type'] in (1, 2, 3, 6, 8, 9, 11, 12, 13, 14, 15, 23, 24, 27, 28):  #bet
            '''6.1 save to game_bet and deduct money'''
            is_ok, result = self._save_bet_record(data, params, user_id, api_info)
            if not is_ok:
                return result

        else:
            data['status'] = 505  #no this type

        '''6 return response'''

        data['seqNo'] = params['seqNo']
        data['event'] = params['event']
        data['timestamp'] = int(time.time() * 1000)

        json_data = json.dumps(data)
        '''7 put return data to log'''
        log('ebet_increase', 'return:' + json_data)
        return json_data

    def _save_bet_record(self, data, params, user_id, api_info):
        if data['status'] == 200:
            '''1 prepare params'''
            bet_list = []
            bet_fields = []
            bet_field_amounts = []
            if 'betList' in params['detail']:
                bet_list = params['detail']['betList']
                for trans in bet_list:
                    bet_fields.append(int(trans['betType']))
                    bet_field_amounts.append(trans['betMoney'])

            data_save = {}
            # data_save['uid'] = uuid.uuid3(uuid.NAMESPACE_DNS,'betamount')
            data_save['user_id'] = user_id
            game_list = game_model.get_id_in_game_list(api_info.api_game_id,params['detail']['tableType'])
            game_list = game_list[0]
            if game_list == False:
                data['status'] = 500
                json_data = json.dumps(data)
                log('ebet_increase', 'error: no game_list return'+json_data)
                return False, json_data
            data_save['game_id'] = game_list.id
            data_save['game_type'] = params['type']
            data_save['game_round'] = params['detail']['roundCode']
            data_save['bet_count'] = len(bet_list)
            data_save['bet_amount'] = params['money']
            data_save['bet_fields'] = bet_fields
            data_save['bet_field_amounts'] = bet_field_amounts
            data_save['order_id'] = params['seqNo']
            if params['type'] in (1, 2, 11, 27):
                data_save['created'] = api_base.timestramp_to_date(params['detail']['betTime'])
            else:
                data_save['created'] = api_base.timestramp_to_date(params['timestamp'])
            data_save['status'] = 1

            # 2 save to game_bet
            bet_order = game_model.save_bet_order(data_save)

            # 3 save money
            game_model.save_user_bal(user_id, params['money'])

            # 4 set to redis
            data_redis = {}
            data_redis['user_id'] = user_id
            data_redis['order_id'] = params['seqNo']
            data_redis['amount'] = params['money']
            data_redis['balance'] = data['money']
            data_redis['balance_before'] = data['moneyBefore']
            data_redis['create_date'] = data_save['created']
            data_redis['type'] = GAME_TYPE_DEC[params['type']] if params['type'] in GAME_TYPE_DEC else params['type']
            data_redis['game_name'] = game_list.name
            data_redis['round_code'] = params['detail']['roundCode']
            data_redis['game_vendor'] = 'ebet'
            # db_redis.hset("user_bet_record", params['seqNo'], json.dumps(data_redis))
            send_ebet_game_record(json.dumps(data_redis))
        return True, "ok"


'''payout again if didn't payout(补单派彩)'''
class queryIncreaseCreditRecord:
    def POST(self):
        '''1 get post'''
        params = str(web.data(), 'utf-8')
        print("queryIncreaseCreditRecord")
        print(params)

        '''2 put post to log'''
        log('ebet_query_increase', 'request:'+params)
        data = {}
        params = json.loads(params)

        '''3 prepare response data'''
        data['seqNo'] = params['seqNo']
        data['event'] = params['event']
        data['username'] = params['username']
        data['creditRecord'] = []

        '''4 vertify'''
        sep_username = params['username'].split('_')
        platform_pre = sep_username[0]+'_'
        param_username = sep_username[1]
        api_info = game_api(param_username, platform_pre)
        user_id = api_info.user_id
        if user_id == False:
            data['status'] = 4037
            data['timestamp'] = int(time.time() * 1000)
            json_data = json.dumps(data)
            log('ebet_query_increase', 'error: no user_id return'+json_data)
            return json_data
        signature = params['signature']
        signn = base64.b64decode(signature)
        rsa_pubKey = RSA.importKey(api_info._pubkey)
        vertifier = PKCS1_v1_5.new(rsa_pubKey)
        wait_sign = params['username'] + str(params['timestamp'])
        hash_md5 = MD5.new(wait_sign.encode("utf-8"))
        vertify = vertifier.verify(hash_md5, signn)

        '''5 judge post information'''
        wait_md5 = 'if'+api_info.username
        md5_username = MD5.new(wait_md5.encode("utf-8"))
        if not vertify:  # wrong signature
            data['status'] = 4026
        elif params['channelId'] != int(api_info._merchant_id):  #channel is not exist
            data['status'] = 1004
        else:
            data['status'] = 200

        '''6 deal our logic'''
        bet_order = game_model.is_exist_bet(params['querySeqNo'])
        if not bet_order:  #no this order in our game_bet
            data['timestamp'] = int(time.time() * 1000)
            json_data = json.dumps(data)
            return json_data
#         if params['querySeqNo']:  #如果有此参数,则只要回传对应的SeqNo,否则要回传相关的请求纪录
#             only_return = {}
#             only_return['seqNo'] = bet_order['order_id']
#             json_data = json.dumps(only_return)
#             return json_data
        credit_record = {}
        credit_record['querySeqNo'] = params['querySeqNo']
        credit_record['type'] = bet_order['game_type']
        credit_record['username'] = params['username']
        credit_record['roundCode'] = bet_order['game_round']
        credit_record['status'] = 200
        credit_record['creditTime'] = bet_order['created']
        credit_record['moneyBefore']  = 0
        credit_record['moneyAfter']  = 0
        credit_record['money']  = bet_order['bet_amount']
        data['creditRecord'].append(credit_record)

        '''7 return response '''
        data['timestamp'] = int(time.time() * 1000)
        json_data = json.dumps(data)
        '''8 put return data to log'''
        log('ebet_query_increase', 'return:' + json_data)
        return json_data


'''refund for bet failed money in single table number'''
class refundSingleWallet:
    def POST(self):
        '''1 get post'''
        params = str(web.data(), 'utf-8')
        '''2 put post to log'''
        print("refundSingleWallet")
        print(params)
        log('ebet_wallet', params)
        data = {}
        params = json.loads(params)
        
        '''3 prepare response data'''
        data['seqNo'] = params['seqNo']
        data['event'] = params['event']
        data['username'] = params['username']
        data['refundMoney'] = 0

        '''4 vertify'''
        sep_username = params['username'].split('_')
        platform_pre = sep_username[0]+'_'
        param_username = sep_username[1]
        api_info = game_api(param_username, platform_pre)
        user_id = api_info.user_id
        if user_id == False:
            data['moneyAfter'] = 0
            data['moneyBefore'] = 0
            data['refundMoney'] = 0
            data['status'] = 4037
            data['timestamp'] = int(time.time() * 1000)
            data['resultList'] = []
            json_data = json.dumps(data)
            log('ebet_wallet', 'error: no user_id return: ' + json_data)
            return json_data
        data['moneyBefore'] = api_info.balance
        event = params['event']
        signature = params['signature']
        signn = base64.b64decode(signature)
        rsa_pubKey = RSA.importKey(game_api._pubkey)
        vertifier = PKCS1_v1_5.new(rsa_pubKey)
        wait_sign = params['username'] + str(params['timestamp'])
        hash_md5 = MD5.new(wait_sign.encode("utf-8"))
        vertify = vertifier.verify(hash_md5, signn)

        '''4 judge post information'''
        if not vertify:  # wrong signature
            data['status'] = 4026
        # -------------------------(now explanatory note)
        # elif params['username'] != our_username:  #username is not exist
        #     data['status'] = 4037
        # elif params['channelId'] != int(api_info._merchant_id):  #channel is not exist
        #     data['status'] = 1004
        # elif params['detail']['betList']['betMoney'] > our_user_money: # balance not enough
        #     data['status'] = 1003
        else:
            data['status'] = 200
        
        # -------------------------------------------

        '''5 deal refund operation'''
        refund_list = params['refundList']
        for refund in refund_list:
            result, result_obj = self._save_bet_record(data, refund, params, user_id, api_info)
            if result:
                data['resultList'].append(result_obj)

        '''6 return response'''
        data['timestamp'] = int(time.time() * 1000)
        json_data = json.dumps(data)
        '''7 put return data to log'''
        log('ebet_wallet', 'return: ' + json_data)
        return json_data

    def _save_bet_record(self, data, refund, params, user_id, api_info):
        if data['status'] == 200:
            '''1 prepare params'''
            bet_fields = []
            bet_field_amounts = []

            data_save = {}
            # data_save['uid'] = uuid.uuid3(uuid.NAMESPACE_DNS,'betamount')
            data_save['user_id'] = user_id
            data_save['game_id'] = 0
            data_save['game_type'] = 0
            data_save['game_round'] = refund['roundCode']
            data_save['bet_count'] = 1
            data_save['bet_amount'] = refund['refundMoney']
            data_save['bet_fields'] = bet_fields
            data_save['bet_field_amounts'] = bet_field_amounts
            data_save['order_id'] = refund['refundSeqNo']
            data_save['created'] = api_base.timestramp_to_date(params['timestamp'])
            data_save['status'] = 1
            
            bet_order = game_model.is_exist_bet(refund['refundSeqNo'])
            if not bet_order:  #no this order in our game_bet
                # 2 save to game_bet
                bet_order = game_model.save_bet_order(data_save)

            # 3 save money
            game_model.save_user_bal(user_id, refund['refundMoney'])

            # 4 set to redis
            data_redis = {}
            data_redis['user_id'] = user_id
            data_redis['order_id'] = refund['refundSeqNo']
            data_redis['amount'] = refund['refundMoney']
            data_redis['balance'] = float(api_info.balance)+float(refund['refundMoney'])
            data_redis['balance_before'] = data['moneyBefore']
            data_redis['create_date'] = data_save['created']
            data_redis['type'] = GAME_TYPE_DEC[28]
            data_redis['game_name'] = ''
            data_redis['round_code'] = refund['roundCode']
            data_redis['game_vendor'] = 'ebet'
            # db_redis.hset("user_bet_record", refund['refundSeqNo'], json.dumps(data_redis))
            send_ebet_game_record(json.dumps(data_redis))

            result_obj = {}
            result_obj['refundSeqNo'] = refund['roundCode']
            result_obj['status'] = 200
            data['moneyAfter'] = data_redis['balance']
            data['refundMoney'] += refund['refundMoney']
        return True, result_obj


class autoBatchRefund:
    def POST(self):
        '''1 get post'''
        params = str(web.data(), 'utf-8')
        '''2 put post to log'''
        print("autoBatchRefund")
        print(params)
        log('ebet_batch_refund', params)
        data = {}
        params = json.loads(params)

        '''3 prepare response data'''
        data['seqNo'] = params['seqNo']
        data['event'] = params['event']
        data['refundResultList'] = []

        '''3 vertify'''
        game_info = game_model.get_game_api_info('ebet', 'panda_')
        if game_info != False:
            game_info = game_info[0]
            event = params['event']
            signature = params['signature']
            signn = base64.b64decode(signature)
            rsa_pubKey = RSA.importKey(game_info.pub_key.strip())
            vertifier = PKCS1_v1_5.new(rsa_pubKey)
            wait_sign = str(params['channelId']) + str(params['timestamp'])
            hash_md5 = MD5.new(wait_sign.encode("utf-8"))
            vertify = vertifier.verify(hash_md5, signn)
        else:
            vertify = False
        

        '''4 judge post information'''
        if not vertify:  # wrong signature
            data['status'] = 4026
        # -------------------------(now explanatory note)
        # elif params['username'] != our_username:  #username is not exist
        #     data['status'] = 4037
        # elif params['channelId'] != _merchant_id:  #channel is not exist
        #     data['status'] = 1004
        # elif params['detail']['betList']['betMoney'] > our_user_money: # balance not enough
        #     data['status'] = 1003
        else:
            data['status'] = 200
        # -------------------------------------------

        '''5 deal refund operation'''
        refund_list = params['batchRefundList']
        for refund in refund_list:
            result, result_obj = self._save_bet_record(data, refund, params)
            if result:
                data['refundResultList'].append(result_obj)

        '''6 return response'''
        data['timestamp'] = int(time.time() * 1000)
#         data = {
#             'seqNo': params['seqNo'],
#             'event': params['event'],
#             'timestamp': int(time.time() * 1000),
#             'username': params['username'],
#             'moneyBefore': '',
#             'moneyAfter': '',
#             'refundMoney': '',
#             'refundResultList': {
#                 'username': '',
#                 'roundCode': '',
#                 'refundTotalMoney': '',
#                 'sucRefundSeqNoList': {
#                     'seqNo': '',
#                     'status': '',
#                 }
#             }
#         }
        json_data = json.dumps(data)
        '''7 put return data to log'''
        log('ebet_batch_refund', 'return: ' + json_data)
        return json_data

    def _save_bet_record(self, data, refund, params):
        if data['status'] == 200:
            result_obj = {}
            result_obj['username'] = refund['username']
            result_obj['roundCode'] = refund['roundCode']
            result_obj['sucRefundSeqNoList'] = []
            
            bet_order = game_model.is_exist_bet(refund['seqNo'])
            if bet_order:
                result_obj['refundTotalMoney'] = 0
                return False, result_obj
            sep_username = refund['username'].split('_')
            platform_pre = sep_username[0]+'_'
            param_username = sep_username[1]
            api_info = game_api(param_username, platform_pre)
            user_id = api_info.user_id
            if user_id == False:
                result_obj['refundTotalMoney'] = 0
                return False, result_obj
            
            '''1 prepare params'''
            bet_fields = []
            bet_field_amounts = []

            data_save = {}
            # data_save['uid'] = uuid.uuid3(uuid.NAMESPACE_DNS,'betamount')
            data_save['user_id'] = user_id
            data_save['game_id'] = 0
            data_save['game_type'] = 0
            data_save['game_round'] = refund['roundCode']
            data_save['bet_count'] = 1
            data_save['bet_amount'] = refund['refundMoney']
            data_save['bet_fields'] = bet_fields
            data_save['bet_field_amounts'] = bet_field_amounts
            data_save['order_id'] = refund['seqNo']
            data_save['created'] = api_base.timestramp_to_date(params['timestamp'])
            data_save['status'] = 1
            
            bet_order = game_model.save_bet_order(data_save)

            # 3 save money
            game_model.save_user_bal(user_id, refund['refundMoney'])

            # 4 set to redis
            data_redis = {}
            data_redis['user_id'] = user_id
            data_redis['order_id'] = refund['seqNo']
            data_redis['amount'] = refund['refundMoney']
            data_redis['balance'] = float(api_info.balance)+float(refund['refundMoney'])
            data_redis['balance_before'] = api_info.balance
            data_redis['create_date'] = data_save['created']
            data_redis['type'] = GAME_TYPE_DEC[28]
            data_redis['game_name'] = ''
            data_redis['round_code'] = refund['roundCode']
            data_redis['game_vendor'] = 'ebet'
            # db_redis.hset("user_bet_record", refund['seqNo'], json.dumps(data_redis))
            send_ebet_game_record(json.dumps(data_redis))

            result_obj['refundTotalMoney'] = refund['refundMoney']
            suc_result_obj = {}
            suc_result_obj['seqNo'] = refund['seqNo']
            suc_result_obj['status'] = 200
            result_obj['sucRefundSeqNoList'].append(suc_result_obj)

            log('ebet_batch_refund', 'save: amount %s Seq %s' %(refund['refundMoney'], refund['seqNo']))
        return True, result_obj


#__version__ = 'v1'
class game_api(game_api_basic):

    __version__ = 'v1'
    __file__ = 'ebet_v1'
    MOD_COMPANY = 'MOD_GAME_EBET'

#     _merchant_id = 920
#     _pubkey = '''-----BEGIN PUBLIC KEY-----
# MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAI/JXfdisVlaGUgDxNPQaDqvaHH3KD+9
# 1gc2LspRBlK8uSM8aFfojtqeXq7Gqq2N74zT6uaYOYoZf/OTTIN1/ZUCAwEAAQ==
# -----END PUBLIC KEY-----'''
#     _prikey = '''-----BEGIN PRIVATE KEY-----
# MIIBVQIBADANBgkqhkiG9w0BAQEFAASCAT8wggE7AgEAAkEAj8ld92KxWVoZSAPE
# 09BoOq9ocfcoP73WBzYuylEGUry5IzxoV+iO2p5ersaqrY3vjNPq5pg5ihl/85NM
# g3X9lQIDAQABAkEAg3jIJq9jIiQ0AZkQm+xvoVlJ0wr/DmlyDd4JIoy7j2IF3un7
# 0OL0SkVqM3KjWaOjrRLIuc4XTa/ob4zzso6WgQIhAN6CXGC7YlggVwvxWPnXBF0i
# IyS1dVO3Q2a+6rpGaqM9AiEApW2yPQ0omVbM3cirQ91cJUVKcRKSBK+e5OaTeGuM
# iTkCIAp15HPju07bTlxQX1d3hUv/k9lg8oAaCIAnD4/sSY0dAiBbqKQRX7EXBRkN
# 6Zm7SHM9016jt/5fyk7n1TnwhuafQQIhAJwLw1gtwlHeLz+qfF13xmWAZVtpYKlE
# IPDvRMkAtG6o
# -----END PRIVATE KEY-----'''
    _merchant_id = ""
    _pubkey = ""
    _prikey = ""
    _key = ""
    url = "http://icefoxcny.ebet.im:8888/"
    _password = "123456"
    _prefix = "" #用户名前缀
    currency = ""
    lang = "" '''语言'''
    username = ""
    api_game_id = ""

    def __init__(self, username,platform_prefix):
        self._prefix = "jll"
        '''获取游戏配置信息  表gameapi'''
        # db_game_api = db.game_api()
        # plat_api_info = db_game_api.get(company= 'ebet',platform= 'panda')

        # game_info = game_manager.game_manager(user_id).get_game_api_info('ebet',platform_prefix)
        # game_info = game_info[0]
        #
        # self._merchant_id = game_info.merchant_id.strip()
        # self._prefix = game_info.prefix_name.strip()
        # self._pubkey = game_info.pub_key.strip()
        # self._prikey = game_info.private_key.strip()
        # self.user_id = user_id
        #
        # user_info = game_manager.game_manager(user_id).get_user_info(user_id)
        # user_info = user_info[0]
        # self.username = user_info.username
        #
        # user_bal = game_manager.game_manager(user_id).get_user_bal(user_id)
        # user_bal = user_bal[0]
        # self.balance = user_bal.balance

        game_info = game_model.get_game_api_info('ebet',platform_prefix)
        if game_info != False:
            try:
                game_info = game_info[0]
                self._merchant_id = game_info.merchant_id.strip()
                self._prefix = game_info.prefix_name.strip()
                self._pubkey = game_info.pub_key.strip()
                self._prikey = game_info.private_key.strip()
                self.api_game_id = game_info.id
            except:
                log('game_api', 'game_info ebet ' + platform_prefix + " error")
                return None


        user_info = game_model.get_user_info(username)
        if user_info != False:
            try:
                user_info = user_info[0]
                self.username = user_info.username.strip()
                self.user_id = user_info.user_id
            except:
                log('game_api', 'user_info ' + username + " error")
                self.user_id = False
                return None

            user_bal = game_model.get_user_bal(self.user_id)
            if user_bal != False:
                try:
                    user_bal = user_bal[0]
                    self.balance = float(user_bal.balance)
                except:
                    log('game_api', 'error: user_balance, user_id:%s error' % user_info.user_id)
                    return None
        else:
            self.user_id = False


