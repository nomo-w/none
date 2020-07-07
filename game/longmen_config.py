CONTENT = 'application/json'

DEFAULT_HEADERS = {
    'User-Agent': "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    # 'Content-Type': 'application/json',
    'Accept': '*/*',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
    'Content-Length': '278',
    'Accept-Encoding': 'gzip,deflate',
}

MD5KEY = '36879ec23fb55e5ce1f04d33b0bfc55b'

# 第三方游戏的base URL
BASE_URL = 'http://*******************:8003'
# 获取游戏连接API POST
GET_GAME_API = BASE_URL + '/game/getToken'
# 获取游戏种类API(查看一共有几种类型) POST
GET_GAME_TYPE_API = BASE_URL + '/manager/getGameKindList'
# 根据游戏种类获取游戏厂商API(通过游戏类型获取该游戏类型有几种厂商) POST
GET_GAME_VENDOR_API = BASE_URL + '/manager/***************'
# 查询游戏代码
GET_GAME_CODE_API = BASE_URL + '/manager/getGameByCondition'
# 查询****钱包余额API POST
GET_PLAYER_BALANCE_API = BASE_URL + '/money/queryBlance'
# ****钱包充值API POST
RECHARGE_API = BASE_URL + '/money/rechargeBlance'
# *****钱包提现API POST
WITHDRAW_API = BASE_URL + '/money/withdrawBlance'
# *****钱包订单查询 POST
WALLET_ORDER_API = BASE_URL + '/money/queryByOrderNum'
# *****钱包日志查询 POST
WALLET_LOG_API = BASE_URL + '/money/queryMoneyLog'
# 查询用户***** POST
GET_BETRECORDS_API = BASE_URL + '/game/********'
# 查询用户在游戏商的余额 POST
GET_BALANCE_BY_VENDOR_API = BASE_URL + '/game/getPlayerBalance'
# 查询用户在所有游戏商的余额 POST
GET_ALL_BALANCE_API = BASE_URL + '/game/oneKeyQueryBalance'
# 查询用户的**********
GET_BET_API = BASE_URL + '/game/*******************'

PLAYERWITHDRAW_API = BASE_URL + '/game/playerWithdraw'
# 第三方游戏返回的状态码
OK_STATUS = '200'
# 商户标识
CLIENTCODE = 'icefox'