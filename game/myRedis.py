import redis
from game.all_config import *

class RedisClient(redis.StrictRedis):
    '''单例模式'''
    _instance = {}
 
    def __init__(self, server):
        redis.StrictRedis.__init__(self, **server)
 
    def __new__(cls, *args):
        if str(args) not in cls._instance:
            cls._instance[str(args)] = super(RedisClient, cls).__new__(cls)
        return cls._instance[str(args)]


def send_ebet_game_record(data, KEY=TO_BALANCE_KEY):
    '''存入消息队列'''
    db_redis.rpush(KEY, data)

def get_queue_record(key):
    '''从消息队列中取, 移除并返回列表的第一个元素'''
    return db_redis.lpop(key)
 
db_redis = RedisClient(REDIS_CACHE)
