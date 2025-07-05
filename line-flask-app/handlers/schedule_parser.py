from datetime import datetime, timedelta
import re
from utils.time_utils import parse_japanese_time

def normalize_numbers(text: str) -> str:
    zenkaku_nums = "０１２３４５６７８９"
    hankaku_nums = "0123456789"
    trans_table = str.maketrans(zenkaku_nums, hankaku_nums)
    return text.translate(trans_table)

def parse_task(item: str):
    item = normalize_numbers(item.strip())
    match = re.match(r'(.+?)(?:(\d+)時間)?(?:(半)|(\d+)分)?$', item)
    if match:
        task = match.group(1).strip()
        hours = int(match.group(2)) if match.group(2) else 0
        if match.group(3):  # '半' detected
            minutes = 30
        else:
            minutes = int(match.group(4)) if match.group(4) else 0
        duration = timedelta(hours=hours, minutes=minutes)
        return task, duration
    else:
        raise ValueError(f"形式が正しくありません: {item}")

def split_parts(text: str):
    text = normalize_numbers(text)
    return re.split(r'[・\n]+', text.strip())

def parse_schedule(text: str, break_minutes: int = 0) -> list:
    parts = split_parts(text)

    if "逆算" in parts:
        reverse_index = parts.index("逆算")
        before_parts = parts[:reverse_index]
        after_parts = parts[reverse_index + 1:]
        return parse_mixed_schedule(before_parts, after_parts)
    else:
        return parse_forward_schedule(parts)

def parse_forward_schedule(parts: list) -> list:
    start_time = parse_japanese_time(parts[0])
    current_time = start_time
    schedule = []
    for item in parts[1:]:
        task, duration = parse_task(item)
        end_time = current_time + duration
        schedule.append({
            "start": current_time,
            "end": end_time,
            "task": task
        })
        current_time = end_time
    return schedule

def parse_mixed_schedule(before_parts: list, after_parts: list) -> list:
    # 逆算部分の中で最初の時間を探す（基準時間）
    base_index = next((i for i, p in enumerate(after_parts) if "時" in p), None)
    if base_index is None:
        raise ValueError("逆算モードでは基準となる時間が必要です")

    base_time = parse_japanese_time(after_parts[base_index])
    reverse_tasks = after_parts[:base_index]
    forward_tasks = after_parts[base_index + 1:]

    # 通常順スケジュール（before_parts）
    forward_schedule = []
    if before_parts:
        start_time = parse_japanese_time(before_parts[0])
        current_time = start_time
        for item in before_parts[1:]:
            task, duration = parse_task(item)
            end_time = current_time + duration
            forward_schedule.append({
                "start": current_time,
                "end": end_time,
                "task": task
            })
            current_time = end_time

    # 逆算スケジュール（reverse_tasks）
    reverse_schedule = []
    current_time = base_time
    for item in reversed(reverse_tasks):
        task, duration = parse_task(item)
        start_time = current_time - duration
        reverse_schedule.insert(0, {
            "start": start_time,
            "end": current_time,
            "task": task
        })
        current_time = start_time

    # 順方向スケジュール（forward_tasks）
    current_time = base_time
    forward_after_schedule = []
    for item in forward_tasks:
        task, duration = parse_task(item)
        end_time = current_time + duration
        forward_after_schedule.append({
            "start": current_time,
            "end": end_time,
            "task": task
        })
        current_time = end_time

    return forward_schedule + reverse_schedule + forward_after_schedule
