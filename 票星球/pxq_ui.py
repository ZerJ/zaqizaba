# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import logging
import colorlog
import os
import time
import json
import requests
import wmi
import keyboard
import base64
import shelve
import datetime
from threading import Thread
from PIL import Image, ImageTk
import io
import urllib3

w = wmi.WMI()
# 全局变量，用于控制程序的暂停和继续
paused = False
current_time = datetime.datetime.now().time()
print(current_time)
# 定义暂停和继续的快捷键处理函数
def toggle_pause():
    global paused
    paused = not paused
    if paused:
        print("程序已暂停")
    else:
        print("程序继续运行")


# 绑定快捷键
keyboard.add_hotkey('ctrl+shift+p', toggle_pause)  # 使用Ctrl+Shift+P暂停和继续程序

with open('./config.json', 'r', encoding='utf_8_sig') as f:
    config = json.loads(f.read())

ProjectPath = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
LogsPath = os.path.join('./', 'logs/log_{0}'.format(time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())))

# 设置控制台打印的颜色
log_colors_config = {
    'DEBUG': 'cyan',
    'INFO': 'blue',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red',
}


class MyLogs:
    def mylog(self, level, msg):
        logger = logging.getLogger('PaioXingQiu_API')
        logger.setLevel(logging.DEBUG)
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s',
            log_colors=log_colors_config)
        formatter2 = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s')
        sh = logging.StreamHandler()  # 输出到控制台
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)  # 指定格式

        fh = logging.FileHandler(LogsPath, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter2)
        logger.addHandler(sh)
        logger.addHandler(fh)  # 输出到文件

        if level == "DEBUG":
            logger.debug(msg)
        elif level == "INFO":
            logger.info(msg)
        elif level == "WARNING":
            logger.warning(msg)
        elif level == "ERROR":
            logger.error(msg)
        elif level == "CRITICAL":
            logger.critical(msg)
        logger.removeHandler(sh)
        logger.removeHandler(fh)
        fh.close()  #不关闭会警告

    def debug(self, msg):
        self.mylog("DEBUG", msg)

    def info(self, msg):
        self.mylog("INFO", msg)

    def warning(self, msg):
        self.mylog("WARNING", msg)

    def error(self, msg):
        self.mylog("ERROR", msg)

    def critical(self, msg):
        self.mylog("CRITICAL", msg)


log = MyLogs()


def get_audienceIds(access_token):
    headers = {
        'content-type': 'application/json; application/json',
        'access-token': access_token,
        'host': 'm.piaoxingqiu.com',
        'terminal-src': 'WEB',
        'ver': '4.1.2-20240305183007',
        'origin': 'https://m.piaoxingqiu.com',
        'referer': 'https://m.piaoxingqiu.com',
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    }
    urllib3.disable_warnings()
    audienceIds_list = []
    url = 'https://m.piaoxingqiu.com/cyy_gatewayapi/user/buyer/v3/user_audiences?src=WEB&channelId=&terminalSrc=WEB&offset=0&length=50&bizCode=FHL_M&idTypes=ID_CARD,PASSPORT,MAINLAND_TRAVEL_PERMIT_TAIWAN,MAINLAND_TRAVEL_PERMIT_HK_MC&showId='
    resp = requests.get(url, verify=False, headers=headers).json()['data']

    return resp


# def get_addressId():
#     url = 'https://m.piaoxingqiu.com/cyy_gatewayapi/user/buyer/v3/user/addresses/default?showId=&src=WEB&channelId=&terminalSrc=WEB'
#     resp = requests.get(url, headers=headers)
#     dic_ = {}
#     dic_['detailAddress'] = resp.json()['data']['detailAddress']
#     dic_['addressId'] = resp.json()['data']['addressId']
#     dic_['receiver'] = resp.json()['data']['username']
#     dic_['cellphone'] = resp.json()['data']['cellphone']
#     dic_['province'] = resp.json()['data']['location']['locationId'][0:2]
#     dic_['city'] = resp.json()['data']['location']['locationId'][2:4]
#     dic_['district'] = resp.json()['data']['location']['locationId'][4:6]
#     return dic_


def get_locationCityId(headers):
    url = 'https://m.piaoxingqiu.com/cyy_gatewayapi/home/pub/v3/citys/current_location?src=WEB&channelId=&terminalSrc=WEB'
    resp = requests.get(url, verify=False, headers=headers)

    return resp.json()['data']['bsCityId']


def get_deliverMethod(headers, seatPlanId, bizShowSessionId, showId, price, ticket_num):
    url = 'https://m.piaoxingqiu.com/cyy_gatewayapi/trade/buyer/order/v3/pre_order?channelId=&terminalSrc=WEB'
    data = {
        "items": [
            {"skus": [
                {"seatPlanId": seatPlanId,
                 "sessionId": bizShowSessionId,
                 "showId": showId,
                 "skuId": seatPlanId,
                 "skuType": "SINGLE",
                 "ticketPrice": price,
                 "qty": ticket_num
                 }
            ],
                "spu": {
                    "id": showId,
                    "spuType": "SINGLE"}
            }
        ],
        "src": "WEB"
    }
    resp = requests.post(url, headers=headers, verify=False, data=json.dumps(data))
    return resp.json()['data']['supportDeliveries'][0]['name']


