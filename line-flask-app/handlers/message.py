# -*- coding: utf-8 -*-

from linebot import LineBotApi
from reply_builder import build_schedule_message  # Flex Messageを構築する関数をインポート

# トークンとユーザーID
MSG_TOKEN = 'IP8ouEpLxtf95tc+xOoFSnFf3B8tK7f3dkPIlcpcHI3WDUYaHIMQQhrBfiw7NDCtTOIqQv3yd9aAt0j15PH/dsmSBRSyuVUWRyK2xQ1RUfhxQMsXIa3HESCqa/3wT+0Q0bPSNFJa9ZZGfewVnc6Y3QdB04t89/1O/w1cDnyilFU='
USER_ID = 'Uf053a30508fc0340f3c4ce4d9c8ad484'

# LINE Bot APIの初期化
line_bot_api = LineBotApi(MSG_TOKEN)

# 仮の予定データ（本来はユーザー入力などから生成）
schedule = [
    {"time": "9:00", "task": "起床"},
    {"time": "10:00", "task": "朝食"},
    {"time": "11:00", "task": "勉強"}
]

# Flex Messageを構築
flex_message = build_schedule_message(schedule)

# メッセージを送信
line_bot_api.push_message(USER_ID, flex_message)
print('Flex Message送信完了')
