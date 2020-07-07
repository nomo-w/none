from .all_config import *


class GaotongPay:
    '''***的接口数据'''
    # 子商户号
    MEMCODE = '*****'
    def __init__(self):
        # 厂商名
        self.NAME = '高通'
        # 公钥
        self.PUBKEY = '************'
        # 私钥
        self.PRIKEY = '***************'
        # 第三方地址
        self.BASE_API = '********************'
        # 加密格式
        self.SIGN_CHATSET = 'utf-8'
        # 加密方法
        self.SIGN_METHOD = 'MD5'
        # 请求头
        self.HEADERS = DEFAULT_HEADERS
        # 需要加密的数据格式
        self.SIGN = 'partner={partner}&banktype={channel}&paymoney={amount}&ordernumber={orderNo}&callbackurl=%s{key}' % CALLBACK
        # 所需参数
        self.PARAMS = '?partner={partner}&banktype={bank}&paymoney={money}&ordernumber={order}&callbackurl=%s&sign={sign}' % CALLBACK

        self.CALLBACK_SIGN = 'partner={partner}&ordernumber={order}&orderstatus={orderstatus}&paymoney={money}{key}'
        # 支付通道码
        self.CHANNEL_CODE = {
            'ALIPAY': 'ALIPAY',              # 支付宝
            'ALIPAYWAP': 'ALIPAYWAP',        # 手机支付宝WAP
            'TENPAY': 'TENPAY',              # 财付通
            'WEIXIN': 'WEIXIN',              # 微信
            'WEIXINWAP': 'WEIXINWAP',        # 手机微信WAP
            'QQPAY': 'QQPAY',                # QQ钱包
            'QQPAYWAP': 'QQPAYWAP',          # 手机QQ钱包WAP
            'UNIONPAY': 'UNIONPAY',          # 银联扫码
            'UNIONWAPPAY': 'UNIONWAPPAY',    # 银联快捷
            'FRONTFASTPAY': 'FRONTFASTPAY',  # 无卡快捷
        }
        # 本地定义的支付码
        self.LOCAL_CODE = {
            '401': self.CHANNEL_CODE['ALIPAY'],         # 支付宝
            '402': self.CHANNEL_CODE['ALIPAYWAP'],      # 手机支付宝WAP
            '403': self.CHANNEL_CODE['TENPAY'],         # 财付通
            '404': self.CHANNEL_CODE['WEIXIN'],         # 微信
            '405': self.CHANNEL_CODE['WEIXINWAP'],      # 手机微信WAP
            '406': self.CHANNEL_CODE['QQPAY'],          # QQ钱包
            '407': self.CHANNEL_CODE['QQPAYWAP'],       # 手机QQ钱包WAP
            '408': self.CHANNEL_CODE['UNIONPAY'],       # 银联扫码
            '409': self.CHANNEL_CODE['UNIONWAPPAY'],    # 银联快捷
            '410': self.CHANNEL_CODE['FRONTFASTPAY'],   # 无卡快捷
        }
