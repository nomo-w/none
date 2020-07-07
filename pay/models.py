from django.db import models
# from django.contrib.auth.models import AbstractUser
# from django.utils import timezone

# Create your models here.
#
#
# class Payment_type(models.Model):
#     '''支付总类型表'''
#     pay_method = models.CharField(max_length=255, verbose_name='支付总类型')
#     is_active = models.BooleanField(default=True, verbose_name='是否可用')
#     method_code = models.CharField(max_length=125, verbose_name='支付类型代码')
#     image_path = models.CharField(max_length=500, verbose_name='展示图片')
#     create_date = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
#     update_date = models.DateTimeField(default=timezone.now, verbose_name='更新时间')
#
#
# class Payment_vendor(models.Model):
#     '''厂商表'''
#     vendor_name = models.CharField(max_length=255, verbose_name='厂商名')
#     vendor_url = models.URLField(max_length=500, verbose_name='厂商的支付url')
#     vendor_sign = models.CharField(max_length=500, verbose_name='厂商加密数据格式')
#     vendor_header = models.CharField(max_length=255, verbose_name='厂商所需请求头内容')
#     vendor_character = models.CharField(max_length=20, verbose_name='厂商所需字符编码')
#     vendor_sign_method = models.CharField(max_length=255, verbose_name='厂商使用的加密方法')
#     vendor_pubkey = models.CharField(max_length=500, verbose_name='厂商所需公钥路径')
#     vendor_prikey = models.CharField(max_length=500, verbose_name='厂商所需私钥路径')
#     vendor_params = models.CharField(max_length=500, verbose_name='子商户所需参数')
#     vendor_memcode = models.CharField(max_length=100, verbose_name='子商户号')
#     vendor_callback = models.URLField(verbose_name='提供给子商户的回调地址')
#     create_date = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
#     update_date = models.DateTimeField(default=timezone.now, verbose_name='更新时间')
#     is_active = models.BooleanField(default=True, verbose_name='是否可用')
#
#
# class Payment_channel(models.Model):
#     '''支付子类型表'''
#     pay_method = models.CharField(max_length=255, verbose_name='支付子类型')
#     vendor_paycode = models.CharField(max_length=255, verbose_name='厂商支付码')
#     vendor = models.ForeignKey(Payment_vendor, on_delete=models.CASCADE, related_name='vendor', verbose_name='对应的厂商')
#     # vendor = models.CharField(max_length=100, verbose_name='对应的厂商')
#     pay_type = models.ForeignKey(Payment_type, on_delete=models.CASCADE, related_name='pt', verbose_name='对应的支付总类型')
#     # pay_type = models.CharField(max_length=100, verbose_name='对应的支付总类型')
#     is_active = models.BooleanField(default=True, verbose_name='是否可用')
#     is_fast = models.CharField(max_length=10, verbose_name='是否好用快速')
#     image_path = models.CharField(max_length=500, verbose_name='展示图片')
#     create_date = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
#     update_date = models.DateTimeField(default=timezone.now, verbose_name='更新时间')


# class Order(models.Model):
#     userid = models.CharField(max_length=255, verbose_name='用户')
#     amount = models.CharField(max_length=255, verbose_name='付款金额')
#     orderno = models.CharField(max_length=255, verbose_name='订单号')
#     state = models.CharField(max_length=255, verbose_name='订单状态')
#     channel = models.CharField(max_length=255, verbose_name='支付方法')
#     ordertime = models.CharField(max_length=255, verbose_name='下单时间')

