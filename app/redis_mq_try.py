##################### 这个文件没有用 #################################################
import time

from .myRedis import db_redis, send_ebet_game_record, get_ebet_game_record

SYNC_USER = "create_user"
SYNC_FINANCE = "finance"


def sync_redis_bet():
    '''同步游戏数据到管理后台'''

    i = 20
    while True:
        i -= 1
        time_str = time.strftime("%Y-%m-%d %H:%M:%S")
        send_ebet_game_record(time_str)
        print("send ebet game %s" % time_str)
        time.sleep(1)
        if i < 0:
            break
        #print(db_redis.hget("user_bet_record", k))
    
def get_redis_bet():
    
    i = 20
    while True:
        i -= 1
        str = get_ebet_game_record()
        print("get ebet game: %s" % str)
        time.sleep(1)
        if i < 0:
            break

if __name__ == '__main__':
    sync_redis_bet()
    time.sleep(5)
    get_redis_bet()
    
