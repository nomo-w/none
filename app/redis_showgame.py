from .myRedis import db_redis

SYNC_USER = "create_user"
SYNC_FINANCE = "finance"

def sync_redis_bet():
    '''同步游戏数据到管理后台'''
            
    kkk = db_redis.hkeys("user_bet_record")
    print("user_bet_record")
    for k in kkk:
        print("key: %s" % k)
        print(db_redis.hget("user_bet_record", k))
    



if __name__ == '__main__':
    sync_redis_bet()
