
# 本地使用graphql登录用户
GRA_USER = 'Jay'
# 本地使用graphql登录密码
GRA_PASS = '*********'
# graphql地址
GRA_URL = 'https://*******:8000/graphql/'
# 回调地址url
CALLBACK = 'http://*******:8088/callback/'
# 登录graphql参数
LOGIN_GRAPHQL = '''
mutation{
    login(
      username: \"%s\"
      password: \"%s\"
    ) {
      token
  }
}
''' % (GRA_USER, GRA_PASS)

# 查询用户的graphql参数
QUERY_USER_GRAPHQL = '''
query {
  users(username: "%s") {
    edges {
      node {
        id
        username
        balance
      }
    }
  }
}
'''

# 创建订单的graphql参数
CREATE_ORDER_GRAPHQL = '''
mutation {
  deposit(input: {
    user: "%s"
	amount: %s
	depositType: "online"
  })
  {
    deposit{
      id
      pk
      amount
      orderId
    }
  }
}
'''

# 修改订单的graphql参数
UPDATE_ORDER_GRAPHQL = '''
mutation{
  depositCallback(input:{
    amount: %s
    status: "%s"
    orderId: "%s"
  }){
    deposit {
      id
      pk
      amount
      status
    }
  }
}
'''

# 查询厂商详情的graphql参数
QUERY_VENDOR_GRAPHQL = '''
query{
  payVendor (%s){
    edges {
      node {
        id
        name
        merchantNumber
        merchantKey
        merchantCertificate
      }
    }
  }
}
'''

# 查询订单的graphql参数
CHECK_ORDER_GRAPHQL = '''
query {
  deposities(
    orderId_Icontains: "%s"
  ) {
    edges {
      node {
        id
        status
        user{
          username
        }
      }
    }
  }
}
'''

# 查询支付类型的graphql参数
CHECK_VENDOR_GRAPHQL = '''
query{
  banks (
    id: "%s"
  )
  {
    edges {
      node {
        id
        businessType
        businessCode
        payVendor{
          name
        }
      }
    }
  }
}
'''

# 接口返回状态定义
RETURN_STATUS = {
    'good': 'success',
    'not good': 'failed',
}

DEFAULT_HEADERS = {
    'User-Agent': "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    # 'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': '*/*',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
    'Content-Length': '278',
    'Accept-Encoding': 'gzip,deflate',
}