def get_param_data(audienceId, bsCityId, seatPlanId, bizShowSessionId,
                   deliverMethod, price, ticket_num, showId):
    data = {
        "src": "weixin_mini",
        "merchantId": "6267a80eed218542786f1494",
        "ver": "4.26.6",
        "appId": "wxad60dd8123a62329",
        "addressParam": {},
        "locationParam": {
            "locationCityId": bsCityId,
            "bsCityId": bsCityId
        },
        "paymentParam": {
            "totalAmount": price * ticket_num,
            "payAmount": price * ticket_num
        },
        "priceItemParam": [{
            "applyTickets": [],
            "priceItemName": "票款总额",
            "priceItemVal": price * ticket_num,
            "priceItemType": "TICKET_FEE",
            "priceItemSpecies": "SEAT_PLAN",
            "direction": "INCREASE",
            "priceDisplay": "￥{}".format(price * ticket_num)
        }],
        "items": [{
            "sku": {
                "skuId": seatPlanId,
                "skuType": "SINGLE",
                "ticketPrice": price * ticket_num,
                "qty": 1,
                "ticketItems": [{
                    "id": "1",
                    "audienceId": audienceId
                }]
            },
            "spu": {
                "showId": showId,
                "sessionId": bizShowSessionId,
                "promotionVersionHash": "EMPTY_PROMOTION_HASH",
                "addPromoVersionHash": "EMPTY_PROMOTION_HASH"
            },
            "deliverMethod": "ID_CARD"
        }],
        "priorityId": "",
        "addPurchasePromotionId": "",
        "many2OneAudience": {},
        "orderSource": "COMMON"
    }
    return data


def get_express_param_data(audienceId, locationCityId, seatPlanId,
                           bizShowSessionId, deliverMethod, price, ticket_num, priceItemVal, showId):
    dic_address = get_addressId()
    data = {
        "audienceIds": audienceId[0],
        "addressParam": {
            "address": dic_address['detailAddress'],
            "addressId": dic_address['addressId'],
            "district": dic_address['district'],
            "city": dic_address['city'],
            "province": dic_address['province']
        },
        "contactParam": {
            "cellphone": dic_address['cellphone'],
            "receiver": dic_address['receiver']
        },
        "locationParam": {
            "locationCityId": locationCityId
        },
        "paymentParam": {
            "totalAmount": price * ticket_num + priceItemVal,
            "payAmount": price * ticket_num + priceItemVal
        },
        "priceItemParam": [{
            "applyTickets": [],
            "priceItemName": "票款总额",
            "priceItemVal": price * ticket_num,
            "priceItemType": "TICKET_FEE",
            "priceItemSpecies": "SEAT_PLAN",
            "direction": "INCREASE",
            "priceDisplay": "￥{}".format(price * ticket_num)
        }, {
            "applyTickets": [],
            "priceItemName": "快递费",
            "priceItemVal": priceItemVal,
            "priceItemId": showId,
            "priceItemSpecies": "SEAT_PLAN",
            "priceItemType": "EXPRESS_FEE",
            "direction": "INCREASE",
            "priceDisplay": "￥{}".format(priceItemVal)
        }],
        "items": [{
            "skus": [{
                "seatPlanId": seatPlanId,
                "sessionId": bizShowSessionId,
                "showId": showId,
                "skuId": seatPlanId,
                "skuType": "SINGLE",
                "ticketPrice": price,
                "qty": ticket_num,
                "deliverMethod": "ID_CARD"
            }],
            "spu": {
                "id": showId,
                "spuType": "SINGLE"
            }
        }],
        "many2OneAudience": {
            "audienceId": audienceId[0],
            "sessionIds": list(bizShowSessionId)
        },
        "many2OneAudience": {},
        # "one2oneAudiences": [{
        #     "audienceId": audienceId[0],
        #     "sessionId": bizShowSessionId
        # }],
        "src": "WEB"
    }
    return data


def default_show_detail(access_token, showId):
    url = "https://m.piaoxingqiu.com/cyy_gatewayapi/show/pub/v5/show/" + showId + "/sessions"

    payload = {}
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'access-token': access_token,
        'host': 'm.piaoxingqiu.com',
        'terminal-src': 'WEB',
        'src': 'WEB',
        'ver': '4.1.2-20240305183007',
        'origin': 'https://m.piaoxingqiu.com',
        'referer': 'https://m.piaoxingqiu.com',
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    }

    response = requests.request("GET", url, headers=headers, data=payload, verify=False)

    print(response.text)


def default_show(access_token, cityId, length, sortType, keyword):
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'access-token': access_token,
        'host': 'm.piaoxingqiu.com',
        'terminal-src': 'WEB',
        'src': 'WEB',
        'ver': '4.1.2-20240305183007',
        'origin': 'https://m.piaoxingqiu.com',
        'referer': 'https://m.piaoxingqiu.com',
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    }

    params = {
        'backendCategoryCode': 'ALL',
        'cityId': cityId,
        'keyword': keyword,
        'length': length,  #演唱会长度
        'offset': '0',
        'pageType': 'SEARCH_PAGE',
        'sortType': sortType,  # ATTENTION:热点排序  NEW：最新排序 RECOMMEND：推荐排序
        'src': 'WEB',
        'ver': '4.1.2-20240305183007',
    }

    response = requests.get('https://m.piaoxingqiu.com/cyy_gatewayapi/home/pub/v3/show_list/search', params=params,
                            verify=False,
                            headers=headers).json()
    return response


