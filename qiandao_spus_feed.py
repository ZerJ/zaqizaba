# -*- coding: utf-8 -*-
"""
qiandao 签名：还原 skey (production/development) + 生成 X-Request-Sign
复刻自你提供的 JS 片段：
- sl() 字符表 + Mu/Au 取值（带数组旋转归位）
- Qu() 数组 + Xu 取值（带数组旋转归位）
- il / ol 组合出 production / development skey
- 签名：path + sorted(query) + requestId + timestamp  -> HMAC-SHA256 -> hex小写 -> Base64(对hex做Base64)
"""
from urllib.parse import urlparse, parse_qsl, quote
import base64
import hashlib
import hmac
import time
import urllib
from collections import OrderedDict


# -----------------------------
# 工具：模仿 JS parseInt(字符串) 的行为（取前导整数部分）
# -----------------------------
def parse_int_prefix(s: str) -> int:
    neg = False
    i = 0
    if not s:
        return 0
    if s[0] == '-':
        neg = True
        s = s[1:]
    num = 0
    has_digit = False
    for ch in s:
        if '0' <= ch <= '9':
            has_digit = True
            num = num * 10 + (ord(ch) - 48)
        else:
            break
    if not has_digit:
        return 0
    return -num if neg else num


# -----------------------------
# sl() 来自你贴的 JS
# -----------------------------
def sl():
    return [
        "pi.", "NWR", "res", "rZB", "hanfu086.com", "length", "ZhY", "tusi.cn", "rra", "htt",
        "11VzfLOj", "concat", "red", "5089565Eaetsw", "req", "ine", "848690SJsScr", "14eNXFns",
        "5777435nBeqxl", "dat", "194890aCnDqs", "qdurl.green", "9948550vQtWtQ", "T9f", "58TAkEdf",
        "def", "JmZ", "push", "获取s", "5HE", "79328CBUbpI", "11540244uSmwIU", "2730OPZKYE", "isA",
        "bra", "ww=", "fT6", "1208454omqgEd", "tusiart.work", "query", "13788eMMrUA", "hostname",
        "qiandaoapp.com", "host", "yxt", "qdurl.net", "66286uhmjCN", "get", "charAt", "774808IqwOtl",
        "echo.tech", "VjY", "localhost", "hBd", "o.c", "333GGgnUa", "MjQ", "spl", "tId", "endsWith",
        "rep", "est", "protocol", "eUL", "tensor.art", "Dkw", "hX3", "qdurl.quest", "1313100GOPUTD",
        "TA2", "MzA", "qiandao.com", "nda", "str", "file", "development", "C_S", "key", "17078GKfvPD",
        "gRI", "I4Z", "//a", "charCodeAt", "ing", "sor", "zQ1", "que", "370290UxOKKn", "1372548ywGmcD",
        "fromCharCode", "ZaC", "25448wXoNQz", "27WGxnKz", "cke", "0123456789ABCDEF", "wM2", "2991489eqqUva",
        "DxB", "WM1", "50156qTOaYD", "2440JOeunC", "ueO", "qdurl.co", "fxZ", "1Y2", "shift", "equ",
        "qdurl9.cn", "qdurl.club", "hash", "ues", "Pro", "HA2", "0.0", "39vwSqXV", "NTB", "qia",
        "val", "exec", "5752kcCXul", "845967HwXojA", "UKA", "n/n", "1adApUv", "pat", "yNj",
        "0123456789abcdef", "min", "JlY", "qiandao.cn", "-Id", "ipr", "TY2", "olv", "35vFLWmX",
        "ogr", "test", "185VUDphb", "3NT", "url", "99952MUVqSX", "8SPPNvM", "qdurl.sh.cn", "Rww",
        "6716220oCuxbV", "forEach", "2119530oMEblD", "N2Y", "par"
    ]


# 全局可变数组，模拟 JS 里被旋转的数组
SL = sl()


# -----------------------------
# Mu / Au：Mu(t) = SL[t - 430]；Au = Mu
# 并用 IIFE 的方式旋转 SL 直到命中常量
# -----------------------------
def Mu(idx: int) -> str:
    return SL[idx - 430]


