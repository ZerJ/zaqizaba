# -*- coding: utf-8 -*-

import warnings
warnings.filterwarnings('ignore')
import requests
import json
with open('./config.json', 'r', encoding='utf_8_sig') as f:
    config = json.loads(f.read())
token=""

def get_projectId(keyword):

    headers = {
        'Host': 'api.livelab.com.cn',
        'Xweb_xhr': '1',
        'Platform-Version': '3.3.1',
        'Platform-Type': '%E7%BA%B7%E7%8E%A9%E5%B2%9B%E5%BE%AE%E4%BF%A1%E5%B0%8F%E7%A8%8B%E5%BA%8F',
        'X-Fwd-Anonymousid': '1734659996937-5078017-04694c10035f068-17650497',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c11)XWEB/11581',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://servicewechat.com/wx5a8f481d967649eb/103/page-frame.html',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'close',
    }

    json_data = {
        'cityName': '海南',
        'keyword': keyword,
        'channel': '2',
    }

    response = requests.post('https://api.livelab.com.cn/search/app/search/text', headers=headers, json=json_data, verify=False).json()
    print(response)
    for data in response['data']:
        print(data)


def send_sms(cellphone):
    url = "https://api.livelab.com.cn/thirdParty/sms/app/captcha"

    payload = "phone="+cellphone+"&type=1"
    headers = {
        'user-agent': 'Dart/3.3 (dart:io)',
        'content-type': 'application/x-www-form-urlencoded;charset=utf-8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Length': '24',
        'host': 'api.livelab.com.cn',
        'Connection': 'keep-alive'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

def phone_captcha(phone,captcha):

    url = "https://api.livelab.com.cn/auth/app/login/phoneCaptcha"

    payload = "phone="+phone+"&captcha="+captcha+"&sekyCaptcha=&deviceId=07b515e35c885056&deviceType=2&blackBox="
    headers = {
        'user-agent': 'Dart/3.3 (dart:io)',
        'content-type': 'application/x-www-form-urlencoded;charset=utf-8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Length': '94',
        'host': 'api.livelab.com.cn',
        'Connection': 'keep-alive'
    }

    response = requests.request("POST", url, headers=headers, data=payload,verify=False)

    print(response.text)
    print(response.json()["data"]["token"])
    token=response.json()["data"]["token"]
    return token

def get_performance(project_id):

    headers = {
        'Host': 'api.livelab.com.cn',
        'Xweb_xhr': '1',
        'Platform-Version': '3.3.1',
        'Platform-Type': '%E7%BA%B7%E7%8E%A9%E5%B2%9B%E5%BE%AE%E4%BF%A1%E5%B0%8F%E7%A8%8B%E5%BA%8F',
        'X-Fwd-Anonymousid': '1734659996937-5078017-04694c10035f068-17650497',
        'Authorization': config['Authorization'],
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c11)XWEB/11581',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://servicewechat.com/wx5a8f481d967649eb/103/page-frame.html',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'close',
    }
    params = {
        'project_id': project_id, 'v': '1734624002', 'retry': 'false',
    }

    response = requests.get(
        'https://api.livelab.com.cn/performance/app/project/get_performs',
        params=params,
        headers=headers,
        verify=False,
    ).json()
    print(response)
    performs = (response['data']['performInfos'][0]['performInfo'][0]['seatPlans'])
    for i in range(len(performs)):
        print("请选择: {} 模式".format(i) + "-----" + str(performs[i]))

    infos = input("请选择对应的模式:")
    seatPlanId = performs[int(infos)]['seatPlanId']
    performId = performs[int(infos)]['performId']
    price = performs[int(infos)]['price']
    return price, performId, project_id, seatPlanId



def order(price,performId,projectId,seatPlanId,frequentIds):
    headers = {
        'Host': 'api.livelab.com.cn',
        'Xweb_xhr': '1',
        'Platform-Version': '3.3.1',
        'Platform-Type': '%E7%BA%B7%E7%8E%A9%E5%B2%9B%E5%BE%AE%E4%BF%A1%E5%B0%8F%E7%A8%8B%E5%BA%8F',
        'X-Fwd-Anonymousid': '1734659996937-5078017-04694c10035f068-17650497',
        'Authorization': config['Authorization'],
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c11)XWEB/11581',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://servicewechat.com/wx5a8f481d967649eb/103/page-frame.html',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'close',
    }

    json_data = {
        'deliveryType': 1,
        'contactName': config['contactName'],
        'contactPhone': config['contactPhone'],
        'combineTicketVos': None,
        'ordinaryTicketVos': None,
        'payment': price,
        'totalPrice': price,
        'performId': performId,  #场次id
        'projectId': projectId,#项目ID
        'privilegeCodeList': [],
        'audienceCount': 1,
        'frequentIds': [
            frequentIds,
        ],
        'seatPlanIds': [
            seatPlanId,
        ],
        'blackBox': ':0',
    }
    response = requests.post('https://api.livelab.com.cn/order/app/center/v3/create', headers=headers, json=json_data, verify=False)
    print(response.json())


def getMemberList():
    url = "https://api.livelab.com.cn/member/member/bearer/app/list"

    payload = {}
    headers = {
        'Host': 'api.livelab.com.cn',
        'xweb_xhr': '1',
        'platform-version': '3.3.2',
        'platform-type': '%E7%BA%B7%E7%8E%A9%E5%B2%9B%E5%BE%AE%E4%BF%A1%E5%B0%8F%E7%A8%8B%E5%BA%8F',
        'x-fwd-anonymousid': 'ocXac5O_YiObtdoxFfbky8tsnTBk',
        'authorization': config['Authorization'],
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c2d)XWEB/11581',
        'content-type': 'application/json',
        'accept': '*/*',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wx5a8f481d967649eb/104/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9'
    }

    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    print(response.json()["data"])
# print(token)
phone = input("请输入电话号码：")
send_sms(phone)
captcha =input("请输入验证码：")
token=phone_captcha(phone,captcha)
print(token)
keyword = input("请输入需要搜索内容:")  #下一站
get_projectId(keyword)  # 6258744554
project_id = input("请输入待抢购的场次的projectId:")
price, performId, projectId, seatPlanId = get_performance(project_id)
getMemberList()
frequentIds = input("请输入观影人的frequentIds:")
order(price, performId, projectId, seatPlanId,frequentIds)