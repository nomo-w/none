from django.http import HttpResponse
from django.views.generic import View
from .models import User, AccountChange, UserBalance
from .myRedis import send_ebet_game_record
from .api import GAME_API, MyError
from .longmen_config import *
from .all_config import *
import json
import time
import traceback

# Create your views here.


class Login(View):
    def post(self, request):
        '''获取游戏连接'''
        try:
            data = json.loads(request.body.decode())
            print()
            print('Get game request: ', data)
            username = data['username']
            vendorCode = data['vendorCode']
            gameCode = data.get('gameCode', None)
            terminalType = data.get('terminalType', None)
            if 'HTTP_X_FORWARDED_FOR' in request.META:
                ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                ip = request.META['REMOTE_ADDR']

            # 查询用户是否存在
            userinfo = User.objects.get(username=username)
            balance_obj = UserBalance.objects.get(pkNo=userinfo.pkNo)
            # vendor = GameVendor.objects.get(vendorCode=vendorCode, is_active=True)

            ###############################
            # 计算金额
            recharge_amount = [101.00, balance_obj.balance][balance_obj.balance < 101.00] \
                if vendorCode == 'gm-ag' else balance_obj.balance
            # 执行
            resp = GAME_API.recharge_withdraw(RECHARGE_API, recharge_amount, username)
            print('Recharge value is: ', resp)
            ############################### 修改数据库postgresql
            # 钱用户余额
            befor = balance_obj.balance
            # 将用户的余额减去的钱数
            balance_obj.balance = float('%.2f' % (balance_obj.balance - recharge_amount))
            # 保存用户金额变动信息到数据库
            balance_obj.save()
            # 创建一条订单
            AccountChange.objects.create(
                user=userinfo,
                orderNum=resp['result']['orderNum'],
                vendor_code=vendorCode,
                transaction='-%.2f' % recharge_amount,
                befor_balance=befor,
                after_balance=float('%.2f' % (befor - recharge_amount)),
                game_code=gameCode
            )
            ############################### 同步redis数据
            redis_data = {
                'user_id': userinfo.pkNo,
                'balance_before': befor,
                'balance': float('%.2f' % (befor - recharge_amount)),
                'amount': recharge_amount,
                'order_id': resp['result']['orderNum'],
                'type': 'game-recharge',
                'created_date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            }
            # 写入redis
            send_ebet_game_record(json.dumps(redis_data))

            # 获取游戏连接
            resp = GAME_API.get_game(username, vendorCode, ip, gameCode=gameCode, terminalType=terminalType)
            print('Game response is: ', resp)
        except (KeyError, json.JSONDecodeError):
            return HttpResponse(json.dumps(GAME_API.handle_httpresponse('Parameter error')))
        except User.DoesNotExist:
            return HttpResponse(json.dumps(GAME_API.handle_httpresponse('Not found user')))
        except UserBalance.DoesNotExist:
            return HttpResponse(json.dumps(GAME_API.handle_httpresponse('Service error')))
        except MyError as e:
            return HttpResponse(e)
        except Exception as e:
            print('SERVICE ERROR')
            traceback.print_exc()
            return HttpResponse(json.dumps(GAME_API.handle_httpresponse('Service error [%s]' % e)))
        else:
            return HttpResponse(json.dumps(resp))


class Withdraw(View):
    def post(self, request):

        try:
            data = json.loads(request.body.decode())
            print()
            print('Withdraw request: ', data)
            username = data['username']
            vendors = data.get('vendors', None)
            if 'HTTP_X_FORWARDED_FOR' in request.META:
                ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                ip = request.META['REMOTE_ADDR']

            # 查询用户是否存在
            userinfo = User.objects.get(username=username)
            balance_obj = UserBalance.objects.get(pkNo=userinfo.pkNo)

            # 将厂商的钱钱包里
            GAME_API.withdraw_all_vendor(username, ip)
            #
            player_balance = GAME_API.queryBalance(username)
            print('User wallet value is: ', player_balance)
            # 将余额全部取出
            resp = GAME_API.recharge_withdraw(WITHDRAW_API, player_balance['result']['money'], username)
            print('Withdraw response is: ', resp)
            ############################# 修改数据库
            # 修改用户余额表
            befor = balance_obj.balance
            after = befor + player_balance['result']['money']
            balance_obj.balance = after
            balance_obj.save()
            ############################# 创建订单
            AccountChange.objects.create(user=userinfo, transaction='+%.2f' % player_balance['result']['money'],
                orderNum=resp['result']['orderNum'], befor_balance=befor, after_balance=after)
            ############################# 同步redis
            redis_data = {
                'user_id': userinfo.pkNo,
                'balance_before': befor,
                'balance': after,
                'amount': player_balance['result']['money'],
                'order_id': resp['result']['orderNum'],
                'type': 'game-withdraw',
                'created_date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            }
            send_ebet_game_record(json.dumps(redis_data))
        except (KeyError, json.JSONDecodeError):
            return HttpResponse(json.dumps(GAME_API.handle_httpresponse('Parameter error')))
        except User.DoesNotExist:
            return HttpResponse(json.dumps(GAME_API.handle_httpresponse('Not found user')))
        except UserBalance.DoesNotExist:
            return HttpResponse(json.dumps(GAME_API.handle_httpresponse('Service error')))
        except MyError as e:
            return HttpResponse(e)
        except Exception as e:
            print('SERVICE ERROR')
            traceback.print_exc()
            return HttpResponse(json.dumps(GAME_API.handle_httpresponse('Service error [%s]' % e)))
        else:
            return HttpResponse(json.dumps(resp))


class GetWallet(View):
    def post(self, request):

        try:
            data = json.loads(request.body.decode())
            print()
            print('Query wallet request: ', data)
            user = data['username']
            walletType = data.get('walletType')
            if 'HTTP_X_FORWARDED_FOR' in request.META:
                ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                ip = request.META['REMOTE_ADDR']

            #
            GAME_API.withdraw_all_vendor(user, ip)

            if walletType == 'longmen':
                #
                resp = GAME_API.queryBalance(user)
                print('Wallet response is: ', resp)
                resp['walletType'] = 'longmen'
            else:
                raise MyError(json.dumps(GAME_API.handle_httpresponse('Not found walletType')))
        except (KeyError, json.JSONDecodeError):
            return HttpResponse(json.dumps(GAME_API.handle_httpresponse('Parameter error')))
        except User.DoesNotExist:
            return HttpResponse(json.dumps(GAME_API.handle_httpresponse('Not found user')))
        except UserBalance.DoesNotExist:
            return HttpResponse(json.dumps(GAME_API.handle_httpresponse('Service error')))
        except MyError as e:
            return HttpResponse(e)
        except Exception as e:
            print('SERVICE ERROR')
            traceback.print_exc()
            return HttpResponse(json.dumps(GAME_API.handle_httpresponse('Service error [%s]' % e)))
        else:
            return HttpResponse(json.dumps(resp))
