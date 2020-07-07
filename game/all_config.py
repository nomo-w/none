# 接口返回状态定义
RETURN_STATUS = {
    'good': 'success',
    'not good': 'failed',
}

# 同步用户redis字段名
USER_KEY = "create_user_queue"
# 同步金额变动redis字段名
BALANCE_KEY = 'finance_queue'
# 同步**信息redis字段名
BET_KEY = "user_**_queue"
# 同步****金额变动redis字段名
TO_BALANCE_KEY = "user_balance_queue"
# 用户金额表postgresql
USER_BALANCE_TB = 'test_game_userbalance'
# 用户表postgresql
USER_TB = 'test_game_user'
# 用户**表postgresql
USER_BET_TB = 'test_game_*******'

# redis数据库信息
REDIS_CACHE = {
    "host": '**********',
    "port": '6379',
    "db": 0,
    "password": ''
}