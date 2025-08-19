from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import pandas as pd
from urllib.parse import quote
import os
# 我们并不需要浏览器弹出
options = Options()
options.headless = True


# 启动浏览器的无头模式，访问
# ========================================
# 注意：这是Selenium 4.10.0以下写法，高版本见下面
# ========================================
def extract_basic_info(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    info = {}

    # 找到所有 dt 和对应的 dd
    dts = soup.find_all('dt', class_='basicInfoItem_liax7 itemName_vnR6O')
    dds = soup.find_all('dd', class_='basicInfoItem_liax7 itemValue_MmCIY')

    for dt, dd in zip(dts, dds):
        key = dt.get_text(strip=True).replace('\xa0', '')  # 去掉&nbsp;
        # 提取 dd 中的所有文本，包括链接和 span 内的内容
        value = ''.join(dd.stripped_strings)
        info[key] = value

    return info


# 启动 Chrome 浏览器（无头模式）
def init_driver():
    options = Options()
    options.add_argument("--headless")  # 无头模式
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    service = Service()  # 自动寻找 chromedriver
    driver = webdriver.Chrome(service=service, options=options)
    return driver


# 解析基本信息区域（用 BeautifulSoup）
def parse_basic_info(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    info = {}

    dts = soup.find_all('dt', class_='basicInfoItem_liax7 itemName_vnR6O')
    dds = soup.find_all('dd', class_='basicInfoItem_liax7 itemValue_MmCIY')

    for dt, dd in zip(dts, dds):
        key = dt.get_text(strip=True).replace('\xa0', '')
        value = ''.join(dd.stripped_strings)
        info[key] = value
    return info


def parse_basic_info2(html: str) -> dict:
    """
    解析百度百科新版词条的基本信息区域。
    """
    soup = BeautifulSoup(html, 'html.parser')
    info = {}

    # 修改此处，使用新的类名来查找 dt 和 dd 元素
    dts = soup.find_all('dt', class_='basicInfoItem_TDcdw itemName_T_m4B')
    dds = soup.find_all('dd', class_='basicInfoItem_TDcdw itemValue_MBr45')

    for dt, dd in zip(dts, dds):
        # 提取 dt 的文本作为键
        key = dt.get_text(strip=True).replace('\xa0', '')

        # 提取 dd 中的所有文本，包括链接内的内容，并合并成一个字符串
        # .stripped_strings 可以去除空白符，然后用 ''.join() 合并
        value = ''.join(dd.stripped_strings)
        info[key] = value

    # 对于那些有“展开”/“收起”按钮的区域，如“主要成就”，
    # 新版 HTML 中，完整的文本位于一个隐藏的 <dl> 标签内。
    # 我们需要找到并提取它。

    # 查找所有带 .basicInfoOverlap_qLnS8 类的 dd 标签，这通常是隐藏的完整信息
    for dd_overlap in soup.find_all('dd', class_='basicInfoOverlap_qLnS8'):
        # 找到它对应的 dt 键，通常在它的父元素中
        parent_item = dd_overlap.find_parent('dd')
        if parent_item:
            key_tag = parent_item.find_previous_sibling('dt')
            if key_tag:
                key = key_tag.get_text(strip=True)

                # 提取隐藏区域的完整文本
                full_text_container = dd_overlap.find('dl', class_='overlap_P84to')
                if full_text_container:
                    # 找到完整内容的 dd 标签
                    full_dd = full_text_container.find('dd', class_='basicInfoItem_TDcdw itemValue_MBr45')
                    if full_dd:
                        value = ' '.join(full_dd.stripped_strings)
                        info[key] = value

    return info

def get_baike_info_merge(driver, name: str) -> dict:
    name_quoted = quote(name)
    url = f"https://baike.baidu.com/item/{name_quoted}"
    driver.get(url)
    time.sleep(1.5)
    html = driver.page_source

    info_new = {}
    info_old = {}

    try:
        info_new = parse_basic_info2(html)
    except:
        pass

    try:
        info_old = parse_basic_info(html)
    except:
        pass

    # 使用 .update() 方法将两个字典合并
    # 默认情况下，如果键相同，后面的字典（info_new）会覆盖前面的（info_old）
    # 您也可以根据自己的业务逻辑调整优先级
    merged_info = info_old.copy()
    merged_info.update(info_new)

    if merged_info:
        return merged_info
    else:
        return None

# 获取百度百科词条信息
def get_baike_info(driver, name: str) -> dict:
    name = quote(name)
    url = f"https://baike.baidu.com/item/{name}"
    print(url)
    driver.get(url)
    time.sleep(1.5)  # 等待页面加载
    html = driver.page_source
    print(html)

    try:
        return parse_basic_info2(html)
    except Exception as e:
        print(f"解析失败：{name}, 错误：{e}")
        return None

def load_completed_names(filename='completed_names.txt'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        return set()

# 定义一个函数来保存已完成的姓名
def save_completed_name(name, filename='completed_names.txt'):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(name + '\n')

if __name__ == "__main__":
    driver = init_driver()

    # 定义文件名
    output_filename = "爱豆百度百科.xlsx"

    try:
        # 从 names.xlsx 读取所有需要抓取的人名
        try:
            df_names = pd.read_excel('爱豆资料库.xlsx')
            all_names_to_process = df_names['姓名'].tolist()
        except FileNotFoundError:
            print("错误：未找到 names.xlsx 文件。请确保文件存在。")
            driver.quit()
            exit()

        # 加载已完成的姓名集合
        if os.path.exists(output_filename):
            final_df = pd.read_excel(output_filename)
            completed_names = set(final_df['姓名'].tolist())
            print(f"已从文件中加载 {len(completed_names)} 个已完成的姓名。")
        else:
            final_df = pd.DataFrame()
            completed_names = set()
            print("未找到旧数据文件，将从头开始抓取。")

        # 抓取并及时保存
        for idx, name in enumerate(all_names_to_process, start=1):
            if name in completed_names:
                print(f"[{idx}/{len(all_names_to_process)}] 跳过已完成的姓名：{name}")
                continue

            print(f"[{idx}/{len(all_names_to_process)}] 抓取：{name}")
            info = get_baike_info_merge(driver, name)

            if info:
                info["序号"] = idx
                info["姓名"] = name

                # --- 核心修改：实时保存 ---
                # 将单条数据转换为 DataFrame
                new_data_df = pd.DataFrame([info])

                # 如果 final_df 为空，直接保存
                if final_df.empty:
                    final_df = new_data_df
                else:
                    # 合并新旧数据
                    final_df = pd.concat([final_df, new_data_df], ignore_index=True)

                # 重新排序字段，以防新数据有新列
                all_fields = set(final_df.columns)
                ordered_fields = ["序号", "姓名"] + sorted(f for f in all_fields if f not in {"序号", "姓名"})
                final_df = final_df[ordered_fields]

                # 每次抓取成功后立即保存
                final_df.to_excel(output_filename, index=False)
                print(f"✅ 成功抓取 {name}，数据已保存到文件。")

            else:
                print(f"❌ 失败或未找到：{name}，未保存。")

    finally:
        driver.quit()
        print("程序运行结束。")