def get_showInformation(showId, access_token):
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'access-token': access_token,
        'host': 'm.piaoxingqiu.com',
        'terminal-src': 'WEB',
        'src': 'WEB',
        'ver': '4.1.2-20240305183007',
        'origin': 'https://m.piaoxingqiu.com',
        'referer': 'https://m.piaoxingqiu.com',
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    }

    data = {
        'isQueryShowBasicInfo': 'true',
        'source': 'FROM_QUICK_ORDER',
        'src': 'WEB',
        'ver': '4.1.2-20240305183007',
    }

    response = requests.get(
        'https://m.piaoxingqiu.com/cyy_gatewayapi/show/pub/v5/show/{}/sessions?src=WEB&ver=4.19.6&source=FROM_QUICK_ORDER&isQueryShowBasicInfo=true'.format(
            showId),
        headers=headers, verify=False, data=data).json()
    return response


def get_baseCode(cellphone):
    headers = {
        'content-type': 'application/json; application/json',
        'host': 'm.piaoxingqiu.com',
        'terminal-src': 'WEB',
        'ver': '4.1.2-20240305183007',
        'origin': 'https://m.piaoxingqiu.com',
        'referer': 'https://m.piaoxingqiu.com',
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    }

    json_data = {
        'cellphone': cellphone,
        'messageType': 'MOBILE',
        'src': 'WEB',
        'ver': '4.1.2-20240305183007',
        'verifyCodeUseType': 'USER_LOGIN',
    }

    urllib3.disable_warnings()
    response = requests.post(
        'https://m.piaoxingqiu.com/cyy_gatewayapi/user/pub/v3/generate_photo_code',
        headers=headers,
        json=json_data,
        verify=False,
    )

    baseCode = response.json()['data']['baseCode']
    return baseCode


def get_send_verifyCode(cellphone, token):
    headers = {
        'content-type': 'application/json; application/json',
        'host': 'm.piaoxingqiu.com',
        'terminal-src': 'WEB',
        'ver': '4.1.2-20240305183007',
        'origin': 'https://m.piaoxingqiu.com',
        'referer': 'https://m.piaoxingqiu.com',
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    }

    json_data = {
        'cellphone': cellphone,
        'messageType': 'MOBILE',
        'src': 'WEB',
        'token': token,
        'ver': '4.1.2-20240305183007',
        'verifyCodeUseType': 'USER_LOGIN',
    }
    urllib3.disable_warnings()
    response = requests.post(
        'https://m.piaoxingqiu.com/cyy_gatewayapi/user/pub/v3/send_verify_code',
        headers=headers,
        json=json_data,
        verify=False,
    ).json()
    return response


def get_user_choice(prompt):
    while True:
        choice = input(prompt).strip().lower()
        if choice in ['y', 'n']:
            return choice == 'y'
        else:
            print("无效输入，请输入 'y' 或 'n'。")


# def get_captcha(cellphone):
#     baseCode = get_baseCode(cellphone)
#     head, context = baseCode.split(",")  # 将base64_str以“,”分割为两部分
#     img_data = base64.b64decode(context)  # 解码时只要内容部分
#     with open('captcha.png', 'wb') as f:
#         f.write(img_data)


def login_success_message(access_token):
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'access-token': access_token,
        'host': 'm.piaoxingqiu.com',
        'terminal-src': 'WEB',
        'src': 'WEB',
        'ver': '4.1.2-20240305183007',
        'origin': 'https://m.piaoxingqiu.com',
        'referer': 'https://m.piaoxingqiu.com',
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    }

    data = {
        'src': 'WEB',
        'ver': '4.1.2-20240305183007',
    }

    response = requests.get('https://m.piaoxingqiu.com/cyy_gatewayapi/user/buyer/v3/profile', headers=headers,
                            verify=False,
                            data=data, ).json()
    return response


def get_access_token(cellphone, verifyCode):
    headers = {
        'content-type': 'application/json; application/json',
        'host': 'm.piaoxingqiu.com',
        'terminal-src': 'WEB',
        'ver': '4.1.2-20240305183007',
        'origin': 'https://m.piaoxingqiu.com',
        'referer': 'https://m.piaoxingqiu.com',
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    }

    json_data = {
        'cellphone': cellphone,
        'src': 'WEB',
        'ver': '4.1.2-20240305183007',
        'verifyCode': verifyCode,
    }

    response = requests.post(
        'https://m.piaoxingqiu.com/cyy_gatewayapi/user/pub/v3/login_or_register',
        headers=headers,
        json=json_data,
        verify=False,
    ).json()

    access_token = response['data']['accessToken']

    result = login_success_message(access_token)
    log_success = "用户" + result['data']['nickname'] + "登录成功"

    return access_token, log_success


def get_ip_geolocation(ip):
    ipinfo_url = f'http://ipinfo.io/{ip}/json'

    response = requests.get(ipinfo_url)
    response.raise_for_status()
    return response.json()


