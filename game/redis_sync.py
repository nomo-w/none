import json
import time
import traceback
from game.all_config import USER_BALANCE_TB, USER_KEY, BALANCE_KEY, BET_KEY
from game.api import GAME_API, Postgresql
from game.myRedis import get_queue_record, send_ebet_game_record


def retry_zsq(func_name):
    def inner1(func):
        def inner2(*args, **kwargs):
            while True:
                try:
                    func(*args, **kwargs)
                except Exception:
                    print('Func [%s] error.' % func_name)
                    traceback.print_exc()
                    # print('重新运行该函数')
        return inner2
    return inner1

# BET_KEY = 'user_bet_queue_test'
@retry_zsq('sync_user')
def do_sync_user(postgresql_obj=Postgresql()):
    while True:
        while True:
            user_list = get_queue_record(USER_KEY)
            if user_list:
                print('发现用户变动数据', user_list)
                value = json.loads(user_list.decode())
                if not postgresql_obj.select_(value['user_id']):
                    postgresql_obj.create_(value)
                    ###################
                    postgresql_obj.create_({'user_id': value['user_id'], 'balance': 0.00}, USER_BALANCE_TB)
                    #############
                    postgresql_obj.commit_()
                    # postgresql_obj.close_()
                else:
                    print('[%s]用户已经存在, 不会继续创建' % value['user_name'])
            else:
                break

        while True:
            balance_list = get_queue_record(BALANCE_KEY)
            if balance_list:
                print('发现金额变动数据', balance_list)
                value = json.loads(balance_list.decode())
                if postgresql_obj.select_(value['user_id'], USER_BALANCE_TB):
                    postgresql_obj.update_(value, USER_BALANCE_TB)
                else:
                    postgresql_obj.create_(value, USER_BALANCE_TB)
                postgresql_obj.commit_()
            else:
                break


def handle_bet_to_db(bet_data):
    # _ = dict()
    # _['vendor_data'] = bet_data.pop('betRaw')
    # _['longmen_data'] = bet_data
    # _['username'] = bet_data['username']
    # Postgresql.create_(_, 'test_game_betrecords')

    _ = dict()
    posg_obj = Postgresql()
    userid = posg_obj.select_(bet_data['username'][3:], key='username')
    posg_obj.close_()
    _['user_id'] = userid[0][0]
    _['created_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(bet_data['createdAt']/1000))
    if bet_data['betAmount'] == None:
        _['amount'] = bet_data['payoff']
    else:
        _['amount'] = -bet_data['betAmount']
    _['game_vendor'] = bet_data['vendorCode']
    _['game_name'] = bet_data['gameCode']
    _['type'] = ['bet', 'payoff'][bet_data['betAmount'] == None]
    _['order_id'] = '%s-%s-%s-%s' % (_['game_vendor'], _['game_name'],
        time.strftime('%Y%m%d%H%M%S', time.localtime(bet_data['createdAt']/1000)), _['user_id'])
    _['remark'] = '%s-%s-%s' % (_['game_vendor'], _['game_name'], _['user_id'])
    if _['game_name'] == '':
        _['game_name'] = 'lobby'
    if bet_data['betAmount'] and bet_data['payoff']:
        _['amount'] = -bet_data['betAmount']
        _['type'] = 'bet'
        # print('数据库数据为', _)
        send_ebet_game_record(json.dumps(_), BET_KEY)
        _['amount'] = bet_data['payoff']
        _['type'] = 'payoff'
        # print('数据库数据为', _)
        send_ebet_game_record(json.dumps(_), BET_KEY)
    else:
        # print('数据库数据为', _)
        send_ebet_game_record(json.dumps(_), BET_KEY)


@retry_zsq('sync_bet')
def do_sync_bet(intervals=2*60):
    start_time = int(round((time.time() - intervals) * 1000))
    while True:
        end_t = int(round(time.time() * 1000))
        #
        vendor_set = GAME_API.getAllVendors()
        for i in vendor_set:
            #
            bet_data = GAME_API.getBetRecords(i, startTimeBet=start_time, endTimeBet=end_t, pageNum='1', pageSize='200')

            for i1 in bet_data['result']['list']:
                print('Write to database: ', i1)
                handle_bet_to_db(i1)
            for i1 in bet_data['result']['navigatepageNums'][1:]:
                bet_data1 = GAME_API.getBetRecords(i, startTimeBet=start_time,
                            endTimeBet=end_t, pageNum=str(i1), pageSize='200')
                for i2 in bet_data1['result']['list']:
                    # print('收到信息写入数据库', i2)
                    print('Pagination [%s]' % i1)
                    print('Write to database: ', i2)
                    handle_bet_to_db(i2)
        start_time = end_t
        time.sleep(intervals)


def test_sync_bet():
    while True:
        # 获取游戏厂商
        vendor_set = GAME_API.getAllVendors()
        for i in vendor_set:
            bet_data = GAME_API.getBetRecords(i, pageNum='1', pageSize='200', username='123232')
            print('[%s]是  %s: ' % (i, bet_data))
            for i1 in bet_data['result']['list']:
                handle_bet_to_db(i1)
            for i1 in bet_data['result']['navigatepageNums'][1:]:
                bet_data1 = GAME_API.getBetRecords(i, pageNum=str(i1), pageSize='200', username='123232')
                for i2 in bet_data1['result']['list']:
                    handle_bet_to_db(i2)
        time.sleep(60*5)

