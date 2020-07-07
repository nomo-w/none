from django.http import HttpResponse
from django.views.generic import View
from .all_config import *
from .lingyunpay_config import LingyunPay
from .gaotongpay_config import GaotongPay
from .api import API, MyError
import json
import traceback

# from .models import Payment_type, Payment_vendor, Payment_channel

# Create your views here.


def dispatcher(vendor=None, memcode=None):
    if vendor == '凌云付' or memcode == LingyunPay.MEMCODE:
        _ = LingyunPay()
    elif vendor == '高通' or memcode == GaotongPay.MEMCODE:
        _ = GaotongPay()
    else:
        raise MyError(json.dumps(API.handle_httpresponse('Not found vendor.')))
    return _


class Callback(View):
    '''回调接口'''
    def post(self, request):
        # 不确定平台返回的是哪种数据格式,所以要判断一下
        # try:
        #     data = request.POST.dict()
        # except Exception:
        try:
            data = json.loads(request.body.decode())
            memCode = data['memCode']
            orderNo = data['orderNo']
            state = data['state']
            amount = data['amount']
            orderTime = data['orderTime']
            notifyTime = data['notifyTime']
            sign = data['sign']

            vendor_obj = dispatcher(memcode=memCode)
            # 登录获取token并把token加入headers里, 登录默认使用的Jay用户
            headers = API.login_graphql()
            # 查询厂商graphql
            vendor_data = API.request_graphql(
                headers,
                {"query": QUERY_VENDOR_GRAPHQL.format(key_value='merchantNumber: "%s"' % memCode)},
                'get_vendor'
            )
            vendor_obj = dispatcher(memcode=memCode)
            vendor_obj.MEMCODE = vendor_data['merchantNumber']
            vendor_obj.PUBKEY = vendor_data['merchantCertificate']
            vendor_obj.PRIKEY = vendor_data['merchantKey']
            # 根据厂商类型生成对应的签名原串
            if vendor_obj.NAME == '凌云付':
                origin_sign = vendor_obj.CALLBACK_SIGN.format(m=memCode, o=orderNo, s=state, a=amount)

            # 验签
            if API.verify_(sign, origin_sign, vendor_obj.SIGN_METHOD, vendor_obj.PUBKEY, vendor_obj.SIGN_CHATSET):
                orderinfo = API.update_order_status(vendor_obj.NAME, state, amount, orderNo)
                print('修改后的订单信息为', orderinfo)

                # 根据厂商类型生成对应的成功返回值
                if vendor_obj.NAME == '凌云付':
                    value = 'success'
            # 验签失败返回错误
            else:
                raise MyError('error')
        except MyError as e:
            return HttpResponse(e)
        except Exception:
            traceback.print_exc()
            return HttpResponse('error')
        else:
            return HttpResponse(value)

    def get(self, request):
        try:
            data = request.GET.dict()
            print('收到参数', data)
            partner = data.get('partner')
            ordernumber = data.get('ordernumber')
            orderstatus = str(data.get('orderstatus'))
            paymoney = data.get('paymoney')
            sysnumber = data.get('sysnumber')
            attach = data.get('attach')
            sign = data.get('sign')

            # 登录获取token并把token加入headers里, 登录默认使用的Jay用户
            headers = API.login_graphql()
            # 查询厂商graphql
            vendor_data = API.request_graphql(
                headers,
                {"query": QUERY_VENDOR_GRAPHQL % 'merchantNumber: "{}"'.format(partner)},
                'get_vendor'
            )
            vendor_obj = dispatcher(memcode=partner)
            vendor_obj.MEMCODE = vendor_data['merchantNumber']
            vendor_obj.PUBKEY = vendor_data['merchantCertificate']
            vendor_obj.PRIKEY = vendor_data['merchantKey']
            if vendor_obj.NAME == '高通':
                origin_sign = vendor_obj.CALLBACK_SIGN.format(
                    partner=vendor_obj.MEMCODE,
                    order=ordernumber,
                    orderstatus=orderstatus,
                    money=paymoney,
                    key=vendor_obj.PUBKEY
                )
            if API.verify_(sign, origin_sign, vendor_obj.SIGN_METHOD, vendor_obj.PUBKEY, vendor_obj.SIGN_CHATSET):
                orderinfo = API.update_order_status(vendor_obj.NAME, orderstatus, paymoney, ordernumber)
                print('修改后的订单信息为', orderinfo)
                if vendor_obj.NAME == '高通':
                    value = 'ok'
            else:
                raise MyError(json.dumps(API.handle_httpresponse('Verify failed')))
        except MyError as e:
            return HttpResponse(e)
        except Exception:
            traceback.print_exc()
            return HttpResponse('error')
        else:
            return HttpResponse(value)


class Deposit(View):
    '''支付接口'''
    def post(self, request):
        try:
            data = json.loads(request.body.decode())
            print()
            print('Receive deposit: ', data)
            bank_id = data['channel']
            user = data['user']
            amount = data['amount']

            # 登录获取token并把token加入headers里, 登录默认使用的Jay用户
            headers = API.login_graphql()
            # 查询用户是否存在
            userinfo = API.request_graphql(headers, {"query": QUERY_USER_GRAPHQL % user}, 'user')
            # 查询是否存在该支付方法
            vendor_info = API.request_graphql(headers, {'query': CHECK_VENDOR_GRAPHQL % bank_id}, 'bank')
            print('The user information found is: ', userinfo)
            print('The bank information found is: ', vendor_info)
            # 请求graphql, 创建订单, 会返回订单号
            # 用户要填user的graphql的id字段VXNlck5vZGU6MTA4NA==
            orderInfo = API.request_graphql(
                headers,
                {"query": CREATE_ORDER_GRAPHQL % (
                    userinfo['id'],
                    amount
                )},
                'create_order'
            )
            print('The order info create is: ', orderInfo)
            # 实例化厂商对象, 生成请求参数使用
            vendor_obj = dispatcher(vendor_info['payVendor']['name'])
            # 查询厂商graphql
            vendor_data = API.request_graphql(
                headers,
                {"query": QUERY_VENDOR_GRAPHQL % 'name: "{}"'.format(vendor_obj.NAME)},
                'get_vendor'
            )
            vendor_obj.MEMCODE = vendor_data['merchantNumber']
            vendor_obj.PUBKEY = vendor_data['merchantCertificate']
            vendor_obj.PRIKEY = vendor_data['merchantKey']
            param = API.handle_param(
                vendor_obj,
                amount,
                orderInfo['orderId'],
                vendor_info['businessCode']
            )

            if vendor_obj.NAME == '凌云付':
                value = API.do_pay(param, vendor_obj.BUY_API, vendor_obj.HEADERS)
            elif vendor_obj.NAME == '高通':
                value = {'status': RETURN_STATUS['good'], 'result': vendor_obj.BASE_API + param}
        except MyError as e:
            return HttpResponse(e)
        except (KeyError, json.JSONDecodeError):
            return HttpResponse(json.dumps(API.handle_httpresponse('Parameter error')))
        except Exception as e:
            print('SERVICE ERROR')
            traceback.print_exc()
            return HttpResponse(json.dumps(API.handle_httpresponse('Service error [%s]' % e)))
        else:
            return HttpResponse(json.dumps(value))
