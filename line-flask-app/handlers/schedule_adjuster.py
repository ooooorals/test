from datetime import datetime, timedelta
import re

def parse_schedule_text(schedule_text):
    """
    Parses a schedule text like:
    6:00~6:30 朝ごはん
    6:30~7:30 勉強
    7:30~16:00 お出かけ
    into a list of dictionaries with start, end, and task.
    """
    schedule = []
    lines = schedule_text.strip().split('\n')
    for line in lines:
        match = re.match(r'(\d{1,2}:\d{2})~(\d{1,2}:\d{2})\s+(.+)', line.strip())
        if match:
            start_str, end_str, task = match.groups()
            start_time = datetime.strptime(start_str, "%H:%M")
            end_time = datetime.strptime(end_str, "%H:%M")
            schedule.append({
                "start": start_time,
                "end": end_time,
                "task": task
            })
    return schedule

def adjust_schedule(schedule, adjustment_text):
    """
    Adjusts the schedule based on an input like '勉強プラス10分'
    """
    match = re.match(r'(.+?)プラス(\d+)分', adjustment_text.strip())
    if not match:
        raise ValueError("調整形式が正しくありません。例：勉強プラス10分")
    
    target_task, extra_minutes = match.groups()
    extra_delta = timedelta(minutes=int(extra_minutes))

    adjusted_schedule = []
    shift = timedelta(0)
    task_found = False

    for item in schedule:
        start = item["start"] + shift
        end = item["end"] + shift
        task = item["task"]

        if not task_found and task == target_task:
            end += extra_delta
            shift += extra_delta
            task_found = True

        adjusted_schedule.append({
            "start": start,
            "end": end,
            "task": task
        })

    return adjusted_schedule

def format_schedule(schedule):
    """
    Formats the adjusted schedule back into text.
    """
    lines = []
    for item in schedule:
        start_str = item["start"].strftime("%H:%M")
        end_str = item["end"].strftime("%H:%M")
        lines.append(f"{start_str}~{end_str} {item['task']}")
    return "\n".join(lines)

# Example usage
if __name__ == "__main__":
    original_text = """6:00~6:30 朝ごはん
6:30~7:30 勉強
7:30~16:00 お出かけ"""
    adjustment = "勉強プラス10分"

    schedule = parse_schedule_text(original_text)
    adjusted = adjust_schedule(schedule, adjustment)
    result_text = format_schedule(adjusted)
    print(result_text)

