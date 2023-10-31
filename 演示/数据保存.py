# -*- coding: UTF-8 -*-
# 请看下面代码
import pymysql
import requests
import base64
import hmac
import time
from urllib.parse import quote
import json

'''
以下三个变量换成你的内容
'''
PRODUCT_ID = 'iTPfSq42wR'  # 产品ID
PRODUCT_ACCESS_KEY = 'Qyln34dFU1lTK4OLcetVqQEnl8vvu9Vr+6evVTOj/Z0='  # 产品的access_key
DEVICE_NAME = 'd1'  # 设备名称

'''
以下四个变量含义，请参考连接：https://open.iot.10086.cn/doc/v5/fuse/detail/1431
'''
START = '2023-10-20T08:00:00'
LIMIT = 60
SORT = 'ASC'
DS_ID = 'tem,hum'


# token计算
def token(id, access_key):
    """
    @:param
    id:产品id
    access_key:产品的access_key
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


# 请求数据
def requestData():
    AU = token(PRODUCT_ID, PRODUCT_ACCESS_KEY)
    url = 'http://iot-api.heclouds.com/datapoint/history-datapoints'

    # 请求多个数据模板id的特定时间的多组数据
    params = {
        'product_id': PRODUCT_ID,
        'device_name': DEVICE_NAME,
        'start': START,
        'limit': LIMIT,
        'sort': SORT,
        'datastream_id': DS_ID
    }
    header = {
        'authorization': AU
    }
    result = requests.get(url=url, params=params, headers=header)
    return json.loads(result.text)


# 数据解析
def dataParse():
    origin_data = requestData()
    tem_dp, hum_dp = origin_data['data']['datastreams'][0]['datapoints'], origin_data['data']['datastreams'][1][
        'datapoints']
    tem_data_value, hum_data_value = [i['value'] for i in tem_dp], [i['value'] for i in hum_dp]
    tem_data_time, hum_data_time = [i['at'] for i in tem_dp], [i['at'] for i in hum_dp]
    return tem_data_value, hum_data_value, tem_data_time, hum_data_time


# 数据存储
def storeData():
    # pymysql用法：https://www.cnblogs.com/liubinsh/p/7568423.html

    # 将数据存入数据库中
    tem_data_value, hum_data_value, tem_data_time, hum_data_time = dataParse()

    try:
        db = pymysql.connect(user='root', password='123456', host='127.0.0.1',
                             database='onenet')  # 参数含义依次为：用户名，密码，主机（127.0.0.1表示本地），数据库名
        cursor = db.cursor()  # 使用cursor()方法创建一个游标对象

        sql = ''  # sql语句

        try:
            # 存入温度value,time
            for i in zip(tem_data_value, tem_data_time):
                v, t = str(i[0]), str(i[1])
                sql = f"INSERT INTO tem_table(value,time) VALUES('{v}','{t}')"
                print(sql)
                cursor.execute(sql)  # 执行sql语句
                db.commit()  # 提交数据
            # 存入湿度value,time
            for i in zip(hum_data_value, hum_data_time):
                v, t = str(i[0]), str(i[1])
                sql = f"INSERT INTO hum_table(value,time) VALUES('{v}','{t}')"
                print(sql)
                cursor.execute(sql)
                db.commit()
            print('success!')
            cursor.close()  # 关闭游标
            db.close()  # 关闭连接
        except Exception as e:
            print(e)
            print('数据存入失败')
    except Exception as e:
        print(e)
        print('连接数据库失败！')


# 数据读取
def feathData():
    # pymysql用法：https://www.cnblogs.com/liubinsh/p/7568423.html
    try:
        db = pymysql.connect(user='root', password='123456', host='127.0.0.1',
                             database='onenet')  # 参数含义依次为：用户名，密码，主机（127.0.0.1表示本地），数据库名
        cursor = db.cursor()  # 使用cursor()方法创建一个游标对象
        try:
            sql = 'SELECT * FROM tem_table'  # sql语句
            # sql = 'SELECT * FROM hum_table'  # sql语句

            # 使用execute()方法执行SQL语句
            cursor.execute(sql)

            # 使用fetall()获取全部数据
            data = cursor.fetchall()

            # 打印获取到的数据
            print(data)

            # 关闭游标和数据库的连接
            cursor.close()
            db.close()
        except Exception as e:
            print(e)
            print('数据读取失败')
    except Exception as e:
        print(e)
        print('连接数据库失败！')


if __name__ == '__main__':
    data = requestData()
    dataParse()
    # storeData()
    feathData()