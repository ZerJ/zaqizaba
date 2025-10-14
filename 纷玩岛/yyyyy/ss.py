import hashlib
from  time import  time
def generate_md5_hash(data: str) -> str:
    return hashlib.md5(data.encode('utf-8')).hexdigest()

print(int(round(time() * 1000)))
# 输入字符串
input_str = "ce8b64d6c1a0a275d8822ad273315eb3&1741677566626&12574478&{\"itemId\":\"880693337037\",\"bizCode\":\"ali.china.damai\",\"scenario\":\"itemsku\",\"exParams\":\"{\\\"dataType\\\":4,\\\"dataId\\\":\\\"\\\",\\\"privilegeActId\\\":\\\"\\\"}\",\"platform\":\"8\",\"comboChannel\":\"2\",\"dmChannel\":\"damai@damaih5_h5\"}"
print(input_str)
# 计算 MD5 值
md5_result = generate_md5_hash(input_str)
print(md5_result)