import requests
import base64
import hmac
import time
from urllib.parse import quote

# PRODUCT_ID = '6mQDyE2cz4'  # 产品ID
# PRODUCT_ACCESS_KEY = 'EQVxNdPtQwVlKbMXSccfNzuPfY3nz/2FmU0f+3n18fM='  # 产品的access_key

'''
以下三个变量换成你的内容
'''
PRODUCT_ID = ''  # 产品ID
PRODUCT_ACCESS_KEY = ''  # 产品的access_key
DEVICE_NAME = ''  # 设备名称


def token(id, access_key):
    """
    @:param
    id:产品id
    access_key:产品开发中的那个key
    """
    version = '2018-10-31'

    res = 'products/%s' % id  # 通过产品ID访问产品API

    # 用户自定义token过期时间
    et = str(int(time.time()) + 3600)

    # 签名方法，支持md5、sha1、sha256
    method = 'sha1'

    # 对access_key进行decode
    key = base64.b64decode(access_key)

    # 计算sign
    org = et + '\n' + method + '\n' + res + '\n' + version
    sign_b = hmac.new(key=key, msg=org.encode(), digestmod=method)
    sign = base64.b64encode(sign_b.digest()).decode()

    # value 部分进行url编码，method/res/version值较为简单无需编码
    sign = quote(sign, safe='')
    res = quote(res, safe='')

    # token参数拼接
    token = 'version=%s&res=%s&et=%s&method=%s&sign=%s' % (version, res, et, method, sign)

    return token

AU = token(PRODUCT_ID, PRODUCT_ACCESS_KEY)
print(AU)
url = 'http://iot-api.heclouds.com/datapoint/history-datapoints'
params = {
    'product_id': PRODUCT_ID,
    'device_name': DEVICE_NAME,
}
header = {
    'authorization': AU
}

result = requests.get(url=url, params=params, headers=header)

print(result.text)
