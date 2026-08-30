#PGM-ID:GK1S0105
#PGM-NAME:GK養成計画進捗チェック
#最終更新日:2026/02/08

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_mail(info,to, cc, title, mail):
    """メール送信処理"""
    
    # 送信先のメールアドレ
    if not to:
        print("送信先アドレスが見つかりません。")
        return False
    
    # メール作成
    msg = MIMEMultipart()
    msg["From"] = info[0]
    msg["To"] = ", ".join(to)
    msg["Subject"] = title
    msg.attach(MIMEText(mail, "plain", "utf-8"))

    # GmailのSMTPサーバーを設定
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(info[0], info[1])
            server.sendmail(info[0], to, msg.as_string())
        print(f"メールを正常に送信しました。")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("認証エラー: メールアドレスまたはパスワードが間違っています。")
        return False
    except smtplib.SMTPRecipientsRefused:
        print("送信先アドレスが無効です。")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP エラー: {e}")
        return False
    except Exception as e:
        print(f"予期しないエラー: {e}")
        return False