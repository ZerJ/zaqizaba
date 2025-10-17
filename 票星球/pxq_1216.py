# -*- coding: utf-8 -*-
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

w = wmi.WMI()
# 全局变量，用于控制程序的暂停和继续
paused = False
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
LogsPath = os.path.join('./',  'logs\log_{0}'.format(time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())))

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
        fh.close() #不关闭会警告

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

    audienceIds_list = []
    url = 'https://m.piaoxingqiu.com/cyy_gatewayapi/user/buyer/v3/user_audiences?src=WEB&channelId=&terminalSrc=WEB&offset=0&length=50&bizCode=FHL_M&idTypes=ID_CARD,PASSPORT,MAINLAND_TRAVEL_PERMIT_TAIWAN,MAINLAND_TRAVEL_PERMIT_HK_MC&showId='
    resp = requests.get(url, headers=headers).json()['data']
    return resp


def get_addressId():

    url = 'https://m.piaoxingqiu.com/cyy_gatewayapi/user/buyer/v3/user/addresses/default?showId=&src=WEB&channelId=&terminalSrc=WEB'
    resp = requests.get(url, headers=headers)
    dic_ = {}
    dic_['detailAddress'] = resp.json()['data']['detailAddress']
    dic_['addressId'] = resp.json()['data']['addressId']
    dic_['receiver'] = resp.json()['data']['username']
    dic_['cellphone'] = resp.json()['data']['cellphone']
    dic_['province'] = resp.json()['data']['location']['locationId'][0:2]
    dic_['city'] = resp.json()['data']['location']['locationId'][2:4]
    dic_['district'] = resp.json()['data']['location']['locationId'][4:6]
    return dic_



def get_locationCityId(headers):
    url = 'https://m.piaoxingqiu.com/cyy_gatewayapi/home/pub/v3/citys/current_location?src=WEB&channelId=&terminalSrc=WEB'
    resp = requests.get(url, headers=headers)
    return resp.json()['data']['cityId']

def get_deliverMethod(seatPlanId,bizShowSessionId,showId,price,ticket_num):
    url = 'https://m.piaoxingqiu.com/cyy_gatewayapi/trade/buyer/order/v3/pre_order?channelId=&terminalSrc=WEB'
    data = {
            "items":[
                {"skus":[
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
        "src":"WEB"
    }
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    return resp.json()['data']['supportDeliveries'][0]['name']


def get_param_data(audienceId, locationCityId, seatPlanId, bizShowSessionId,
                   deliverMethod,price, ticket_num,showId):
    data = {
        "audienceIds": audienceId[0],
        "addressParam": {},
        "contactParam": {},
        "locationParam": {
            "locationCityId": locationCityId
        },
        "paymentParam": {
            "totalAmount": price * ticket_num,
            "payAmount": price * ticket_num
        },
        "priceItemParam": [
            {"applyTickets": [],
             "priceItemName": "票款总额",
             "priceItemVal": price * ticket_num,
             "priceItemType": "TICKET_FEE",
             "priceItemSpecies":"SEAT_PLAN",
             "direction": "INCREASE",
             "priceDisplay": "￥{}".format(price * ticket_num)
             }
        ],
        "items": [
            {"skus": [
                {
                    "seatPlanId": seatPlanId,
                    "sessionId": bizShowSessionId,
                    "showId": showId,
                    "skuId": seatPlanId,
                    "skuType": "SINGLE",
                    "ticketPrice": price,
                    "qty": ticket_num,
                    "deliverMethod": deliverMethod
                }
            ],
                "spu": {
                    "id": showId,
                    "spuType": "SINGLE"
                }
            }
        ],
        "many2OneAudience": {},
        "one2oneAudiences": [
            {"audienceId": audienceId[0],
             "sessionId": bizShowSessionId
             },
        ],
        "src": "WEB"
    }
    return data



def get_express_param_data(audienceId, locationCityId, seatPlanId,
                           bizShowSessionId, deliverMethod,price,ticket_num,priceItemVal,showId):
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
                "deliverMethod": deliverMethod
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
        # "many2OneAudience": {},
        "one2oneAudiences": [{
            "audienceId": audienceId[0],
            "sessionId": bizShowSessionId
        }],
        "src": "WEB"
    }
    return data


def default_show(access_token,cityId,length,sortType,keyword):


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
        'length': length, #演唱会长度
        'offset': '0',
        'pageType': 'SEARCH_PAGE',
        'sortType': sortType,    # ATTENTION:热点排序  NEW：最新排序 RECOMMEND：推荐排序
        'src': 'WEB',
        'ver': '4.1.2-20240305183007',
    }

    response = requests.get('https://m.piaoxingqiu.com/cyy_gatewayapi/home/pub/v3/show_list/search', params=params, headers=headers).json()
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
        'https://m.piaoxingqiu.com/cyy_gatewayapi/show/pub/v5/show/{}/sessions?src=WEB&ver=4.19.6&source=FROM_QUICK_ORDER&isQueryShowBasicInfo=true'.format(showId),
        headers=headers, data=data).json()
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

    response = requests.post(
        'https://m.piaoxingqiu.com/cyy_gatewayapi/user/pub/v3/generate_photo_code',
        headers=headers,
        json=json_data,
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

    response = requests.post(
        'https://m.piaoxingqiu.com/cyy_gatewayapi/user/pub/v3/send_verify_code',
        headers=headers,
        json=json_data,
    ).json()
    return response

def get_user_choice(prompt):
    while True:
        choice = input(prompt).strip().lower()
        if choice in ['y', 'n']:
            return choice == 'y'
        else:
            print("无效输入，请输入 'y' 或 'n'。")


def get_captcha(cellphone):
    baseCode = get_baseCode(cellphone)
    head, context = baseCode.split(",")  # 将base64_str以“,”分割为两部分
    img_data = base64.b64decode(context)  # 解码时只要内容部分
    with open('captcha.png', 'wb') as f:
        f.write(img_data)


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

    response = requests.get('https://m.piaoxingqiu.com/cyy_gatewayapi/user/buyer/v3/profile', headers=headers, data=data).json()
    return response


def get_access_token(cellphone,verifyCode):
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
    ).json()

    access_token = response['data']['accessToken']

    result = login_success_message(access_token)
    log_success = "用户" + result['data']['nickname'] + "登录成功"

    return access_token,log_success


