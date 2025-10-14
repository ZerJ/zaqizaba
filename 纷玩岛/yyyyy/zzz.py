import requests
from time import  time
from hashlib import md5
import urllib.parse
inner_c = 'ce8b64d6c1a0a275d8822ad273315eb3_1741680393062'
t=int(round(time() * 1000))
show_id="891097237968"
url = "https://mtop.damai.cn/h5/mtop.alibaba.detail.subpage.getdetail/2.0/"
params = {
    'jsv': '2.7.4',
    'appKey': '12574478',
    't': f'{t}',
    'sign': 'cfcc345ab6871c74f3b1d45ff536d261',
    'api': 'mtop.alibaba.detail.subpage.getdetail',
    'v': '2.0',
    'H5Request': 'true',
    'type': 'originaljson',
    'timeout': '10000',
    'dataType': 'json',
    'valueType': 'original',
    'forceAntiCreep': 'true',
    'AntiCreep': 'true',
    'useH5': 'true',
    'data': '{"itemId":"' + show_id + '","bizCode":"ali.china.damai","scenario":"itemsku","exParams":"{\\"dataType\\":4,\\"dataId\\":\\"''\\",\\"privilegeActId\\":\\"\\"}","platform":"8","comboChannel":"2","dmChannel":"damai@damaih5_h5"}',
}
plain = f"{inner_c.split('_')[0]}&{t}&12574478&{params["data"]}"
params["sign"]=md5(plain.encode(encoding='utf-8')).hexdigest()
print(params["sign"])
u=f"{url}?{urllib.parse.urlencode(params)}"
print(u)
payload = {}
headers = {
    'accept': 'application/json',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://m.damai.cn',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://m.damai.cn/',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    'Cookie': 'cna=76nVH2e97i8CAd5McpVCnA2A; xlly_s=1; _samesite_flag_=true; cookie2=1b82ba498b76eedf3896a3336887f7b0; t=c1868b52817307e45b36d84041c6883d; _tb_token_=eee1a631b6433; _hvn_login=18; munb=2216789454799; mtop_partitioned_detect=1; sgcookie=E100M9x3t7AmDz13MqysA3XtCkCEoavGpFS9YljbhoCqO%2FJV%2B1lFkSUJl9af%2Fff%2BSpo19QIhX9RUCmfK0d1pFUbkYWPp3C1Lte0%2Fs7iHlFjkF9A%3D; csg=dc42e0ce; _m_h5_tk=ce8b64d6c1a0a275d8822ad273315eb3_1741681868746; _m_h5_tk_enc=02ad026e9aa934c7f52b26a026d47d0a; dm_nickname=%E9%BA%A6%E5%AD%905TwJd; usercode=461874011; havanaId=2216789454799; isg=BFNThIRVMLVBjfzgTlAdujKg4td9COfK3tKImAVwGnKphHImjdtaHkSSvvTqJD_C; tfstk=gYdKdhfKccmnvzCmtXMgZgPDbU0iSQLFBH8bZgj3FhK9jGAo8eDEwdKWjMNHZ6q5VGtLZpYHPzQWjhtRU2SlVgKkPp0iijYe8_55wmcmi9rZ3KK8V9sIP1_RoygGddKu305SmmcgIP6Ex_thbskQWFsNyaw7N3_11Zs_VJt5AOZ1kZ55V3t75f_fk8ZCNTwsWaS1V_1WV1Gzj2IaRwFJh546oCmA17NW6wBsIes6oEulR9I6RGnjcCFVpiTCX7iqaXiO2GRjjALw0pth73hxX_-wF3_JflilLU99XwKnDuSkTeAR7eHIvFC1vU6RMzGBW6IdhBKgRWxXWU9cBC0jg6CCALferrnHWBKH8CLuPR1dtdBv9sG4AgvMkQQJa0l9DERwXNtjwDsrpIAAHTZcDa2IWVezU9_wZH6MRFKcjk_Om26QU8Wl7NImWVezUTbNWi0QN8yPEN5..; _m_h5_tk=4f9b187ae09bb2b16c143dfaf5fbdecf_1741683312130; _m_h5_tk_enc=dd0a175cefee8534129b352f265aa927; mtop_partitioned_detect=1'
}

response = requests.request("GET", u, headers=headers, data=payload)

print(response.text)
