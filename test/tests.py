# message = 'memCode=10000000069&channel=0001&amount=50&orderNo=2019090712573012241286&notifyUrl=http://93.157.63.50:8088/callback/'
#
# resp_data = '{"code":"1000000","msg":"请求成功","data":"http://pay.f7pc.cn:3389/xinduibao/scanPay/qrcode/66666877941362867871","sign":"mYfHTFJ2ZRkfQbRGCguvaY1UPki8+WPxw6/FvvYj3vPfUJQ63hlN2wPxGPJyW1kNJbQFBSaIScKjuffa3O8+227N0DgYS1w0UAXRj54IXdZMB4WFSdNC0OVTJC1BtL357rG7bb/mthqXva9jmlHCkNhoj217k/IxSPmDc6j8UnA="}'
#
# from Crypto.PublicKey import RSA
# from Crypto.Signature import PKCS1_v1_5
# from Crypto.Hash import MD5
# import base64
#
# privateKey = open('/home/p007/Desktop/my_private_rsa_key.pem').read()
# publicKey = open('/home/p007/Desktop/pingtai_pub.pem').read()
# def RSA_sign(encrData):
#     # private_keyBytes = base64.b64decode(privateKey)
#     # key = '-----BEGIN PRIVATE KEY-----\n' + privateKey + '\n-----END PRIVATE KEY-----'
#     priKey = RSA.importKey(privateKey)
#     #priKey = RSA.importKey(privateKey)
#     signer = PKCS1_v1_5.new(priKey)
#     hash_obj = MD5.new(encrData.encode('utf-8'))
#     signature = base64.b64encode(signer.sign(hash_obj))
#     # signature = signer.sign(hash_obj)
#     # print(signature.hex())
#     # print(signature.decode('utf-8'))
#     return signature
#
#
# def verify(signature, encrData):
#     public_keyBytes = base64.b64decode(publicKey)
#     pubKey = RSA.importKey(public_keyBytes)
#     h = MD5.new(encrData.encode('utf-8'))
#     verifier = PKCS1_v1_5.new(pubKey)
#     return verifier.verify(h, base64.b64decode(signature))


# w = RSA_sign(message)
# new_ = json.loads(resp_data)
# sign = new_['sign']
# print(sign)
# verify_sign = 'code={c}&msg={m}&data={d}'.format(c=new_['code'], m=new_['msg'], d=new_['data'])
# print(verify_sign)
# w = verify('NWBWk4Jhp2pss9oWBM9si6xGw0uMmLytHiWvtw4KL4Q1z3GlnfasX2I+OvJFX6jltOUlJ9+qYJhXdxblIomT7IAbCKAKhAykR7R0bml9rXRwkdpOWXjmt849vHmKFd5SB7bAzVUMcMUQ46FCD8Nw8WuN5m9YqG2dvWKD0aGS40k=', message)
# print(w)
# w = RSA_sign(message)
# print(w.decode('utf-8'))
# w = verify('sfsdfsdfsdfsdfselfjslekfjsenfinsefinsefinisoenfoinsefoinsefoinsefoinoiefn', message)
# print(w)


def a(**kwargs):
    print(kwargs)

a()