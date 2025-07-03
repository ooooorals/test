from datetime import datetime

def parse_japanese_time(time_str: str) -> datetime:
   match = time_str.strip().replace('時', '')
   hour = int(match)
   return datetime.strptime(f"{hour}:00", "%H:%M")
