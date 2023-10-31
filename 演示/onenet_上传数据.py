import random
import paho.mqtt.client as mqtt
from urllib.parse import quote
import json
import base64
import hmac
import time

# 请参考连接：https://open.iot.10086.cn/doc/v5/fuse/detail/919
HOST = "mqtts.heclouds.com"  # 连接主机
PORT = "1883"  # 端口

'''
以下四个变量换成你的内容
'''
# OneNET平台产品相关信息
PRO_ID = "iTPfSq42wR"  # 产品ID
DEV_KEY = "S08yMzNkSUFpcnM4dEFMVnluZXZmaVBJS3o5NWR6ZWE="  # 设备密钥
DEV_ID = "2125533019"  # 设备ID
DEV_NAME = "d1"  # 设备名称


# token算法,请参考连接：https://open.iot.10086.cn/doc/v5/fuse/detail/1486
def token(pro_id, dev_name, access_key):
    version = '2018-10-31'
    res = 'products/%s/devices/%s' % (pro_id, dev_name)
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


# 数据模板，json格式，请参考连接：https://open.iot.10086.cn/doc/v5/fuse/detail/923中“payload示例”
def data(data_id):
    message = {
        "id": data_id,
        "dp": {
            'tem': [{
                'v': random.randint(-50, 101)
            }],
            'hum': [{
                'v': random.randint(0, 201)
            }]
        }
    }
    message = json.dumps(message).encode('ascii')
    return message


if __name__ == '__main__':
    password = token(PRO_ID, DEV_NAME, DEV_KEY)

    client = mqtt.Client(client_id=DEV_NAME, clean_session=True,
                         protocol=mqtt.MQTTv311)  # client_id:设备名，protocol协议为：标准MQTTV3.1.1版本
    # 请参考连接：https://open.iot.10086.cn/doc/v5/fuse/detail/919

    client.username_pw_set(username=PRO_ID,
                           password=password)  # username:产品ID，password:token
    # 请参考连接：https://open.iot.10086.cn/doc/v5/fuse/detail/919

    client.connect(HOST, int(PORT),
                   keepalive=1200)  # host为目标地址，port为端口号
    # 请参考连接：https://open.iot.10086.cn/doc/v5/fuse/detail/919

    topic_publish = '$sys/%s/%s/dp/post/json' % (
        PRO_ID, DEV_NAME)  # publish topic发布簇，请参考连接：https://open.iot.10086.cn/doc/v5/fuse/detail/920

    client.loop_start()
    while True:
        # 树莓派循环发布数据到OneNET
        client.publish(topic=topic_publish, payload=data(123))
        print("-------------------------------------------------------------------------------")
        time.sleep(5)
