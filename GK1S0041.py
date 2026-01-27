#PGM-ID:GK1S0041
#PGM-NAME:GK自家用MSG送信
#最終更新日:2026/01/27

import requests

# Discord Webhook URL
WEBHOOK_URL = "https://discordapp.com/api/webhooks/1454837288344228035/9LvK3n6u9JWLBjpIZXG27WJzqiosq1zFxRmVPIkkPAVbuGEtazE6K7cPLedsv2E5Slwd"


def send_msg(msg_data, user_id):
    """Discord にメッセージを送信
    
    Args:
        msg_data: [区分, タイトル, 本文]
            区分: "1"=通知, "2"=注意, "3"=警告
        user_id: 送信者ID
    
    Returns:
        str: エラーメッセージ（成功時は空文字）
    """
    
    # 入力チェック
    if not msg_data[1]:
        return "タイトルを入力してください。"
    if not msg_data[2]:
        return "本文を入力してください。"
    
    # 区分に応じた色とプレフィックスを設定
    kbn = msg_data[0]
    if kbn == "1":
        color = 0x3498db  # 青色（通知）
        prefix = "【通知】"
    elif kbn == "2":
        color = 0xff0000  # 赤色（注意）
        prefix = "【注意】"
    elif kbn == "3":
        color = 0x800080  # 紫色（警告）
        prefix = "【警告】"
    else:
        color = 0x3498db
        prefix = ""
    
    # タイトルと本文
    title = prefix + msg_data[1]
    body = msg_data[2]
    
    # Discord送信
    try:
        payload = {
            "embeds": [{
                "title": title,
                "description": body,
                "color": color,
                "footer": {
                    "text": "※送信専用のため、返信禁止"
                }
            }]
        }
        response = requests.post(WEBHOOK_URL, json=payload)
        
        if response.status_code == 204:
            print(f"Discordへの送信が完了しました。送信者: {user_id}")
            return ""
        else:
            print(f"Discord送信エラー: {response.status_code}")
            return f"送信に失敗しました。(エラーコード: {response.status_code})"
            
    except Exception as e:
        print(f"予期しないエラー: {e}")
        return "送信中にエラーが発生しました。"