def add_audiences(name, idcart, access_token):
    headers = {
        'Host': 'm.piaoxingqiu.com',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'src': 'WEB',
        'sec-ch-ua-mobile': '?0',
        'access-token': access_token,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Content-Type': 'application/json',
        'terminal-src': 'WEB',
        'ver': '4.6.6',
        'sec-ch-ua-platform': '"Windows"',
        'Accept': '*/*',
        'Origin': 'https://m.piaoxingqiu.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://m.piaoxingqiu.com/package-user/pages/audience-modification/audience-modification?watcherReplacer=%E8%A7%82%E6%BC%94',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    json_data = {
        'src': 'WEB',
        'ver': '4.6.6',
        'bizCode': 'FHL_M',
        'name': name,
        'idType': 'ID_CARD',
        'idNo': idcart,
    }

    response = requests.post(
        'https://m.piaoxingqiu.com/cyy_gatewayapi/user/buyer/v4/user_audiences',
        headers=headers,
        json=json_data,
        verify=False,
    ).json()


class App:
    def __init__(self, root):
        self.manual_entries = None
        self.token_file = "token.json"
        self.access_token = self.load_and_validate_token()
        self.phone_entry = None
        self.login_frame = None
        self.search_frame = None
        self.root = root
        self.root.title("票星球抢票工具")

        self.cellphone = None
        self.sms_code_entry = None
        self.captcha_entry = None
        self.captcha_image = None  # 新增：用于保持图片引用
        self.current_config = None
        self.audiences = None

        if self.access_token:

            audiences = get_audienceIds(self.access_token)
            if audiences is None:
                self.show_audience_adder()
            self.root.after(0, self.setup_main_ui())  # 直接进入主界面
        else:
            self.root.after(0, self.setup_login_ui())  # 显示登录界面

    def load_and_validate_token(self):
        try:
            # 从本地文件加载token
            if not os.path.exists(self.token_file):
                return None

            with open(self.token_file, "r") as f:
                token_data = json.load(f)

            token = token_data.get("access_token")

            if not token:
                return None

            # 执行快速验证（使用轻量级API）
            if self.validate_token(token):
                return token
            return None
        except Exception as e:
            return None

    def validate_token(self, token):
        """验证token有效性"""
        self.headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
            "access-token": token
        }
        try:
            resp = requests.get(
                'https://m.piaoxingqiu.com/cyy_gatewayapi/user/buyer/v3/profile',
                headers=self.headers,
                verify=False,
                timeout=5
            )

            return resp.status_code == 200 and resp.json().get('statusCode') == 200
        except:
            return False

    def setup_login_ui(self):
        self.login_frame = ttk.Frame(self.root, padding="20")
        self.login_frame.grid(row=0, column=0)

        # 手机号输入
        ttk.Label(self.login_frame, text="手机号:").grid(row=0, column=0, sticky="w")
        self.phone_entry = ttk.Entry(self.login_frame)
        self.phone_entry.grid(row=0, column=1, padx=5)

        # 图形验证码
        ttk.Button(self.login_frame, text="获取图形验证码", command=self.get_captcha).grid(row=1, column=0, pady=5)
        self.captcha_entry = ttk.Entry(self.login_frame)
        self.captcha_entry.grid(row=1, column=1, padx=5)

        # 短信验证码
        ttk.Button(self.login_frame, text="发送短信验证码", command=self.send_sms_code).grid(row=2, column=0, pady=5)
        self.sms_code_entry = ttk.Entry(self.login_frame)
        self.sms_code_entry.grid(row=2, column=1, padx=5)

        # 登录按钮
        ttk.Button(self.login_frame, text="登录", command=self.login).grid(row=3, columnspan=2, pady=10)

        # # 验证码图片显示区域（初始为空）
        # self.captcha_entry.grid(row=1, column=1, padx=5)
        # ttk.Button(self.login_frame, text="发送短信验证码").grid(row=2, column=0, pady=5)
        # self.sms_code_entry.grid(row=2, column=1, padx=5)

    def get_captcha(self):
        self.cellphone = self.phone_entry.get()
        if not self.cellphone:
            messagebox.showerror("错误", "请输入手机号")
            return
        try:
            baseCode = get_baseCode(self.cellphone)
            head, context = baseCode.split(",")
            img_data = base64.b64decode(context)

            # 使用PIL打开图片并显示在UI上
            image = Image.open(io.BytesIO(img_data))
            photo = ImageTk.PhotoImage(image)

            # 如果已有验证码标签则更新，否则创建
            if hasattr(self, 'captcha_label'):
                self.captcha_label.configure(image=photo)
                self.captcha_label.image = photo
            else:
                self.captcha_label = ttk.Label(self.login_frame, image=photo)
                self.captcha_label.grid(row=4, columnspan=2, pady=10)
                self.captcha_label.image = photo  # 保持引用

        except Exception as e:
            messagebox.showerror("错误", f"获取验证码失败: {str(e)}")

    def send_sms_code(self):

        captcha = self.captcha_entry.get()

        if not captcha:
            messagebox.showerror("错误", "请输入图形验证码")
            return
        try:
            get_send_verifyCode(self.cellphone, captcha)
            messagebox.showinfo("成功", "短信验证码已发送")
        except Exception as e:
            messagebox.showerror("错误", f"发送失败: {str(e)}")

    def save_token(self, token):
        """明文保存token到文件"""
        config = {'access_token': token}
        with open(self.token_file, 'w') as f:
            json.dump(config, f, indent=2)

    def login(self):
        verify_code = self.sms_code_entry.get()
        if not verify_code:
            messagebox.showerror("错误", "请输入短信验证码")
            return
        try:
            self.access_token, log_success = get_access_token(self.cellphone, verify_code)

            self.headers = {
                "Content-Type": "application/json;charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
                "access-token": self.access_token
            }
            messagebox.showinfo("成功", log_success)
            self.save_token(self.access_token)
            self.login_frame.destroy()
            audiences = get_audienceIds(self.access_token)
            if audiences is None:
                self.show_order_config()
            self.setup_main_ui()
        except Exception as e:
            messagebox.showerror("错误", f"登录失败: {str(e)}")

    def setup_main_ui(self):
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0)

        # 创建参数展示容器
        ttk.Button(self.main_frame, text="加载配置",
                   command=self.refresh_parameter_display).pack(pady=5)
        self.create_parameter_display()

        # 创建操作按钮
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(pady=10)

        ttk.Button(control_frame, text="配置抢票参数",
                   command=self.show_order_config).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="立即抢票",
                   command=self.start_order_process).grid(row=0, column=1, padx=5)

    def create_parameter_display(self):
        """创建参数展示区域（带配置加载功能）"""
        display_frame = ttk.LabelFrame(self.main_frame, text="当前抢票配置")
        display_frame.pack(fill="x", padx=5, pady=5)

        # 初始化显示内容
        default_values = self.load_config_or_default()
        if default_values['audience'] == "":
            self.show_audience_adder()
        # 使用Grid布局创建两列展示
        self.display_labels = {
            "show": ttk.Label(display_frame, text=f"演出信息：{default_values['show']}"),
            "session": ttk.Label(display_frame, text=f"场次信息：{default_values['session']}"),
            "ticket": ttk.Label(display_frame, text=f"票价信息：{default_values['ticket']}"),
            "quantity": ttk.Label(display_frame, text=f"购票数量：{default_values['quantity']}"),
            "audience": ttk.Label(display_frame, text=f"观影人：{default_values['audience']}")
        }

        for idx, (key, label) in enumerate(self.display_labels.items()):
            label.grid(row=idx, column=0, sticky="w", padx=10, pady=2)

    def show_audience_adder(self):
        """显示观影人添加界面"""
        # 创建弹窗
        self.audience_dialog = tk.Toplevel(self.root)
        self.audience_dialog.title("添加观影人")
        self.audience_dialog.geometry("300x200")

        # 姓名输入
        ttk.Label(self.audience_dialog, text="姓名：").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(self.audience_dialog)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        # 身份证输入
        ttk.Label(self.audience_dialog, text="身份证：").grid(row=1, column=0, padx=5, pady=5)
        self.id_entry = ttk.Entry(self.audience_dialog)
        self.id_entry.grid(row=1, column=1, padx=5, pady=5)

        # 操作按钮
        btn_frame = ttk.Frame(self.audience_dialog)
        btn_frame.grid(row=2, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="保存", command=self.save_audience).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="取消", command=self.audience_dialog.destroy).pack(side="left", padx=5)

    def save_audience(self):
        """保存观影人信息"""
        name = self.name_entry.get().strip()
        id_num = self.id_entry.get().strip()
        add_audiences(name, id_num, self.access_token)
        self.audience_dialog.destroy()
        self.show_order_config()

    def order_info_with_params(self,sessionSaleTime=None):
        url = 'https://m.piaoxingqiu.com/cyy_gatewayapi/trade/buyer/order/v5/create_order?lang=zh'
        bsCityId = get_locationCityId(self.headers)

        audienceId = self.current_config["audienceId"]
        seatPlanId = self.current_config["seatPlanId"]

        bizShowSessionId = self.current_config["bizShowSessionId"]

        price = self.current_config["price"]
        showId = self.current_config["showId"]
        ticket_num = self.current_config["ticket_num"]
        try:
            deliverMethod = get_deliverMethod(self.headers, seatPlanId, bizShowSessionId, showId, price, ticket_num)
        except:
            deliverMethod = "EXPRESS"
        ###########################下单逻辑##############################
        while True:
            while paused:
                time.sleep(0.1)  # 暂停时，短暂休眠以降低CPU使用率
            if sessionSaleTime:

                if (time.mktime(time.localtime(sessionSaleTime/1000)) - time.time() > float(
                        config['wait_time'])):
                    log.info(u"---尚未到开售时间，刷新等待---")
                    time.sleep(0.1)
            else:
                # ID_CARD 被归类到这里
                # 电子票、没有座位:https://m.piaoxingqiu.com/content/63808f2945b6d00001d4718b
                time.sleep(0.5)
                if len(audienceId) > 1:

                    headers = {
                        'Host': 'm.piaoxingqiu.com',
                        #'front-trace-id': 'm7lkmt4t210p8wcqdbl',
                        'src': 'weixin_mini',
                        #'merchant-id': '6267a80eed218542786f1494',
                        'access-token': self.access_token,
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c29)XWEB/11581',
                        'content-type': 'application/json',
                        'xweb_xhr': '1',
                        'terminal-src': 'WEIXIN_MINI',
                        #'angry-dog': 'NDY5OTU1OWUyYTI2OTc5ZWJmYmJiYWM3ZGI4MTkzYmEyNjFmMTU2YjIwMzM2ZjU5MDA1MmI5MDYzZmYxYWU2ZTpmMDY2YWI3YzI5NGZiMzYyZDE3ODAzNjA3MGEzZjQ0N2NjYTkzNzhjYTE4NDE0MGJlNDBlYzU4M2Q2MDU4NmI2NWQ4OGQxZDYyNTY5YTc4Y2YyYzMxMWYyZjNlY2VjNGVjMGUzYzc3ZjRjYTM2YzBlOTcxYzRkMDI4OTc3MjUwNDZlZmJlZTMyYmMwNzQxOTczNWM1MzEyNTNkNTgxMmUwNTRkZTk3OGE5MWQwYTIzYTdhZmQ0OGM4NzJlYmRkOGQ6MTc0MDU1MzQ0NDMwNQ',
                        'ver': '4.26.6',
                        'accept': '*/*',
                        'sec-fetch-site': 'cross-site',
                        'sec-fetch-mode': 'cors',
                        'sec-fetch-dest': 'empty',
                        'referer': 'https://servicewechat.com/wxad60dd8123a62329/321/page-frame.html',
                        'accept-language': 'zh-CN,zh;q=0.9'
                    }
                    data = get_param_data(audienceId, bsCityId, seatPlanId, bizShowSessionId,
                                          deliverMethod, price, ticket_num, showId)

                    result = requests.post(url, headers=headers, data=json.dumps(data), timeout=10,
                                           verify=False, ).json()
                    print(result)
                    if result['comments'] == "成功":
                        log.info(str("---抢票成功，请尽快付款---"))
                        time.sleep(1000)
                        break

                    else:
                        time.sleep(config['requesut_time'])
                        continue

    def load_config_or_default(self):
        """加载已保存配置或返回默认值"""
        try:
            with open("search_config.json", "r", encoding="utf-8") as f:
                self.current_config = json.load(f)
            return {
                "show": f"{self.current_config.get('showName', '')} ({self.current_config.get('showId', '')})",
                "session": self.current_config.get('bizShowSessionId', '未选择'),
                "ticket": f"{self.current_config.get('seatPlanId', '')} ¥{self.current_config.get('price', 0)}",
                "quantity": self.current_config.get('ticket_num', 0),
                "audience": f"{self.current_config.get('audienceId', '未选择')}"
            }
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "show": "未选择",
                "session": "未选择",
                "ticket": "未选择",
                "quantity": 0,
                "audience": "未选择"
            }
        except Exception as e:
            messagebox.showerror("配置错误", f"加载配置失败: {str(e)}")
            return self.load_config_or_default()  # 返回默认值

    def refresh_parameter_display(self):
        """刷新参数展示区域"""
        new_values = self.load_config_or_default()
        self.display_labels["show"].config(text=f"演出信息：{new_values['show']}")
        self.display_labels["session"].config(text=f"场次信息：{new_values['session']}")
        self.display_labels["ticket"].config(text=f"票价信息：{new_values['ticket']}")
        self.display_labels["quantity"].config(text=f"购票数量：{new_values['quantity']}")
        self.display_labels["audience"].config(text=f"观影人：{new_values['audience']}")
        self.search_frame.destroy()

    def show_order_config(self):
        """显示抢票参数配置窗口"""
        config_window = tk.Toplevel(self.root)
        config_window.title("抢票参数配置")

        notebook = ttk.Notebook(config_window)

        # 创建搜索选项卡
        search_tab = ttk.Frame(notebook)
        self.create_search_ui(search_tab)

        # 创建手动输入选项卡
        manual_tab = ttk.Frame(notebook)
        self.create_manual_input(manual_tab)

        notebook.add(search_tab, text="搜索选择")
        notebook.add(manual_tab, text="手动输入")
        notebook.pack(expand=1, fill="both")

    def perform_search(self):
        """执行演出搜索"""
        keyword = self.search_entry.get()
        if not keyword:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return

        try:
            result = default_show(self.access_token, '3208', '20', 'NEW', keyword)

            #
            self.search_tree.delete(*self.search_tree.get_children())
            for show in result['data']['searchData']:
                self.search_tree.insert("", "end", values=(show['showId'], show['showName']))
        except Exception as e:
            messagebox.showerror("错误", f"搜索失败: {str(e)}")

    def on_show_selected(self, event):
        """处理演出选择事件"""
        selected = self.search_tree.selection()
        if not selected:
            return

        item = self.search_tree.item(selected[0])
        self.current_show = {
            "showId": item["values"][0],
            "showName": item["values"][1]
        }

        self.load_sessions()

    def load_sessions(self):
        """加载场次信息"""
        try:
            results = get_showInformation(self.current_show["showId"], self.access_token)['data']

            sessions = []
            for session in results:
                session_info = f"{session['sessionName']} ({session['bizShowSessionId']})"
                sessions.append(session_info)
            self.session_combo["values"] = sessions
            if sessions:
                self.session_combo.current(0)
                self.on_session_selected(None)  # 自动触发场次选择
        except Exception as e:
            messagebox.showerror("错误", f"加载场次失败: {str(e)}")

    def on_session_selected(self, event):
        """处理场次选择事件"""
        selected_session = self.session_combo.get()
        if not selected_session:
            return

        # 提取场次ID
        self.current_session_id = selected_session.split("(")[-1].strip(")")
        self.load_ticket_plans()

    def on_price_selected(self, event):
        """处理场次选择事件"""
        print("---------")
        # selected_price = self.session_combo.get()
        # if not selected_price:
        #     return
        #
        # # 提取场次ID
        # self.current_session_id = selected_price.split("(")[-1].strip(")")
        # self.load_ticket_plans()

    def load_ticket_plans(self):
        """加载票价信息"""
        try:
            results = get_showInformation(self.current_show["showId"], self.access_token)['data']
            prices = []
            for session in results:
                if session['bizShowSessionId'] == self.current_session_id:
                    for plan in session['seatPlans']:
                        price_info = f"{plan['seatPlanName']} ({plan['seatPlanId']}) - ¥{plan['originalPrice']}"
                        prices.append(price_info)
            self.price_combo["values"] = prices
            if prices:
                self.price_combo.current(0)
        except Exception as e:
            messagebox.showerror("错误", f"加载票价失败: {str(e)}")

    def load_audiences(self):
        """加载观影人数据"""
        try:
            audiences = get_audienceIds(self.access_token)
            items = [f"{a['name']} ({a['id']})" for a in audiences]
            self.audience_combo["values"] = items
            if items:
                self.audience_combo.current(0)
        except Exception as e:
            messagebox.showerror("错误", f"加载观影人失败: {str(e)}")

    def create_search_ui(self, parent):
        """创建搜索选择界面"""
        self.search_frame = ttk.Frame(parent, padding=10)
        self.search_frame.pack(fill="both", expand=True)

        # 搜索框
        ttk.Label(self.search_frame, text="搜索演出:").grid(row=0, column=0)
        self.search_entry = ttk.Entry(self.search_frame, width=30)
        self.search_entry.grid(row=0, column=1)
        ttk.Button(self.search_frame, text="搜索",
                   command=self.perform_search).grid(row=0, column=2)

        # 搜索结果列表
        self.search_tree = ttk.Treeview(self.search_frame, columns=("showId", "showName"), show="headings", height=5)
        self.search_tree.heading("showId", text="演出ID")
        self.search_tree.heading("showName", text="演出名称")
        self.search_tree.grid(row=1, columnspan=3, pady=5)
        self.search_tree.bind("<<TreeviewSelect>>", self.on_show_selected)

        # 场次选择
        ttk.Label(self.search_frame, text="选择场次:").grid(row=2, column=0)
        self.session_combo = ttk.Combobox(self.search_frame, state="readonly")
        self.session_combo.grid(row=2, column=1)
        self.session_combo.bind("<<ComboboxSelected>>", self.on_session_selected)

        # 票价选择
        ttk.Label(self.search_frame, text="选择票价:").grid(row=3, column=0)
        self.price_combo = ttk.Combobox(self.search_frame, state="readonly")
        self.price_combo.grid(row=3, column=1)
        self.price_combo.bind("<<PriceSelected>>", self.on_price_selected)

        # 其他参数
        ttk.Label(self.search_frame, text="购票数量:").grid(row=4, column=0)
        self.quantity_spin = ttk.Spinbox(self.search_frame, from_=1, to=10)
        self.quantity_spin.grid(row=4, column=1)

        ttk.Label(self.search_frame, text="选择观影人:").grid(row=5, column=0)
        self.audience_combo = ttk.Combobox(self.search_frame)
        self.audience_combo.grid(row=5, column=1)
        self.load_audiences()
        btn_frame = ttk.Frame(self.search_frame)
        btn_frame.grid(row=6, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="保存配置",
                   command=self.save_search_config).pack(side="left", padx=5)

    def save_search_config(self):
        """保存搜索选择的配置"""
        if not hasattr(self, 'current_show'):
            messagebox.showwarning("提示", "请先选择演出信息")
            return

        cur_config = {
            "showId": self.current_show["showId"],
            "showName": self.current_show["showName"],
            "bizShowSessionId": self.current_session_id,
            "seatPlanId": self.price_combo.get().split("(")[-1].split(")")[0],
            "price": float(self.price_combo.get().split("¥")[-1]),
            "ticket_num": int(self.quantity_spin.get()),
            "audienceId": self.audience_combo.get().split("(")[-1].strip(")")
        }

        try:
            with open("search_config.json", "w", encoding="utf-8") as f:
                json.dump(cur_config, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("成功", "配置已保存为 search_config.json")

            self.refresh_parameter_display()
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")

    def apply_search_config(self):
        """应用搜索选择的配置"""
        try:
            # 验证必填项
            if not all([
                self.current_show,
                self.current_session_id,
                self.price_combo.get(),
                self.audience_combo.get()
            ]):
                raise ValueError("请完成所有选项选择")

            # 构造参数
            self.order_params = {
                "showId": self.current_show["showId"],
                "bizShowSessionId": self.current_session_id,
                "seatPlanId": self.price_combo.get().split("(")[-1].split(")")[0],
                "price": float(self.price_combo.get().split("¥")[-1]),
                "ticket_num": int(self.quantity_spin.get()),
                "priceItemVal": 0,  # 运费根据实际情况调整
                "audienceId": [self.audience_combo.get().split("(")[-1].strip(")")]
            }

            self.update_display()
            messagebox.showinfo("成功", "配置已应用！")
            self.search_frame.destroy()


        except Exception as e:
            messagebox.showerror("错误", f"配置不完整: {str(e)}")

    # 新增配置加载方法
    # def load_search_config(self):
    #     """加载已保存的搜索配置"""
    #     try:
    #         with open("search_config.json", "r", encoding="utf-8") as f:
    #             config = json.load(f)
    #
    #         # 自动填充搜索框
    #         self.search_entry.delete(0, tk.END)
    #         self.search_entry.insert(0, config["showName"])
    #         self.perform_search()  # 触发搜索
    #
    #         # 稍后自动选择配置（需要事件循环处理）
    #         self.root.after(100, lambda: self.auto_select_config(config))
    #
    #     except FileNotFoundError:
    #         messagebox.showinfo("提示", "未找到保存的配置")
    #     except Exception as e:
    #         messagebox.showerror("错误", f"加载配置失败: {str(e)}")

    # def auto_select_config(self, config):
    #     """自动选择已保存的配置"""
    #     try:
    #         # 选择演出
    #         for child in self.search_tree.get_children():
    #             if self.search_tree.item(child)["values"][0] == config["showId"]:
    #                 self.search_tree.selection_set(child)
    #                 self.search_tree.focus(child)
    #                 self.on_show_selected(None)
    #                 break
    #
    #         # 选择场次
    #         self.session_combo.set(
    #             next(s for s in self.session_combo["values"]
    #                  if config["bizShowSessionId"] in s)
    #         )
    #         self.on_session_selected(None)
    #
    #         # 选择票价
    #         self.price_combo.set(
    #             next(p for p in self.price_combo["values"]
    #                  if config["seatPlanId"] in p)
    #         )
    #
    #         # 设置数量
    #         self.quantity_spin.delete(0, tk.END)
    #         self.quantity_spin.insert(0, str(config["ticket_num"]))
    #
    #         # 选择观影人
    #         self.audience_combo.set(
    #             next(a for a in self.audience_combo["values"]
    #                  if config["audienceId"] in a)
    #         )
    #
    #     except Exception as e:
    #         messagebox.showwarning("警告", f"自动选择失败: {str(e)}\n请手动完成剩余配置")

    def create_manual_input(self, parent):
        """创建手动输入界面"""
        manual_frame = ttk.Frame(parent, padding=10)
        manual_frame.pack(fill="both", expand=True)

        params = [
            ("showId", "演出ID"),
            ("bizShowSessionId", "场次ID"),
            ("seatPlanId", "票价ID"),
            ("price", "票价"),
            ("ticket_num", "数量"),
            ("priceItemVal", "运费")
        ]

        self.manual_entries = {}
        for idx, (key, label) in enumerate(params):
            ttk.Label(manual_frame, text=label + ": ").grid(row=idx, column=0, sticky="e")
            entry = ttk.Entry(manual_frame) if key != "ticket_num" else ttk.Spinbox(manual_frame, from_=1, to=10)
            entry.grid(row=idx, column=1, pady=2)
            self.manual_entries[key] = entry

        ttk.Label(manual_frame, text="选择观影人:").grid(row=len(params), column=0)
        self.manual_audience_combo = ttk.Combobox(manual_frame)
        self.manual_audience_combo.grid(row=len(params), column=1)
        self.load_audiences()

        ttk.Button(manual_frame, text="应用配置",
                   command=self.apply_manual_config).grid(row=len(params) + 1, columnspan=2)

    def apply_manual_config(self):
        """应用手动输入的配置"""
        try:
            self.order_params = {
                "showId": self.manual_entries["showId"].get(),
                "bizShowSessionId": self.manual_entries["bizShowSessionId"].get(),
                "seatPlanId": self.manual_entries["seatPlanId"].get(),
                "price": float(self.manual_entries["price"].get()),
                "ticket_num": int(self.manual_entries["ticket_num"].get()),
                "priceItemVal": float(self.manual_entries["priceItemVal"].get() or 0),
                "audienceId": [self.manual_audience_combo.get().split("(")[-1].strip(")")]
            }
            self.update_display()
            messagebox.showinfo("成功", "参数配置已更新！")
        except Exception as e:
            messagebox.showerror("错误", f"参数错误：{str(e)}")

    def update_display(self):
        """更新参数展示"""
        self.display_labels["show"].config(
            text=f"演出ID：{self.order_params.get('showId', '')}")
        self.display_labels["session"].config(
            text=f"场次ID：{self.order_params.get('bizShowSessionId', '')}")
        self.display_labels["ticket"].config(
            text=f"票价ID：{self.order_params.get('seatPlanId', '')} 价格：{self.order_params.get('price', 0)}")
        self.display_labels["quantity"].config(
            text=f"购票数量：{self.order_params.get('ticket_num', 0)}")
        self.display_labels["audience"].config(
            text=f"观影人：{self.order_params.get('audienceId', [''])[0]}")

    def start_order_process(self):
        """启动抢票流程"""

        if not hasattr(self, 'current_config'):
            messagebox.showerror("错误", "请先配置抢票参数！")
            return

        # 显示确认对话框
        confirm_msg = "\n".join([
            "请确认以下抢票信息：",
            f"演出ID：{self.current_config['showId']}",
            f"场次ID：{self.current_config['bizShowSessionId']}",
            f"票价ID：{self.current_config['seatPlanId']}",
            f"数量：{self.current_config['ticket_num']}",
            f"观影人：{self.current_config['audienceId']}"
        ])

        if messagebox.askyesno("确认信息", confirm_msg):
            sessionSaleTime = self.seat_plan()
            Thread(target=self.run_order_task, args=(sessionSaleTime,)).start()

    def seat_plan(self):
        params = {
            'src': 'WEB',
            'ver': '4.19.6',
            'source': 'FROM_QUICK_ORDER',
        }
        print(
            'https://m.piaoxingqiu.com/cyy_gatewayapi/show/pub/v5/show/' + self.current_config['showId'] + '/session/' +
            self.current_config['bizShowSessionId'] + '/seat_plans', )
        result2 = requests.get(
            'https://m.piaoxingqiu.com/cyy_gatewayapi/show/pub/v5/show/' + self.current_config['showId'] + '/session/' +
            self.current_config['bizShowSessionId'] + '/seat_plans',
            params=params,
            headers=self.headers,
        ).json()

        try:
            return result2["data"]["sessionSaleTime"]
        except:
            return None

    def run_order_task(self, params):
        """执行抢票任务的线程方法"""

        try:
            self.order_info_with_params(sessionSaleTime=params)
            messagebox.showinfo("成功", "抢票请求已提交，请查看日志！")
        except Exception as e:
            messagebox.showerror("错误", f"抢票失败：{str(e)}")

    def add_audience(self):
        name = simpledialog.askstring("输入", "请输入姓名:")
        idcard = simpledialog.askstring("输入", "请输入身份证号:")
        if name and idcard:
            try:
                add_audiences(name, idcard, self.access_token)
                messagebox.showinfo("成功", "观影人添加成功")
            except Exception as e:
                messagebox.showerror("错误", f"添加失败: {str(e)}")

    # def start_order(self):
    #     Thread(target=self.run_order_process).start()

    # def run_order_process(self):
    #     try:
    #         order_info(self.access_token, self.headers, self.cellphone)
    #     except Exception as e:
    #         messagebox.showerror("错误", f"抢票失败: {str(e)}")


if __name__ == "__main__":
    urllib3.disable_warnings()
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    keyboard.unhook_all_hotkeys()
