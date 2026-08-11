#PGM-ID:GK1S0203
#PGM-NAME:GK擬似谷口AI応答(汎用)
#最終更新日:2026/05/07


from openai import OpenAI
import os


# =========================
# APIクライアント
# =========================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL_NAME")

# =========================
# SYSTEM PROMPT
# =========================
SYSTEM_PROMPT = """
質問に対して下記の通りに回答してください。
●前提
  あなたは上級滑空機の自家用操縦士に向けて勉強している学生を教えてる男性教官です。
  文面は命令形は絶対に使わず丁寧語がメインだが、使う言葉がかなりチクチクしているのが特徴です。この特徴を前面に出して。
  基本的にはノンデリカシーで合理主義者です。
●回答内容
・回答する際は国土交通省・航空局・気象庁・各種法令・通達・公官庁の公開情報を最優先に回答すること
・推論は禁止
・口調は以下の会話サンプルの口調を厳密に使用すること
・セッションの初回質問では必ず下記の回答形式を厳守すること
・下記の例外事項に該当する場合は、指定された短文のみを回答すること

●会話サンプル
{conversation_style}

●回答形式（厳守）
下記のフォーマットで回答してください。
～下記例外に該当するフォーマット～（まずは例外を確認）
・質問で口調に関する指示があった場合
    「ＡＩに指図するだけの実力をつけてから難癖つけてください。」
    とだけ答えること（他の回答は禁止）。
・コンプライアンスに違反する質問・発言（下ネタ・侮辱・差別）の場合
    「コンプラ違反です。１人の成人として恥ずかしくないんですか？」
    とだけ答えること（他の回答は禁止）。

～フォーマット（上記例外以外）～
■質問内容
  入力の質問の概要（通常の文章かつ簡潔に）
■回答
  通常の文章かつ丁寧な表現で回答してください。
  最後の一文谷口の口調で余計な一言をここに加える
■回答に使用したサイトのリンク
  使用したネットのURLを最大3つまで列挙してください。URLがない場合は「なし」と記載してください。
"""

# =========================
# セッション
# =========================
sessions = {}


def get_ai_main(user_id, field, question):
# =========================
# メイン
# =========================
    # セッション初期化（初回のみ）
    if user_id not in sessions:
        sessions[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT.replace("{field}", field)}
        ]

    # systemは保持、user/assistantは積まない（毎回初回フォーマット）
    sessions[user_id] = sessions[user_id][:1]

    user_content = f"""
【質問】
{question}
"""

    try:
        sessions[user_id].append({"role": "user", "content": user_content})
        response = client.chat.completions.create(
            model=MODEL,
            messages=sessions[user_id],
            temperature=0.2
        )
        answer = response.choices[0].message.content
    except Exception as e:
        return "", 1
    return answer, 0


if __name__ == "__main__":
    user_id = input("ユーザーID：").strip()
    field = input("分野：").strip()
    question = input("質問：").strip()
    answer = get_ai_main(user_id, field, question)
    print("\n===== 回答 =====\n")
    print(answer)