Au = Mu  # 在 JS 中 Au = Mu


def rotate_sl_until_ready():
    # JS:
    # if (323773 == parseInt(n(557))/1 * (-parseInt(n(446))/2) + ... ) break;
    # else r.push(r.shift())
    max_turns = 10000
    turns = 0
    while True:
        try:
            n = Mu
            val = (
                    parse_int_prefix(n(557)) / 1
                    * (-parse_int_prefix(n(446)) / 2)
                    + parse_int_prefix(n(530)) / 3
                    * (parse_int_prefix(n(515)) / 4)
                    + -parse_int_prefix(n(562)) / 5
                    + -parse_int_prefix(n(504)) / 6
                    + parse_int_prefix(n(433)) / 7
                    * (-parse_int_prefix(n(465)) / 8)
                    + -parse_int_prefix(n(484)) / 9
                    + parse_int_prefix(n(516)) / 10
                    * (parse_int_prefix(n(462)) / 11)
            )
            if int(val) == 323773:
                break
            else:
                # r.push(r.shift())
                SL.append(SL.pop(0))
        except Exception:
            SL.append(SL.pop(0))
        turns += 1
        if turns > max_turns:
            raise RuntimeError("rotate_sl_until_ready: exceeded max rotations")


# -----------------------------
# Qu / Xu：Qu() 数组（里头很多 Au(idx)），再旋转；Xu(t)=Qu()[t-214]
# -----------------------------
def build_Qu_array():
    t = Au
    return [
        t(506), t(538), t(497), t(565), t(512), t(439), t(574), "Q1M", t(546), "72y",
        "2718OSIhgT", "8eV", t(435), "get", t(488), "per", t(528), "HMA", t(431), t(503),
        t(555), t(513), t(522), t(539), t(549), t(547), "46407972pwxIzS", t(441), t(479),
        t(492), t(543), t(470), "Tim", t(438), t(445), t(527), t(507), t(434), t(495),
        t(529), "EKx", t(532), t(477), t(568), "abs", t(537), "4yfnKwb", t(452),
        "1304610XjtbUK", t(550), t(469), t(526), t(575), "X-R", "qsq", t(430), "UNH", t(460)
    ]


QU = []  # 将在运行时构建并旋转


def Zu(idx: int) -> str:
    return QU[idx - 214]


Xu = Zu  # const Xu = Zu;


def rotate_qu_until_ready():
    global QU
    QU = build_Qu_array()
    # IIFE: 584566 == -parseInt(r(238))/1 * (-parseInt(r(263))/2) + ...
    max_turns = 10000
    turns = 0
    while True:
        try:
            r = Zu
            val = (
                    -parse_int_prefix(r(238)) / 1
                    * (-parse_int_prefix(r(263)) / 2)
                    + parse_int_prefix(r(219)) / 3
                    * (parse_int_prefix(r(261)) / 4)
                    + parse_int_prefix(r(252)) / 5
                    + -parse_int_prefix(r(234)) / 6
                    * (parse_int_prefix(r(264)) / 7)
                    + -parse_int_prefix(r(251)) / 8
                    * (-parse_int_prefix(r(225)) / 9)
                    + -parse_int_prefix(r(248)) / 10
                    * (-parse_int_prefix(r(267)) / 11)
                    + -parse_int_prefix(r(241)) / 12
            )
            if int(val) == 584566:
                break
            else:
                # i.push(i.shift())
                QU.append(QU.pop(0))
        except Exception:
            QU.append(QU.pop(0))
        turns += 1
        if turns > max_turns:
            raise RuntimeError("rotate_qu_until_ready: exceeded max rotations")


