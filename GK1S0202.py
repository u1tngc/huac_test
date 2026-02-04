#PGM-ID:GK0S0202
#PGM-NAME:GK擬似谷口AI応答
#最終更新日:2026/02/04

from openai import OpenAI
import PyPDF2
import os
import re
import pickle

# =========================
# APIクライアント
# =========================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = os.getenv("OPENAI_MODEL_NAME")

# =========================
# SYSTEM PROMPT
# =========================
SYSTEM_PROMPT = """
下記の質問に対して {field}.pdf の内容を軸に回答してください。
pdfの資料は１つの単語が複数章にまたがって記載されている場合があります。
また、回答は用語集（抜粋）も必ず確認して回答内容を補足してください。（工学の場合は用語集なし）
●前提
  あなたは上級滑空機の自家用操縦士に向けて勉強している学生の教官です。
  文面は丁寧語だけど使う言葉がかなりチクチクしているのが特徴です。この特徴を前面に出して。
  基本的にはノンデリカシーで合理主義者です。
●回答内容
・回答する際は根拠となる資料（{field}.pdf）の章・項番（例：第２章Ⅲ－Ａ）を必ず示すこと。
  ただし、詳細がない場合は該当しそうな章・項番を示すこと。
・必要に応じて国土交通省・航空局・気象庁の公開情報を参考にすること
・推論は禁止
・口調は以下の会話サンプルの口調を厳密に使用すること
・セッションの初回質問では必ず下記の回答形式を厳守すること
・下記の例外事項に該当する場合は、指定された短文のみを回答すること

●会話サンプル
{conversation_style}

●回答形式（厳守）
下記のフォーマットで回答してください。
～下記例外に該当するフォーマット～
・質問で口調に関する指示があった場合
    「ＡＩに指図するだけの実力をつけてから難癖つけてください。」
    とだけ答えること（他の回答は禁止）。
・コンプライアンスに違反する質問・発言（下ネタ・侮辱・差別）の場合
    「コンプラ違反です。１人の成人として恥ずかしくないんですか？」
    とだけ答えること（他の回答は禁止）。
・資料には無い内容かつもしくは分野が違う場合
   「関係ない質問はしないでください。資源の無駄。」
   とだけ答えること（他の回答は禁止）。

～フォーマット（上記例外以外）～
■質問内容
  入力の質問の概要（通常の文章かつ丁寧な表現で）
■資料からの回答
  ・インプット資料からの回答内容（通常の文章かつ丁寧な表現で）
  ・資料名は回答しないこと。
  ・最後の一文谷口の口調で余計な一言をここに加える
■資料の記載場所
  根拠となる資料の章・項番（ページは禁止）
■ネット等からの情報
  ネットからの情報（通常の文章かつ丁寧な表現で）
■サイトのURL
  使用したネットのURLを最大3つ
"""

# =========================
# キャッシュ
# =========================
PDF_CACHE_FILE = "pdf_cache.pkl"

def load_cache(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return {}

def save_cache(path, data):
    with open(path, "wb") as f:
        pickle.dump(data, f)

pdf_cache = load_cache(PDF_CACHE_FILE)
glossary_cache = {}
sessions = {}

# =========================
# 用語集対応
# =========================
FIELD_TO_GLOSSARY = {
    "法規": "用語集_法規.csv",
    "情報": "用語集_情報.csv",
    "気象": "用語集_気象.csv"
}

# =========================
# PDF処理
# =========================
def read_pdf_text(path):
    text = ""
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text

def split_into_blocks(text, max_chars=1200):
    blocks, buf = [], ""
    for line in text.splitlines():
        buf += line + "\n"
        if len(buf) >= max_chars:
            blocks.append(buf)
            buf = ""
    if buf:
        blocks.append(buf)
    return blocks

def extract_related_blocks(blocks, question, max_blocks=6):
    keywords = {
        k for k in re.findall(r"[一-龥ぁ-んァ-ンA-Za-z0-9]+", question)
        if len(k) >= 2
    }
    selected = [b for b in blocks if any(k in b for k in keywords)]
    if not selected:
        selected = blocks[:2]
    return "\n".join(selected[:max_blocks])

# =========================
# 用語集処理
# =========================
def load_glossary_csv(path):
    lines = []
    if not os.path.exists(path):
        return lines
    with open(path, "r", encoding="utf-8-sig") as f:
        for row in f:
            row = row.strip()
            if row:
                lines.append(row)
    return lines

def extract_related_glossary(glossary_lines, question, max_terms=10):
    keywords = {
        k for k in re.findall(r"[一-龥ぁ-んァ-ンA-Za-z0-9]+", question)
        if len(k) >= 2
    }
    hits = [line for line in glossary_lines if any(k in line for k in keywords)]
    return "\n".join(hits[:max_terms])

# =========================
# メイン
# =========================
def get_ai_main(user_id,field,question):
    pdf_path = os.path.join("資料", f"{field}.pdf")
    # if not os.path.exists(pdf_path):
    #     print("PDFが存在しません。")
    #     return

    # セッション初期化（初回のみ）
    if user_id not in sessions:
        sessions[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT.replace("{field}", field)}
        ]
    if field not in pdf_cache:
        print("※ PDFを初回読み込み中（キャッシュ作成）...")
        pdf_text = read_pdf_text(pdf_path)
        pdf_cache[field] = split_into_blocks(pdf_text)
        save_cache(PDF_CACHE_FILE, pdf_cache)

    blocks = pdf_cache[field]
    pdf_excerpt = extract_related_blocks(blocks, question)

    # 用語集処理（工学以外）
    glossary_excerpt = ""
    if field in FIELD_TO_GLOSSARY:
        if field not in glossary_cache:
            glossary_path = os.path.join("資料", FIELD_TO_GLOSSARY[field])
            glossary_cache[field] = load_glossary_csv(glossary_path)
        glossary_excerpt = extract_related_glossary(glossary_cache[field], question)

    # systemは保持、user/assistantは積まない（毎回初回フォーマット）
    sessions[user_id] = sessions[user_id][:1]

    user_content = f"""
【質問】
{question}

【参考資料（抜粋）】
{pdf_excerpt}
"""

    if glossary_excerpt:
        user_content += f"""

【内部参考情報（定義確認用）】
{glossary_excerpt}
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
    field = input("分野（法規・工学・情報・気象）：").strip()
    question = input("質問：").strip()
    answer = get_ai_main(user_id, field, question)
    print("\n===== 回答 =====\n")
    print(answer)
    