from django.db import models
from django.utils import timezone

# Create your models here.


class GameType(models.Model):
    '''游戏种类表'''
    code = models.CharField(max_length=255, verbose_name='种类代码')
    name = models.CharField(max_length=255, verbose_name='游戏名')
    lang_en = models.CharField(max_length=255, null=True, blank=True, verbose_name='游戏英文名')
    lang_zh = models.CharField(max_length=255, null=True, blank=True, verbose_name='游戏中文名')
    creator = models.CharField(max_length=255, verbose_name='创建者')
    createAt = models.CharField(max_length=255, null=True, blank=True)
    updateAt = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)


class GameVendor(models.Model):
    '''游戏厂商表'''
    vendorName = models.CharField(max_length=255, verbose_name='游戏厂商')
    vendorCode = models.CharField(max_length=255, verbose_name='厂商编码')
    gameKindName = models.CharField(max_length=255, verbose_name='游戏名')
    gameKindCode = models.CharField(max_length=255, verbose_name='游戏码')
    gameAlias = models.CharField(max_length=255, verbose_name='别名')
    pictureUrl = models.CharField(max_length=255, blank=True, null=True, verbose_name='图片地址')
    hallUrl = models.CharField(max_length=255, blank=True, null=True)
    gameType = models.ForeignKey(GameType, on_delete=models.CASCADE, related_name='vendor', verbose_name='厂商的游戏类型')
    is_active = models.BooleanField(default=True)


class GameCode(models.Model):
    '''游戏编号表'''
    vendorId = models.CharField(max_length=255, blank=True, null=True)
    gameKindId = models.CharField(max_length=255, blank=True, null=True)
    gameCode = models.CharField(max_length=255, blank=True, null=True, verbose_name='游戏代码')
    gameName = models.CharField(max_length=255, verbose_name='游戏名')
    gameStatus = models.CharField(max_length=255, blank=True, null=True)
    pc = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=255, blank=True, null=True)
    pictureUrl = models.CharField(max_length=255, blank=True, null=True)
    lang = models.CharField(max_length=255, blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)
    createdAt = models.CharField(max_length=255)
    updatedAt = models.CharField(max_length=255, blank=True, null=True)
    deletedAt = models.CharField(max_length=255, blank=True, null=True)
    vendorCode = models.CharField(max_length=255)
    vendorName = models.CharField(max_length=255)
    gameKindCode = models.CharField(max_length=255)
    gameKindName = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)


class User(models.Model):
    '''用户表跟主库同步'''
    pkNo = models.CharField(max_length=255, verbose_name='用户id')
    username = models.CharField(max_length=500, verbose_name='用户名')
    create_date = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    is_active = models.BooleanField(default=True, verbose_name='是否可用')
    # balance = models.FloatField(null=True, blank=True, verbose_name='用户钱包')


class UserBalance(models.Model):
    '''用户金额表'''
    pkNo = models.CharField(max_length=255, verbose_name='用户id')
    balance = models.FloatField(verbose_name='用户余额')


class AccountChange(models.Model):
    '''帐变表要跟主库同步'''
    # user = models.CharField(max_length=255, verbose_name='用户pk')
    user = models.ForeignKey(User, related_name='account', on_delete=models.PROTECT, verbose_name='用户')
    transaction = models.CharField(max_length=500, verbose_name='交易记录')
    orderNum = models.CharField(max_length=500, verbose_name='订单号')
    # vendor_orderNum = models.CharField(max_length=500, blank=True, null=True, verbose_name='厂商订单号')
    befor_balance = models.FloatField(verbose_name='操作前余额')
    after_balance = models.FloatField(verbose_name='操作后余额')
    vendor_code = models.CharField(max_length=255, blank=True, null=True, verbose_name='厂商代码')
    game_code = models.CharField(max_length=255, blank=True, null=True, verbose_name='游戏代码')
    create_date = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    status = models.BooleanField(default=True, verbose_name='订单状态')


class BetRecords(models.Model):
    '''投注记录表也需要同步'''
    user = models.ForeignKey(User, related_name='bet', on_delete=models.CASCADE, verbose_name='用户')
    longmen_data = models.TextField(blank=True, null=True, verbose_name='龙门数据')
    verdor_data = models.TextField(blank=True, null=True, verbose_name='厂商数据')