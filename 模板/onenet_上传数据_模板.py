import paho.mqtt.client as mqtt
from urllib.parse import quote
import json
import base64
import hmac
import time

# OneNET平台产品相关信息
HOST = "mqtts.heclouds.com"  # 连接主机
PORT = "1883"  # 端口
'''
以下四个变量换成你的内容
'''
PRO_ID = ""  # 产品ID
DEV_KEY = ""  # 设备密钥
DEV_ID = ""  # 设备ID
DEV_NAME = ""  # 设备名称


# token算法
def token(pro_id, dev_name, access_key):
    version = '2018-10-31'
    res = 'products/%s/devices/%s' % (pro_id, dev_name)  # 通过产品ID访问产品API
    # res = 'products/%s' % pro_id  # 通过产品ID访问产品API
    # 用户自定义token过期时间
    et = str(int(time.time()) + 3600000)
    # 签名方法，支持md5、sha1、sha256
    method = 'md5'
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


# 数据
def data(data_id):
    message = {
        "id": data_id,
        "dp": {
            'tem': [{
                'v': 15
            }]
        }
    }
    message = json.dumps(message).encode('ascii')
    return message


if __name__ == '__main__':
    # client_id:设备名 , username:产品ID , password:token
    password = token(PRO_ID, DEV_NAME, DEV_KEY)
    client = mqtt.Client(client_id=DEV_NAME, clean_session=True, protocol=mqtt.MQTTv311)
    client.username_pw_set(username=PRO_ID, password=password)
    client.connect(HOST, int(PORT), keepalive=1200)
    topic_publish = '$sys/%s/%s/dp/post/json' % (PRO_ID, DEV_NAME)  # topic
    client.loop_start()
    while True:
        # 树莓派循环发布数据到OneNET
        client.publish(topic=topic_publish, payload=data(123))
        print("-------------------------------------------------------------------------------")
        time.sleep(5)