def get_ip_geolocation(ip):
    ipinfo_url = f'http://ipinfo.io/{ip}/json'

    response = requests.get(ipinfo_url)
    response.raise_for_status()
    return response.json()



def order_info(access_token,headers,cellphone):

    url = 'https://m.piaoxingqiu.com/cyy_gatewayapi/trade/buyer/order/v3/create_order?channelId=&terminalSrc=WEB'

    with shelve.open('./parameters.db') as db:
        use_previous = False
        deliver_method_exists = False
        # 检查是否已经存储了参数
        if 'deliverMethod' in db:
            deliver_method_exists = True
            use_previous = get_user_choice("发现上次存储的参数，是否使用？(y/n): ")

        if deliver_method_exists and use_previous:
            audienceId = db['audienceId']
            locationCityId = db['locationCityId']
            seatPlanId = db['seatPlanId']
            bizShowSessionId = db['bizShowSessionId']
            deliverMethod = db['deliverMethod']
            price = db['price']
            ticket_num = db['ticket_num']
            priceItemVal = db['priceItemVal']
            showId = db['showId']
        else:
            while True:
                confirm = get_user_choice("是否需要手动添加观影人信息，是否使用？(y/n) : ")
                if confirm:
                    name = input("请输入需要添加的观影人姓名:")
                    idcard = input("请输入需要添加的观影人身份证:")
                    add_audiences(name, idcard, access_token)
                    continue
                else:
                    break
            search_content = input("请输入搜索内容:")
            result = default_show(access_token, '3208', '20', 'NEW', search_content)
            deatail_datas = result['data']['searchData']
            for deatail in deatail_datas:
                print("showId:   {},   showName:   {}".format(deatail['showId'], deatail['showName']))
            showId = input("请输入待抢购的showId:")

            results = get_showInformation(showId, access_token)['data']


            try:
                for result in results:
                    session = result['bizShowSessionId']  # 场次ID
                    sessionName = result['sessionName']
                    for de_result in result['seatPlans']:
                        seatPlanId = de_result['seatPlanId']  # 票价ID
                        originalPrice = de_result['originalPrice']
                        seatPlanName = de_result['seatPlanName']
                        print("场次ID:{},   场次名称:{},   票价ID:{},   价格:{}-{}".format(session, sessionName, seatPlanId, originalPrice,
                                                                                 seatPlanName))
            except:
                for result in results:
                    session = result['bizShowSessionId']  # 场次ID
                    sessionName = result['sessionName']

                    params = {
                        'src': 'WEB',
                        'ver': '4.19.6',
                        'source': 'FROM_QUICK_ORDER',
                    }
                    result2 = requests.get(
                        'https://m.piaoxingqiu.com/cyy_gatewayapi/show/pub/v5/show/66d1407e1c27320001ea6519/session/66d140b445d00b0001e457fa/seat_plans',
                        params=params,
                        headers=headers,
                    ).json()
                    for de_result in result2['data']['seatPlans']:
                        seatPlanId = de_result['seatPlanId']  # 票价ID
                        originalPrice = de_result['originalPrice']
                        seatPlanName = de_result['seatPlanName']
                        print("场次ID:{},   场次名称:{},   票价ID:{},   价格:{}-{}".format(session, sessionName, seatPlanId, originalPrice,
                                                                                 seatPlanName))


            locationCityId = get_locationCityId(headers)
            bizShowSessionId = input("请输入待抢购的场次ID:")
            seatPlanId = input("请输入待抢购的票价ID:")
            price = int(input("请输入带抢购的票价:"))
            ticket_num = int(input("请输入抢购的票数量:"))
            priceItemVal = int(input("请输入带抢购票的运费(如果没有则填写0):"))

            resp_audiences = get_audienceIds(access_token)
            for audience in resp_audiences:
                id = audience['id']
                name = audience['name']
                print("身份ID:  {},    姓名:{}".format(id, name))

            audienceId = []
            if ticket_num == 1:
                ids = input("请输入观演人人的身份ID:")
                audienceId.append(ids)
            elif ticket_num == 2:
                ids1 = input("请输入第一个观演人的身份ID:")
                ids2 = input("请输入第一个观演人的身份ID:")
                audienceId.append(ids1)
                audienceId.append(ids2)
            try:
                deliverMethod = get_deliverMethod(seatPlanId, bizShowSessionId, showId, price, ticket_num)
            except:
                deliverMethod = 'EXPRESS'
            log.info(deliverMethod)

            if os.path.exists('./parameters.db'):
                os.remove('./parameters.db')
            with shelve.open('./parameters.db') as db:
                db['audienceId'] = audienceId
                db['locationCityId'] = locationCityId
                db['seatPlanId'] = seatPlanId
                db['bizShowSessionId'] = bizShowSessionId
                db['deliverMethod'] = deliverMethod
                db['price'] = price
                db['ticket_num'] = ticket_num
                db['priceItemVal'] = priceItemVal
                db['showId'] = showId

    ###########################下单逻辑##############################
    while True:
        while paused:
            time.sleep(0.1)  # 暂停时，短暂休眠以降低CPU使用率
        if (time.mktime(time.strptime(config['buy_time'], "%Y %m %d %H %M %S")) - time.time() > float(config['wait_time'])):
            log.info(u"---尚未到开售时间，刷新等待---")
        else:

            if deliverMethod == 'EXPRESS':
                # 快递票:https://m.piaoxingqiu.com/content/63c2d785afec8c00018a3a2f
                if (len(audienceId) == 1):
                    data = get_express_param_data(audienceId, locationCityId, seatPlanId, bizShowSessionId, deliverMethod,price, ticket_num, priceItemVal,showId)
                    result = requests.post(url, headers=headers, data=json.dumps(data), timeout=10).json()

                    if result['comments'] == "成功":
                        log.info(str("---抢票成功，请尽快付款---"))
                        time.sleep(1000)
                        break
                    else:
                        result = requests.post(url, headers=headers, data=json.dumps(data), timeout=10).json()
                        time.sleep(config['requesut_time'])
                        continue
            else:
                # ID_CARD 被归类到这里
                # 电子票、没有座位:https://m.piaoxingqiu.com/content/63808f2945b6d00001d4718b
                if(len(audienceId) == 1):
                    data = get_param_data(audienceId, locationCityId, seatPlanId, bizShowSessionId,
                                          deliverMethod,price, ticket_num, showId)
                    result = requests.post(url, headers=headers, data=json.dumps(data), timeout=10).json()
                    if result['comments'] == "成功":
                        log.info(str("---抢票成功，请尽快付款---"))
                        time.sleep(1000)
                        break
                    else:
                        result = requests.post(url, headers=headers, data=json.dumps(data), timeout=10).json()
                        time.sleep(config['requesut_time'])
                        continue


def add_audiences(name, idcart, access_token):
    headers = {
        'Host': 'm.piaoxingqiu.com',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'src': 'WEB',
        'sec-ch-ua-mobile': '?0',
        'access-token':access_token ,
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
    ).json()

def main():

    global access_token
    global headers

    cellphone = input('请输入手机号:')
    get_captcha(cellphone)
    captcha = input("请输入图形验证码:")
    result = get_send_verifyCode(cellphone, captcha)
    verify_code = input("请输入短信验证码:")
    access_token, log_success = get_access_token(cellphone, verify_code)
    print("=========" + log_success + "=========")
    print(access_token)

    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        "access-token": access_token
    }
    order_info(access_token, headers, cellphone)



if __name__ == "__main__":
    a = """
        -------------------可以试用 Ctrl+Shift+P 来暂停或继续程序------------------------------                                                                                                                                               
        """
    print(a)
    try:
        print("按 Ctrl+Shift+P 来暂停或继续程序")
        main()
    except KeyboardInterrupt:
        print("程序已手动停止")
    finally:
        keyboard.unhook_all_hotkeys()












