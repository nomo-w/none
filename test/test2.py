import requests


# 登录
param = '''
mutation{
    login(
      username: \"Jay\"
      password: \"intel@123\"
    ) {
      token
  }
}
'''
url = 'http://93.157.63.50:8000/graphql/'

# 查询用户
param2 ='''
query {
  users(username: "Jay") {
    edges {
      node {
        id
        username
        lastLoginAt
        balance
      }
    }
  }
}
'''


# 创建订单
param3 = '''
mutation {
  deposit(input: {
    user: "VXNlck5vZGU6MTA3Mw=="
		amount: 50
		depositType: "online"
  })
  {
    deposit{
      id
      pk
      orderId
      amount
      user {
        id
        username
      }
    }
  errors{
      messages
      field
    }
  }
}'''

# 修改订单状态
param4 = '''
mutation{
  depositApproval(input:{
    pk:6
    status:"confirmed"
  }) {
    clientMutationId
    errors{
      messages
      field
    }
    deposit {
      id
      orderId
      pk
      amount
      updatedAt
    }
  }
}
'''

# 查询订单状态
param5 = '''
query {
  deposities(
    orderId_Icontains: "2019083011264359264858"
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

param6 = '''
query{
  banks (
    id: "QmFua05vZGU6Nw=="
  )
  {
    edges {
      node {
        id
        businessType
        businessCode
        payVendor{
          name
          remark
        }
      }
    }
  }
}
'''

json_param = {"query": param}
w = requests.post(url, data=json_param)
print(w.status_code)
print(w.json())