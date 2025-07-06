
from datetime import datetime, timedelta
import re

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

def parse_japanese_time(time_str: str) -> datetime:
    time_str = normalize_numbers(time_str.strip())
    match = re.match(r'^(\d{1,2})時(?:(\d{1,2})分)?(半)?$', time_str)
    if match:
        hour = int(match.group(1))
        minute = 0
        if match.group(2):
            minute = int(match.group(2))
        elif match.group(3):  # '半'
            minute = 30
        return datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M")
    else:
        raise ValueError(f"時間の形式が正しくありません: {time_str}")

def split_parts(text: str):
    text = normalize_numbers(text)
    parts = re.split(r'[・\n]+', text.strip())
    return [p for p in parts if p.strip()]  # Remove empty strings

def parse_schedule(text: str, break_minutes: int = 0) -> list:
    parts = split_parts(text)

    # Split into blocks by "逆算"
    blocks = []
    current_block = []
    current_mode = "forward"

    for part in parts:
        if part == "逆算":
            if current_block:
                blocks.append((current_mode, current_block))
            current_block = []
            current_mode = "reverse"
        else:
            current_block.append(part)

    if current_block:
        blocks.append((current_mode, current_block))

    schedule = []
    for mode, block in blocks:
        try:
            if mode == "forward":
                schedule += parse_forward_schedule(block)
            elif mode == "reverse":
                schedule += parse_reverse_schedule(block)
        except Exception as e:
            raise ValueError(f"形式が正しくありません（{mode}ブロック）: {e}")

    return schedule

def parse_forward_schedule(parts: list) -> list:
    if not parts:
        return []
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

def parse_reverse_schedule(parts: list) -> list:
    # Match only valid time formats like "9時", "9時30分", "9時半"
    base_index = next((i for i, p in enumerate(parts) if re.match(r'^\d{1,2}時((\d{1,2}分)?|半)?$', p.strip())), None)
    if base_index is None:
        raise ValueError("逆算モードでは基準となる時間が必要です")

    base_time = parse_japanese_time(parts[base_index])
    reverse_tasks = parts[:base_index]
    forward_tasks = parts[base_index + 1:]

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

    forward_schedule = []
    current_time = base_time
    for item in forward_tasks:
        task, duration = parse_task(item)
        end_time = current_time + duration
        forward_schedule.append({
            "start": current_time,
            "end": end_time,
            "task": task
        })
        current_time = end_time

    return reverse_schedule + forward_schedule
