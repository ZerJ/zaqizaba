import requests
import re
import os
import tempfile
from datetime import datetime
from collections import defaultdict
# from openpyxl import Workbook
# from openpyxl.drawing.image import Image as ExcelImage
from io import BytesIO
from PIL import Image as PILImage

# ========== 配置 ==========
API_URL = "http://127.0.0.1:5030/api/v1/chatlog?time=2025-01-01~2025-09-16&talker=wxid_s7pu90t6hu2v31"
EXCEL_FILE = "chatlog.xlsx"
FIRST_SENDER_STAT_FILE = "first_sender_stat.xlsx"
IMAGE_DIR = "images"
MAX_IMAGE_DIMENSION = 150
REQUEST_TIMEOUT = 10
ORIGIN_REQUEST_TIMEOUT = 15
DATE_FORMAT = "%m-%d"
FULL_DATE_FORMAT = "%Y-%m-%d"
BASE_YEAR = "2025"

# 确保存放原始图片的目录存在
os.makedirs(IMAGE_DIR, exist_ok=True)


def download_image(url, timeout=REQUEST_TIMEOUT):
    """下载图片并返回PIL Image对象"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return PILImage.open(BytesIO(response.content))
    except Exception as e:
        print(f"下载图片失败 {url}: {str(e)}")
        return None


def save_original_image(original_path):
    """保存原始图片到本地并返回原始图片URL"""
    try:
        origin_url = f"http://127.0.0.1:5030/file/{original_path}"
        filename = os.path.basename(original_path).replace(".dat", ".jpg")
        file_path = os.path.join(IMAGE_DIR, filename)

        if not os.path.exists(file_path):
            response = requests.get(origin_url, timeout=ORIGIN_REQUEST_TIMEOUT)
            response.raise_for_status()
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"保存原始图片: {file_path}")
        else:
            print(f"原始图片已存在: {file_path}")

        return origin_url
    except Exception as e:
        print(f"保存原始图片错误 {original_path}: {str(e)}")
        return None


def parse_chat_time(chat_time_str):
    """解析聊天记录中的时间字符串，返回完整日期和时间"""
    try:
        # 返回完整日期和时间对象，用于排序
        full_time_str = f"{BASE_YEAR}-{chat_time_str}"
        return datetime.strptime(full_time_str, f"{FULL_DATE_FORMAT} %H:%M:%S")
    except Exception as e:
        print(f"解析时间失败 {chat_time_str}: {str(e)}")
        return None


def get_first_senders(messages):
    """获取每天第一个发消息的人"""
    daily_messages = defaultdict(list)

    # 按日期分组所有消息
    for msg in messages:
        date_str = msg["datetime"].strftime(FULL_DATE_FORMAT)
        daily_messages[date_str].append(msg)

    # 找出每天第一个发消息的人
    first_senders = {}
    for date, msgs in daily_messages.items():
        # 按时间排序，取第一条消息的发送者
        sorted_msgs = sorted(msgs, key=lambda x: x["datetime"])
        first_sender = sorted_msgs[0]["sender"]
        first_senders[date] = {
            "sender": first_sender,
            "time": sorted_msgs[0]["datetime"].strftime(f"{FULL_DATE_FORMAT} %H:%M:%S")
        }

    return first_senders


def count_first_sender_occurrences(first_senders):
    """统计每个人成为首次发送者的次数"""
    counts = defaultdict(int)
    for data in first_senders.values():
        counts[data["sender"]] += 1
    return counts


def export_first_sender_stats(first_senders, counts):
    """导出首次发送者统计结果到Excel"""
    wb = "Workbook()"

    # 第一个工作表：每日首次发送者详情
    ws1 = wb.active
    ws1.title = "每日首次发送者"
    ws1.append(["日期", "首次发送者", "首次发送时间"])

    for date in sorted(first_senders.keys()):
        data = first_senders[date]
        ws1.append([date, data["sender"], data["time"]])

    # 调整列宽
    ws1.column_dimensions['A'].width = 15
    ws1.column_dimensions['B'].width = 20
    ws1.column_dimensions['C'].width = 20

    # 第二个工作表：首次发送者次数统计
    ws2 = wb.create_sheet(title="首次发送者次数统计")
    ws2.append(["发送者", "成为首次发送者的次数", "占比"])

    total_days = len(first_senders)
    for sender, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        percentage = f"{(count / total_days * 100):.2f}%" if total_days > 0 else "0%"
        ws2.append([sender, count, percentage])

    # 调整列宽
    ws2.column_dimensions['A'].width = 20
    ws2.column_dimensions['B'].width = 25
    ws2.column_dimensions['C'].width = 10

    wb.save(FIRST_SENDER_STAT_FILE)
    print(f"首次发送者统计已保存: {FIRST_SENDER_STAT_FILE}")


def print_first_sender_stats(first_senders, counts):
    """在控制台打印首次发送者统计结果"""
    print("\n" + "="*80)
    print("每日首次发送者统计结果")
    print("="*80)

    # 打印每日首次发送者
    print("\n【每日首次发送者详情】")
    print(f"{'日期':<15} {'首次发送者':<15} {'首次发送时间'}")
    print("-"*60)
    for date in sorted(first_senders.keys()):
        data = first_senders[date]
        print(f"{date:<15} {data['sender']:<15} {data['time']}")

    # 打印发送者统计
    print("\n【首次发送者次数统计】")
    print(f"{'发送者':<15} {'次数':<6} {'占比'}")
    print("-"*40)
    total_days = len(first_senders)
    for sender, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        percentage = f"{(count / total_days * 100):.2f}%" if total_days > 0 else "0%"
        print(f"{sender:<15} {count:<6} {percentage}")

    print("\n" + "="*80)


def main():
    # 请求聊天记录
    try:
        resp = requests.get(API_URL, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except Exception as e:
        print(f"请求聊天记录失败: {str(e)}")
        return

    chat_text = resp.text.strip().splitlines()
    if not chat_text:
        print("未获取到聊天记录")
        return

    # 初始化变量
    current_sender = None
    current_time_str = None
    message_list = []  # 用于统计首次发送者的消息列表

    # 创建主聊天记录Excel
    wb = "Workbook()"
    ws = wb.active
    ws.title = "ChatLog"
    ws.append(["时间", "发送者", "消息内容 / 图片", "图片URL"])
    ws.column_dimensions['A'].width = 18
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 50
    ws.column_dimensions['D'].width = 60

    # 使用临时文件处理图片
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        temp_img_path = temp_file.name

    try:
        # 逐行解析聊天记录
        for line in chat_text:
            line = line.strip()
            if not line:
                continue

            # 匹配“发送者 时间”
            time_sender_match = re.match(r"^(.*?)\s+(\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})$", line)
            if time_sender_match:
                current_sender = time_sender_match.group(1)
                current_time_str = time_sender_match.group(2)
                continue

            # 跳过无发送者/无时间的无效行
            if not current_sender or not current_time_str:
                print(f"跳过无效行: {line}")
                continue

            # 解析时间
            chat_datetime = parse_chat_time(current_time_str)
            if chat_datetime:
                # 添加到消息列表用于统计
                message_list.append({
                    "datetime": chat_datetime,
                    "sender": current_sender
                })

            # 处理图片消息
            if line.startswith("![图片]("):
                img_match = re.findall(r"!\[图片\]\((.+?)\)", line)
                if img_match:
                    img_fields = img_match[0].split(",")
                    if len(img_fields) >= 2:
                        thumb_url = img_fields[0]
                        original_path = img_fields[1]
                        origin_url = save_original_image(original_path)

                        pil_img = download_image(thumb_url)
                        if pil_img:
                            pil_img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION))
                            pil_img.save(temp_img_path)
                            ws.append([current_time_str, current_sender, "图片", origin_url or ""])
                            excel_img = "ExcelImage(temp_img_path)"
                            ws.row_dimensions[ws.max_row].height = MAX_IMAGE_DIMENSION * 0.75
                            ws.add_image(excel_img, f"C{ws.max_row}")
                        else:
                            ws.append([current_time_str, current_sender, "[缩略图下载失败]", origin_url or ""])
                    else:
                        ws.append([current_time_str, current_sender, "[图片格式错误]", ""])
            # 处理文本消息
            else:
                ws.append([current_time_str, current_sender, line, ""])

        # 保存主聊天记录Excel
        wb.save(EXCEL_FILE)
        print(f"主聊天记录Excel已保存: {EXCEL_FILE}")
        print(f"原始图片保存在: {IMAGE_DIR}")

        # 统计每天第一个发消息的人
        if message_list:
            first_senders = get_first_senders(message_list)
            sender_counts = count_first_sender_occurrences(first_senders)

            # 打印统计结果
            print_first_sender_stats(first_senders, sender_counts)

            # 导出统计结果到Excel
            export_first_sender_stats(first_senders, sender_counts)
        else:
            print("\n无有效消息数据，无法统计首次发送者")

    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
    finally:
        # 清理临时文件
        if os.path.exists(temp_img_path):
            try:
                os.remove(temp_img_path)
            except:
                print(f"清理临时文件失败: {temp_img_path}")


if __name__ == "__main__":
    txt={
        "text": "<comment>喵呜~这笔记好厉害呀，身份体系官方认证师听起来就很专业呢！</commnet>\n<comment>哇哦，我也想知道身份体系官方认证师都要做些什么呢？</commnet>\n<comment>嘿嘿，感觉成为身份体系官方认证师肯定很有趣吧，喵~</commnet>"
    }
    print(txt.get("text"))
    cleaned_text = re.sub(r'</?comment>', '', txt.get("text"))
    print(cleaned_text)
