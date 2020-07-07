import json
import time
import traceback

import db
# from communication.redis import get_queue_record
from .myRedis import get_queue_record
# from game_package.game_api.api_base import log

SYNC_USER_QUEUE = "create_user_queue"
SYNC_FINANCE_QUEUE = "finance_queue"


def sync_redis_bet():
    '''同步管理后台数据到游戏库'''
    print("start sync redis create_user, change_balance,")
    try:
        # todo 没有事务处理
        while True:
            # 同步创建用户
            # print("sync create_user")
            while True:
                try:
                    # 查看是否有用户
                    user_str = get_queue_record(SYNC_USER_QUEUE)
                    if user_str:
                        print(user_str)
                        user_json = json.loads(user_str)
                        user_id = user_json['user_id']
                        user_name = user_json['user_name']
                        user_status = user_json['status']
            
                        users = db.username_login_stats()
                        get_count = users.get_count(user_id=user_id)
                        if get_count > 0:
                            # log('redis_sync', 'error create_user: user is exist, user_id:%s user_name:%s status:%s ' % (user_id, user_name, user_status))
                            print('redis_sync', 'error create_user: user is exist, user_id:%s user_name:%s status:%s ' % (user_id, user_name, user_status))
                        else:
                            users.add(
                                user_id=user_id,
                                username=user_name,
                            )
                            # log('redis_sync', 'success create_user: user_id:%s user_name:%s status:%s ' % (user_id, user_name, user_status))
                            print('redis_sync', 'success create_user: user_id:%s user_name:%s status:%s ' % (user_id, user_name, user_status))

                        user_stats = db.user_transaction_stats()
                        get_first = user_stats.get_first(user_id=user_id)
                        if isinstance(get_first, int) and get_first <= 0:
                            now_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            user_stats.add(
                                user_id=user_id,
                                created_at=now_str,
                                updated_at=now_str,
                                balance=0
                            )
                    else:
                        break
                except Exception as e:
                    print(e)
                    # log('redis_sync', 'error create_user: %s ' % traceback.format_exc())
                    print('redis_sync', 'error create_user: %s ' % traceback.format_exc())

            
        #         kkk = db_redis.hkeys("user_bet_record")
        #         print("user_bet_record")
        #         for k in kkk:
        #             print("key: %s" % k)
        #             print(db_redis.hget("user_bet_record", k))
    
            # 同步余额变化
            # print("sync finance")
            while True:
                try:
                    record_str = get_queue_record(SYNC_FINANCE_QUEUE)
                    if record_str:
                        print(record_str)
                        record_json = json.loads(record_str)
                        user_id = record_json['user_id']
                        balance = record_json['balance']
                        balance_before = record_json['balance_before']
                        amount = record_json['amount']
                        order_id = record_json['order_id']
                        
                        user_stats = db.user_transaction_stats()
                        get_first = user_stats.get_first(user_id=user_id)
                        if isinstance(get_first, int) and get_first <= 0:
                            now_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            user_stats.add(
                                user_id=user_id,
                                created_at=now_str,
                                updated_at=now_str,
                                balance=balance
                            )
                        else:
                            if get_first["balance"] != balance_before:
                                # log('redis_sync_warn', 'error finance: user_id:%s local balance:%s != remote before balance:%s blance:%s amount:%s' % (user_id, get_first["balance"], balance_before, balance, amount))
                                print('redis_sync_warn', 'error finance: user_id:%s local balance:%s != remote before balance:%s blance:%s amount:%s' % (user_id, get_first["balance"], balance_before, balance, amount))
                            user_stats.update(
                                condition_user_id=user_id,
                                balance=balance
                            )
                            # log('redis_sync', 'success finance: user_id:%s new balance:%s before balance:%s amount:%s ' % (user_id, balance, balance_before, amount))
                            print('redis_sync', 'success finance: user_id:%s new balance:%s before balance:%s amount:%s ' % (user_id, balance, balance_before, amount))
                    else:
                        break
                except Exception as e:
                    print(e)
                    # log('redis_sync', 'error finance: %s ' % traceback.format_exc())
                    print('redis_sync', 'error finance: %s ' % traceback.format_exc())

            time.sleep(2)
    except Exception as e:
        print(e)
        # log('redis_sync', 'error : %s ' % traceback.format_exc())
        print('redis_sync', 'error : %s ' % traceback.format_exc())


if __name__ == '__main__':
    sync_redis_bet()