# -----------------------------
# 还原 il / ol
# -----------------------------
def recover_skeys():
    # il = Xu(226) + Xu(269) + Xu(265) + Xu(255) + Xu(243) + Xu(222) + Xu(224) + Xu(258) + Xu(249) + Xu(220) + "x0"
    il = (
            Xu(226) + Xu(269) + Xu(265) + Xu(255) + Xu(243)
            + Xu(222) + Xu(224) + Xu(258) + Xu(249) + Xu(220) + "x0"
    )
    # ol = Au(482) + Xu(262) + Xu(215) + Xu(214) + "Lio" + Xu(253) + "O1N" + Xu(260) + Xu(236) + Xu(271) + "QL"
    ol = (
            Au(482) + Xu(262) + Xu(215) + Xu(214) + "Lio"
            + Xu(253) + "O1N" + Xu(260) + Xu(236) + Xu(271) + "QL"
    )
    return il, ol


# -----------------------------
# 签名：HMAC-SHA256 → hex小写 → Base64(对hex做Base64)
# -----------------------------
def hmac_sha256_hex_b64(key: str, msg: str) -> str:
    hex_str = hmac.new(key.encode("utf-8"), msg.encode("utf-8"), hashlib.sha256).hexdigest()
    return base64.b64encode(hex_str.encode("utf-8")).decode("utf-8")

def normalize_params(params: dict) -> str:
    # 1. 转换为键值对列表
    pairs = list(params.items())
    # 2. 仅按key排序（与第一段代码的key排序逻辑一致）
    pairs.sort(key=lambda kv: kv[0])  # 只按key排序，不拼接value
    # 3. 对key进行quote编码（safe=''），value保持原样
    encoded_pairs = [f"{quote(k, safe='')}={v}" for k, v in pairs]
    return "&".join(encoded_pairs)


# -----------------------------
# 【修改2】调整签名基础字符串拼接，移除?前缀
# -----------------------------
def build_sign_string(url: str, request_id: str, timestamp_ms: int, extra_query: dict = None) -> str:
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    # 解析原始查询参数
    q = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
    if extra_query:
        q.update(extra_query)
    # 处理查询参数（无?前缀）
    q_str = normalize_params(q) if q else ""
    # 拼接格式：path + 处理后的query（无?） + request_id + timestamp_ms
    return f"{path}{q_str}{request_id}{timestamp_ms}"


def sign_request(url: str, skey: str, request_id: str = "", timestamp_ms: int = None, extra_query: dict = None):
    if timestamp_ms is None:
        timestamp_ms = int(time.time() * 1000)
    sign_str = build_sign_string(url, request_id, timestamp_ms, extra_query)
    x_request_sign = hmac_sha256_hex_b64(skey, sign_str)
    headers = {
        "X-Request-Sign": x_request_sign,
        "X-Request-Timestamp": str(timestamp_ms),
        "X-Request-Package-Sign-Version": "0.0.2",  # 你贴的值
        "X-Request-Sign-Version": "v1",
        "X-Request-Sign-Type": "HMAC_SHA256"
    }
    if request_id:
        headers["X-Request-Id"] = request_id
    return headers, sign_str


# -----------------------------
# 入口：先旋转 sl / qu，然后复原 skey，再示例签名
# -----------------------------
if __name__ == "__main__":
    # 1) 归位 sl（对应 Au/Mu 的 IIFE）
    rotate_sl_until_ready()

    # 2) 构建并归位 Qu（对应 Xu/Qu 的 IIFE）
    rotate_qu_until_ready()

    # 3) 还原 skey
    il, ol = recover_skeys()
    print("[+] production skey (il):", il)
    print("[+] development skey (ol):", ol)

    # 4) 生成示例签名（按你给的接口）
    #url = "https://api.qiandao.cn/treasure/spus/feed"
    url = "https://api.qiandao.com/treasure/flora/v2/spu/simpleInfo"
    extra_query = {"entryId": "892031759611390293"}
    # 你的 curl 示例里没有 X-Request-Id，所以这里传 ""（空串）
    print(int(round(time.time() * 1000)))
    ts = int(round(time.time() * 1000))  # 也可以用当前时间：int(time.time()*1000)
    headers, sign_str = sign_request(url, skey=il, request_id="", timestamp_ms=ts, extra_query=extra_query)
    print("\n[+] sign base string:", sign_str)
    print("[+] headers:")
    for k, v in headers.items():
        print("   ", k + ":", v)
