# -*- coding: UTF-8 -*-
# 请看下面代码
from flask import Flask, render_template
import requests
import json

app = Flask(__name__, template_folder='./templates', static_folder='./static')


# https://open.ys7.com/help/81
def getToken():
    try:
        APPKEY = 'd0d0f00ae3db4b9c81fdd3fb9e0ef636'
        SECRET = '15c819810de2bbd18c7da5452bb00fb0'
        url = 'https://open.ys7.com/api/lapp/token/get'
        params = {
            'appKey': APPKEY,
            'appSecret': SECRET
        }
        result = requests.post(url=url, params=params).text
        print(f'{__name__}->callback:{result}')
        token = json.loads(result)['data']['accessToken']
        print(f'{__name__}->萤石token：{token}')
        return token
    except requests.exceptions.ProxyError:
        print(f'{__name__}->萤石token error！  Max retries exceeded with url')
        return None
    except Exception as e:
        print(f'{__name__}->callback:{e}')
        return None


# https://open.ys7.com/help/1414
def getAddress(token):
    try:
        DEV_SERIAL = 'L28080095'
        url = 'https://open.ys7.com/api/lapp/v2/live/address/get/'
        params = {
            'accessToken': token,
            'deviceSerial': DEV_SERIAL,
            'channelNo': 1
        }
        result = requests.post(url=url, params=params).text
        print(f'{__name__}->callback:{result}')
        liveAddress = json.loads(result)['data']['url']
        print(f'{__name__}->萤石address：{liveAddress}')
        return liveAddress
    except requests.exceptions.ProxyError:
        print(f'{__name__}->萤石address error！ Max retries exceeded with url')
        return None
    except Exception as e:
        print(f'{__name__}->callback:{e}')
        return None


@app.route('/')
def index():
    token = getToken()
    address = getAddress(token)
    message = None
    if address is None:
        message = '设备不在线!'
        return render_template('index.html', token=token, address='address', message=message)
    else:
        return render_template('index.html', token=token, address=address, message=None)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5666, debug=True)
