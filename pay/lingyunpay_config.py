from .all_config import *


class LingyunPay:
    '''凌云付的接口数据'''
    MEMCODE = '*************'
    def __init__(self):
        # 厂商名
        self.NAME = '凌云付'
        # 公钥
        self.PUBKEY = '*************************************************************'
        # 私钥
        self.PRIKEY = '''***********************************'''
        # 第三方地址
        self.BASE_API = '*******************'
        # 支付api地址
        self.BUY_API = self.BASE_API + '/api/pay/getForm'
        # 加密格式
        self.SIGN_CHATSET = 'utf-8'
        # 加密方法
        self.SIGN_METHOD = 'MD5withRSA'
        # 请求头
        self.HEADERS = DEFAULT_HEADERS
        self.HEADERS['Content-Type'] = 'application/x-www-form-urlencoded'
        # 获取订单api地址
        self.GET_ORDER_API = self.BASE_API + '/api/pay/querryOrder'
        # 需要加密的数据格式
        self.SIGN = 'memCode={memcode}&channel={channel}&amount={amount}&orderNo={orderNo}&notifyUrl=%s' % CALLBACK
        self.CALLBACK_SIGN = 'memCode={m}&orderNo={o}&state={s}&amount={a}'
        # 所需参数
        self.PARAMS = {
            "memCode": "",
            "channel": "",
            "amount": "",
            "orderNo": "",
            "notifyUrl": CALLBACK,
            "sign": ""
        }
        # 支付通道码
        self.CHANNEL_CODE = {
            'alipay scan': '0001',
            'unionpay scan': '0002',
            'checkout counter': '0003',
            'wechat scan': '0004',
            'alipay h5': '0005',
            'wechat h5': '0006',
            'unionpay': '0007',
            'netbank': '0008',
        }
        # 本地定义的支付码
        self.LOCAL_CODE = {
            '005': self.CHANNEL_CODE['alipay h5'],  # 支付宝H5
            '007': self.CHANNEL_CODE['alipay scan'],  # 支付宝扫码
            '008': self.CHANNEL_CODE['unionpay'],  # 银联快捷
            '006': self.CHANNEL_CODE['wechat h5'],  # 微信H5
            '004': self.CHANNEL_CODE['wechat scan'],  # 微信扫码
            '003': self.CHANNEL_CODE['checkout counter'],  # 收银台
            '002': self.CHANNEL_CODE['unionpay scan'],  # 银联扫码
            '001': self.CHANNEL_CODE['netbank']  # 网银支付
        }
        # 平台返回状态码
        self.STATUS_CODE = {
            'success': '1000000',
            'duplicate order number': '1000002',
            'sub-merchant is frozen': '1000008',
            'verify failed': '1000044',
            'service exception': '1000500',
            'error': '1000404',
            'close': '9999999',
        }