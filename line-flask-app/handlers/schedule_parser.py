from datetime import datetime, timedelta
import re
from utils.time_utils import parse_japanese_time

def normalize_numbers(text: str) -> str:
    zenkaku_nums = "０１２３４５６７８９"
    hankaku_nums = "0123456789"
    trans_table = str.maketrans(zenkaku_nums, hankaku_nums)
    return text.translate(trans_table)

def parse_task(item: str):
    match = re.match(r'(.+?)(?:(\d+)時間)?(?:(\d+)分)?$', item.strip())
    if match:
        task = match.group(1).strip()
        hours = int(match.group(2)) if match.group(2) else 0
        minutes = int(match.group(3)) if match.group(3) else 0
        duration = timedelta(hours=hours, minutes=minutes)
        return task, duration
    else:
        raise ValueError(f"形式が正しくありません: {item}")

def parse_schedule(text: str, break_minutes: int = 0) -> list:
    text = normalize_numbers(text)
    parts = text.split('・')

    if "つなげる" in parts:
        connect_index = parts.index("つなげる")
        normal_parts = parts[:connect_index]
        post_connect_parts = parts[connect_index + 1:]

        # 固定時間とそのタスクを探す
        fixed_time = None
        fixed_task = None
        fixed_duration = timedelta()
        reverse_parts = []
        forward_parts = []

        for i, part in enumerate(post_connect_parts):
            if "時" in part and re.match(r'\d+時', part.strip()):
                fixed_time = parse_japanese_time(part)
                if i + 1 < len(post_connect_parts):
                    fixed_task, fixed_duration = parse_task(post_connect_parts[i + 1])
                    forward_parts = post_connect_parts[i + 2:]
                else:
                    fixed_task = part.strip()
                    forward_parts = post_connect_parts[i + 1:]
                reverse_parts = post_connect_parts[:i]
                break

        # 逆算スケジュール
        reverse_schedule = []
        current_time = fixed_time
        for item in reversed(reverse_parts):
            task, duration = parse_task(item)
            start_time = current_time - duration
            reverse_schedule.insert(0, {
                "time": f"{start_time.strftime('%H:%M')}~{current_time.strftime('%H:%M')}",
                "task": task
            })
            current_time = start_time

        # 固定予定
        fixed_schedule = []
        if fixed_task:
            end_time = fixed_time + fixed_duration
            fixed_schedule.append({
                "time": f"{fixed_time.strftime('%H:%M')}~{end_time.strftime('%H:%M')}",
                "task": fixed_task
            })
            current_time = end_time
        else:
            current_time = fixed_time

        # 通常スケジュール（固定時間以降）
        forward_schedule = []
        for item in forward_parts:
            task, duration = parse_task(item)
            end_time = current_time + duration
            forward_schedule.append({
                "time": f"{current_time.strftime('%H:%M')}~{end_time.strftime('%H:%M')}",
                "task": task
            })
            current_time = end_time

        # 通常スケジュール（開始時間から）
        start_time = parse_japanese_time(normal_parts[0])
        current_time = start_time
        normal_schedule = []
        for item in normal_parts[1:]:
            task, duration = parse_task(item)
            end_time = current_time + duration
            normal_schedule.append({
                "time": f"{current_time.strftime('%H:%M')}~{end_time.strftime('%H:%M')}",
                "task": task
            })
            current_time = end_time

        return normal_schedule + reverse_schedule + fixed_schedule + forward_schedule

    else:
        # 通常モードのみ
        start_time = parse_japanese_time(parts[0])
        current_time = start_time
        schedule = []
        for item in parts[1:]:
            task, duration = parse_task(item)
            end_time = current_time + duration
            schedule.append({
                "time": f"{current_time.strftime('%H:%M')}~{end_time.strftime('%H:%M')}",
                "task": task
            })
            current_time = end_time
        return schedule