# class User(AbstractUser):
#     '''用户表'''
#     date_joined = DateField(default=timezone.now)
#     vip_level = CharField(max_length=255)
#     member_level = CharField(max_length=255)
#     affiliate = CharField(max_length=255)
#     name = CharField(max_length=100, null=True)
#     registered_at = DateTimeField(default=timezone.now)
#     last_login_at = DateTimeField(default=timezone.now)
#     last_login_ip = CharField(max_length=255, null=True)
#     balance = CharField(default=0, blank=True, null=True)  # 用户余额
#     frozen_balance = CharField(max_length=255, blank=True, null=True)
#
#     birth_date = CharField(max_length=255, null=True, blank=True)
#     phone = CharField(max_length=100, null=True, blank=True)
#     wechat = CharField(max_length=100, null=True, blank=True)
#     qq_number = CharField(max_length=255, null=True, blank=True)
#     notes = CharField(max_length=255, null=True, blank=True)
#
#     withdrawals_password = CharField(max_length=128, null=True, blank=True)
#
#     USERNAME_FIELD = 'username'
#     REQUIRED_FIELDS = []
#
#     # objects = UserManager()
#
#     class Meta:
#         db_table = 'member_user'
#
#
# class Deposit(Model):
#     '''存款表'''
#     DEPOSIT_TYPES = [
#         ('manual', _('Manual Deposit')),
#         ('company', _('Company Deposit')),
#         ('online', _('Online Deposit')),
#     ]
#     AUDIT_TYPES = [
#         ('deposit', _('Deposit')),
#         ('preferential', _('Preferential')),
#         ('none', _('None')),
#     ]
#     MANUAL_TYPES = [
#         ('manual', _('Manual Deposit')),
#         ('discount', _('Discount')),
#         ('commission', _('Commission')),
#         ('dividends', _('Dividends')),
#         ('cashback', _('Cashback')),
#         ('replenish', _('Replenish')),
#         ('other', _('Other')),
#     ]
#
#     user = ForeignKey(User, related_name="user_deposits", on_delete=CASCADE, blank=True, null=True)
#     amount = FloatField(default=0, blank=True, null=True)   # 存款金额
#     # bank = ForeignKey(Bank, related_name="bank_deposits", on_delete=CASCADE, blank=True, null=True)
#     bank = CharField(max_length=255, blank=True, null=True)
#     handling_fee = FloatField(default=0, blank=True, null=True)  # 手续费
#     deposit_type = CharField(default="company", choices=DEPOSIT_TYPES, max_length=15, blank=True)
#     audit_type = CharField(default="deposit", choices=AUDIT_TYPES, max_length=15, blank=True)  # 审计类型
#     audit_amount = FloatField(default=0, blank=True, null=True)   # 审计金额
#     manual_type = CharField(default='manual', choices=MANUAL_TYPES, max_length=15, blank=True)
#     order_id = CharField(blank=True, null=True, max_length=35)  # 订单号
#     out_trade_no = CharField(blank=True, null=True, max_length=100, verbose_name="Third party order id")  # 第三方订单号
#     user_note = TextField(blank=True, null=True)
#     internal_note = TextField(blank=True, null=True)
#     balance = FloatField(default=0, blank=True, null=True)
#     deposit_date = DateTimeField(blank=True, null=True)  # 存款日期
#     create_user = ForeignKey(User, on_delete=SET_NULL, blank=True, null=True, related_name='deposit_create')
#
#     class Meta:
#         db_table = 'deposit'
#
#
# class UserTransactionStats(Model):
#     '''用户交易统计表'''
#     user_id = BigIntegerField(blank=False, null=False)
#     depost_last_datetime = DateTimeField(blank=True, null=True)
#     withdrawal_last_time = DateTimeField(blank=True, null=True)
#     deposit_count = IntegerField(default=0, blank=True, null=True)  # 用户存款次数,存一此加一次
#     withdrawal_count = IntegerField(default=0, blank=True, null=True)  # 取款次数,不需要操作
#     deposit_total = FloatField(default=0, blank=True, null=True)   # 存款总额
#     deposit_audit_total = FloatField(default=0, blank=True, null=True)
#     preferential_audit_total = FloatField(default=0, blank=True, null=True)
#     withdrawal_total = FloatField(default=0, blank=True, null=True)   # 取款总额
#     balance = FloatField(default=0, blank=True, null=True)
#     frozen_balance = FloatField(default=0, blank=True, null=True)  # 冻结,不需要操作
#
#     class Meta:
#         db_table = 'user_transaction_stats'
#         verbose_name = "user_transaction_stats"
#
#
# class MemberBankRecord(Model):
#     '''用户存款记录'''
#     user = ForeignKey(User, on_delete=SET_NULL,
#                       blank=True, null=True,
#                       related_name='user_bank_record')
#     amount = FloatField(default=0, blank=True, null=True)  # 存款金额
#     balance_before = FloatField(default=0, blank=True, null=True)  # 存款之前余额,需要先去用户表查询余额,然后写进来
#     balance = FloatField(default=0, blank=True, null=True)
#     type = CharField(blank=True, null=True, max_length=100)
#     remark = CharField(blank=True, null=True, max_length=300)
#     game_name = CharField(blank=True, null=True, max_length=100)
#     game_server_timestamp = CharField(blank=True, null=True, max_length=50)
#     order_id = CharField(blank=True, null=True, max_length=35, unique=True)  # 订单号
#     game_vendor = CharField(max_length=20, null=True, blank=True)
#
#     class Meta:
#         db_table = 'member_bank_record'