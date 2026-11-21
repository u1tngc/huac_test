#PGM-ID:WX0S0220
#PGM-NAME:[P]WX METAR/TAF 詳細PDF 共通部品
#最終更新日:2026/11/21
"""
METAR（WX0S0221）・TAF（WX0S0222）の詳細PDFで共通に使う部品。

    ・色・寸法・フォント・文字スタイル
    ・解読結果（日本語・原文・判定）の分解と、表の行へのまとめ（build_rows）
    ・原文の群と表の行の対応付け（match_tokens：未解読の検出・原文の色付け）
    ・見出し（Header）・原文（RawText）・判定ピル（Pill）・フッターとページ番号（NumberedCanvas）
    ・prepare（入力→描画用データ）と build_pdf（PDF出力）

フォント（GenShinGothic-Monospace）は次の順に探す（気象ツール・学科班ツールの両方で同じファイルを使うため）。
    1. 出力先フォルダ/fonts      2. このPGMと同じ場所の fonts
    3. このPGMと同じ場所の static/fonts      4. 実行フォルダの static/fonts

判定の色・文字やフォントを変えるときはこのファイルだけを直す。
"""

import os
import re
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import (Flowable, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

# ------------------------------------------------------------
# 判定の扱い（WX0S0204 の結果を P3 用に読み替える）
# ------------------------------------------------------------
WX_AS_CAUTION = True     # 天気（降水・もや等）は赤ではなく橙にする
FEW_SCT_NO_FLAG = True   # FEW・SCT の雲層（CB/TCU を除く）は判定しない（シーリングにならないため）

# ------------------------------------------------------------
# 色・寸法（pt）
# ------------------------------------------------------------
NAVY = HexColor('#1F3A5F')
INK = HexColor('#1A1D21')
MUTED = HexColor('#5B6470')
SUBTLE = HexColor('#4A5561')
RULE = HexColor('#D0D5DB')
LIGHT_RULE = HexColor('#E3E7EB')
PANEL = HexColor('#F4F6F8')
HEAD_CHIP = HexColor('#E9EDF1')
UNK_ROW = HexColor('#F7F8F9')
WHITE = HexColor('#FFFFFF')
LEVEL_COLOR = {
    'red': (HexColor('#FBE9E7'), HexColor('#A61B1B'), HexColor('#E7B4AD')),
    'org': (HexColor('#FDF0E0'), HexColor('#8A4200'), HexColor('#EBC79A')),
    'unk': (WHITE, SUBTLE, HexColor('#7A848F')),
    '': (WHITE, INK, HexColor('#C7D0D9')),
}
RAW_TEXT_COLOR = {'red': HexColor('#C41E1E'), 'org': HexColor('#B85600')}   # 原文の文字色（赤・橙）
LEVEL_LABEL = {'red': '要注意', 'org': '注意', 'unk': '未解読', '': ''}

PAGE_W, PAGE_H = portrait(A4)
MARGIN_X = 36
MARGIN_TOP = 30
MARGIN_BOTTOM = 40
CONTENT_W = PAGE_W - MARGIN_X * 2
COL_W = [112, 69, CONTENT_W - 112 - 69 - 42, 42]   # 群｜項目｜解読｜判定

FONT = 'WX0S0220R'
FONT_B = 'WX0S0220B'

# 見出しに回す群（表には出さない）
HEADER_LABELS = ('通報種類', '地点略号', '観測日時', '通報日時', '通報区分')
SECTION_NAMES = {
    '国内記事': '国内記事（RMK）',
    '傾向型着陸予報(TREND)': '傾向型着陸予報（TREND・2時間以内）',
    'PIREP(操縦士報告)等': '操縦士報告（PIREP）等',
    'ＴＡＦ': '基本予報',
}
LABEL_RENAME = {
    '風向・風速': '風',
    '風向・風速・ガスト': '風',
    '気温・露点温度': '気温 / 露点',
    '気温・露点': '気温 / 露点',
    'QNH気圧': 'QNH',
    'ＱＮＨ気圧': 'QNH',
    '滑走路視距離': '滑走路視距離',
    '気象現象補足': '天気の経過',
}


# ============================================================
# 入力の分解
# ============================================================
def split_raw(jpn, eng, warn):
    """先頭の原文行（最初の空行まで）と、それ以降の解読行に分ける。"""
    raw = []
    ix = 0
    while ix < len(jpn) and jpn[ix] != '':
        raw.append(jpn[ix])
        ix += 1
    body = []
    for j in range(ix, len(jpn)):
        w = warn[j] if j < len(warn) else 0
        e = eng[j] if j < len(eng) else ''
        body.append((jpn[j], e if e else '', w))
    return raw, body


def level_of(ws):
    if 1 in ws:
        return 'red'
    if 2 in ws:
        return 'org'
    return ''


def _norm_label(label):
    label = label.replace('　', '').replace(' ', '')
    label = re.sub(r'^(雲情報|天気|気象現象)(\d+)$', lambda m: ('雲' if m.group(1) == '雲情報' else m.group(1)) + ' ' + m.group(2), label)
    return label


def _split_line(text):
    t = text.strip().replace('$', '')
    if '：' in t:
        label, value = t.split('：', 1)
        return _norm_label(label), value.strip()
    return '', t


def build_rows(body, metartaf):
    """解読行を表の行にまとめる。戻り値：見出し情報, 行のリスト"""
    header = {}
    items = []          # ('section', title) / ('row', dict)
    first_section = '本文' if metartaf == 1 else '基本予報'
    items.append(('section', first_section))
    ix = 0
    n = len(body)
    while ix < n:
        text, eng, w = body[ix]
        st = text.strip()
        if st == '':
            ix += 1
            continue
        # 区切り（～国内記事～ 等）
        if st.startswith('～') and st.endswith('～'):
            name = st.strip('～').strip()
            m = re.match(r'変化群(\d+)', name)
            if m:
                desc = ''
                if ix + 1 < n and '：' not in body[ix + 1][0] and body[ix + 1][0].strip():
                    desc = body[ix + 1][0].strip()
                    kw = body[ix + 1][1]
                    ix += 1
                    name = f'変化群{m.group(1)}（{kw}）　{desc}' if kw else f'変化群{m.group(1)}　{desc}'
            else:
                name = SECTION_NAMES.get(name, name)
            if items and items[-1][0] == 'section':
                items[-1] = ('section', name)
            else:
                items.append(('section', name))
            ix += 1
            continue
        # ＜…＞ のまとまり
        if st.startswith('＜'):
            label = re.sub(r'\d+$', '', st.strip('＜＞'))
            subs = []
            engs = [eng] if eng else []
            ws = [w]
            ix += 1
            while ix < n:
                t2, e2, w2 = body[ix]
                if t2.strip() == '' or not t2.startswith(' ') or t2.strip().startswith('＜'):
                    break
                subs.append(_split_line(t2))
                if e2:
                    engs.append(e2)
                ws.append(w2)
                ix += 1
            items.append(('row', {'kind': 'block', 'label': _norm_label(label), 'subs': subs,
                                  'engs': _uniq(engs), 'ws': ws}))
            continue
        # 通常の「項目：値」
        label, value = _split_line(text)
        if label in HEADER_LABELS and items[-1][1] == first_section:
            if label == '通報種類':
                header['kind'] = value.split('(')[0]
            elif label == '地点略号':
                header['station'] = value
            elif label in ('観測日時', '通報日時'):
                header['time'] = value.replace('(JST)', ' JST')
            elif label == '通報区分':
                header['class'] = value.split('（')[0]
            ix += 1
            continue
        prev = items[-1]
        if (prev[0] == 'row' and prev[1]['kind'] == 'line' and eng and prev[1]['engs'] == [eng]
                and label != prev[1]['labels'][-1]):
            prev[1]['labels'].append(label)
            prev[1]['values'].append(value)
            prev[1]['ws'].append(w)
        else:
            items.append(('row', {'kind': 'line', 'labels': [label], 'values': [value],
                                  'engs': [eng] if eng else [], 'ws': [w]}))
        ix += 1

    rows = []
    for typ, v in items:
        if typ == 'section':
            rows.append({'type': 'section', 'title': v})
        else:
            rows.append(_finish_row(v))
    rows = _merge_blocks(rows)
    rows = _merge_weather(rows)
    # 中身のない区切りは消す
    out = []
    for i, r in enumerate(rows):
        if r['type'] == 'section' and (i + 1 >= len(rows) or rows[i + 1]['type'] == 'section'):
            continue
        out.append(r)
    return header, out


def _uniq(xs):
    out = []
    for x in xs:
        if x and x not in out:
            out.append(x)
    return out


def _finish_row(v):
    level = level_of(v['ws'])
    if v['kind'] == 'line':
        labels = _uniq(v['labels']) or ['']
        label = '・'.join(l for l in labels if l)
        label = LABEL_RENAME.get(label, label)
        values = [x for x in v['values'] if x]
        # 気温/露点・風向/風速は値を「／」でつなぐ
        if len(set(values)) == 1 and len(values) > 1 and label == '風':
            values = values[:1]
        value = ' ／ '.join(values)
        row = {'type': 'row', 'code': ' '.join(v['engs']), 'item': label,
               'value': value, 'lines': None, 'grid': None, 'level': level}
    else:
        label = LABEL_RENAME.get(v['label'], v['label'])
        subs = [(l, x) for l, x in v['subs'] if x]
        row = {'type': 'row', 'code': ' '.join(v['engs']), 'item': label,
               'value': '', 'lines': None, 'grid': None, 'level': level,
               'block': v['label'], 'subs': subs}
        if len(subs) >= 4:
            row['grid'] = subs
        else:
            row['value'] = '・'.join(f'{l} {x}' if l else x for l, x in subs)
    row['level'] = _adjust_level(row)
    return row


def _adjust_level(row):
    level = row['level']
    text = row['item'] + ' ' + row['value']
    if WX_AS_CAUTION and level == 'red' and re.match(r'^(天気|気象現象|一時的に|下記の状態)', row['item'] or row['value']):
        level = 'org'
    if WX_AS_CAUTION and level == 'red' and row['item'].startswith('天気'):
        level = 'org'
    if FEW_SCT_NO_FLAG and level and ('1/8～2/8' in text or '3/8～4/8' in text) \
            and '積乱雲' not in text and '塔状積雲' not in text:
        level = ''
    if FEW_SCT_NO_FLAG and level and re.search(r'雲量 [1-4]/8', text) \
            and '積乱雲' not in text and '塔状積雲' not in text:
        level = ''
    return level


def _merge_blocks(rows):
    """連続する RVR・天気の開始終了を1行にまとめる。"""
    out = []
    for r in rows:
        if r['type'] == 'row' and r.get('block') in ('滑走路視距離', '気象現象補足'):
            line = _block_line(r)
            if out and out[-1]['type'] == 'row' and out[-1].get('block') == r['block'] and out[-1].get('merged'):
                m = out[-1]
                m['lines'].append(line)
                for word in r['code'].split():
                    if word not in m['code'].split():
                        m['code'] = (m['code'] + ' ' + word).strip()
                m['level'] = max_level(m['level'], r['level'])
                continue
            r = dict(r)
            r['merged'] = True
            r['lines'] = [line]
            r['grid'] = None
            r['value'] = ''
            if r['block'] == '気象現象補足':
                r['level'] = 'org' if (WX_AS_CAUTION and r['level'] == 'red') else r['level']
            out.append(r)
            continue
        out.append(r)
    for r in out:
        if r.get('merged') and r['block'] == '滑走路視距離':
            r['item'] = '滑走路視距離' + (f'（{len(r["lines"])}本）' if len(r['lines']) > 1 else '')
    return out


def _merge_weather(rows):
    """本文の「天気 1」「天気 2」… を1行にまとめる。"""
    out = []
    for r in rows:
        if (r['type'] == 'row' and re.match(r'^(天気|気象現象)( \d+)?$', r['item'] or '') and out
                and out[-1]['type'] == 'row' and out[-1].get('wx_merged')):
            m = out[-1]
            m['value'] = m['value'] + '・' + r['value']
            m['code'] = (m['code'] + ' ' + r['code']).strip()
            m['level'] = max_level(m['level'], r['level'])
            continue
        if r['type'] == 'row' and re.match(r'^(天気|気象現象)( \d+)?$', r['item'] or ''):
            r = dict(r)
            r['item'] = '天気'
            r['wx_merged'] = True
        out.append(r)
    return out


def _block_line(r):
    d = {l: x for l, x in r.get('subs', [])}
    if r['block'] == '滑走路視距離':
        rw = d.get('滑走路', '').replace('RW', '')
        vis = d.get('視程', d.get('視距離', ''))
        trend = d.get('傾向', '')
        parts = [p for p in (vis, trend) if p and p != '動向情報なし']
        return f'{rw}：' + '・'.join(parts) if rw else '・'.join(parts)
    # 気象現象補足
    wx = d.get('気象現象', '')
    t = []
    if d.get('開始時刻'):
        t.append('開始 ' + d['開始時刻'].replace('(JST)', ''))
    if d.get('終了時刻'):
        t.append('終了 ' + d['終了時刻'].replace('(JST)', ''))
    return f'{wx}　' + '・'.join(t)


def max_level(a, b):
    order = {'red': 2, 'org': 1, '': 0, 'unk': 0}
    return a if order.get(a, 0) >= order.get(b, 0) else b


# ============================================================
# 原文の群と行の対応（未解読の検出・チップの色）
# ============================================================
def match_tokens(raw_text, rows, header, metartaf):
    toks = raw_text.split()
    owner = [None] * len(toks)          # 群 → 行番号 / 'hd'
    # 見出しに回した群
    hd_words = {'METAR', 'SPECI', 'TAF', 'COR', 'AMD', 'RTD', 'AUTO', 'RMK'}
    for i, t in enumerate(toks[:6]):
        if t in hd_words or re.fullmatch(r'[A-Z]{4}', t) and i <= 2 or re.fullmatch(r'\d{6}Z', t):
            owner[i] = 'hd'
    for i, t in enumerate(toks):
        if t in ('RMK',):
            owner[i] = 'hd'
    # 各行の群を順に探す
    p = 0
    for r in rows:
        if r['type'] != 'row' or not r['code']:
            continue
        first = None
        for word in r['code'].split():
            for k in range(p, min(len(toks), p + 40)):
                if owner[k] is None and toks[k] == word:
                    owner[k] = r
                    if first is None:
                        first = k
                    break
        if first is not None:
            r['pos'] = first
            p = first
    # PIREP 等の途中にある訳されない語（OBS・AND など）はその行に含める
    for i, o in enumerate(owner):
        if o is not None:
            continue
        prev_o = next((owner[k] for k in range(i - 1, -1, -1) if owner[k] not in (None, 'hd')), None)
        next_o = next((owner[k] for k in range(i + 1, len(owner)) if owner[k] not in (None, 'hd')), None)
        if prev_o is not None and prev_o is next_o:
            owner[i] = prev_o
        elif toks[i] in ('AND', 'OBS') and next_o is not None and next_o.get('block') == '報告等':
            owner[i] = next_o
    for r in rows:
        if r['type'] == 'row':
            idx = [k for k, o in enumerate(owner) if o is r]
            if idx:
                r['code'] = ' '.join(toks[k] for k in idx)
                r['pos'] = idx[0]
    # 未解読の群を行として差し込む
    unknown = [i for i, o in enumerate(owner) if o is None]
    if metartaf == 1 and unknown:
        new_rows = []
        pending = sorted(unknown)
        for r in rows:
            pos = r.get('pos')
            if pos is not None:
                while pending and pending[0] < pos:
                    new_rows.append(_unknown_row(toks[pending.pop(0)]))
            new_rows.append(r)
        for k in pending:
            new_rows.append(_unknown_row(toks[k]))
        rows = new_rows
    chips = []
    for i, t in enumerate(toks):
        o = owner[i]
        if o == 'hd':
            chips.append((t, 'hd'))
        elif o is None:
            chips.append((t, 'unk'))
        else:
            chips.append((t, o['level']))
    return rows, chips


def _unknown_row(tok):
    return {'type': 'row', 'code': tok, 'item': '（不明）',
            'value': '解読プログラムが訳せなかった群', 'lines': None, 'grid': None,
            'level': 'unk'}


# ============================================================
# 描画部品
# ============================================================
def register_fonts(path):
    if FONT in pdfmetrics.getRegisteredFontNames():
        return
    here = os.path.dirname(os.path.abspath(__file__))
    cands = ['./fonts/' if path == '' else path + '/fonts/',
             os.path.join(here, 'fonts'), os.path.join(here, 'static', 'fonts'),
             os.path.join(os.getcwd(), 'static', 'fonts')]
    base = next((d for d in cands if os.path.exists(os.path.join(d, 'GenShinGothic-Monospace-Medium.ttf'))), cands[0])
    medium = os.path.join(base, 'GenShinGothic-Monospace-Medium.ttf')
    regular = os.path.join(base, 'GenShinGothic-Monospace-Regular.ttf')
    if not os.path.exists(regular):
        regular = medium
    pdfmetrics.registerFont(TTFont(FONT, regular))
    pdfmetrics.registerFont(TTFont(FONT_B, medium))
    from reportlab.lib.fonts import addMapping
    addMapping(FONT, 0, 0, FONT)
    addMapping(FONT, 1, 0, FONT_B)
    addMapping(FONT, 0, 1, FONT)
    addMapping(FONT, 1, 1, FONT_B)


_STYLES = {}


def style(size=9.75, bold=False, color=INK, leading=None, align=0):
    key = (size, bold, color.hexval(), leading, align)
    if key not in _STYLES:
        _STYLES[key] = ParagraphStyle(
            name='s%d' % len(_STYLES), fontName=FONT_B if bold else FONT, fontSize=size,
            leading=leading or size * 1.4, textColor=color, alignment=align,
            wordWrap='CJK')
    return _STYLES[key]


def para(text, **kw):
    return Paragraph(escape(text), style(**kw))


class Header(Flowable):
    def __init__(self, kicker, h1, sub, info):
        super().__init__()
        self.kicker, self.h1, self.sub, self.info = kicker, h1, sub, info

    def wrap(self, aw, ah):
        self.width = aw
        return aw, 50

    def draw(self):
        c = self.canv
        c.setFillColor(MUTED)
        c.setFont(FONT_B, 9)
        c.drawString(0, 38, self.kicker)
        c.setFillColor(INK)
        c.setFont(FONT_B, 16.5)
        c.drawString(0, 14, self.h1)
        if self.sub:
            w = pdfmetrics.stringWidth(self.h1, FONT_B, 16.5)
            c.setFillColor(MUTED)
            c.setFont(FONT, 10.5)
            c.drawString(w + 8, 14, self.sub)
        c.setFillColor(MUTED)
        c.setFont(FONT, 9)
        c.drawRightString(self.width, 14, self.info)
        c.setStrokeColor(NAVY)
        c.setLineWidth(1.5)
        c.line(0, 4, self.width, 4)


class RawText(Flowable):
    """原文。区切りは付けず、判定が赤・橙の群だけ文字色を変える。"""
    FS = 9.5
    LEAD = 13.5
    PAD = 7

    def __init__(self, lines, indent_cont=False):
        super().__init__()
        self.lines = lines
        self.indent_cont = indent_cont

    def wrap(self, aw, ah):
        self.width = aw
        inner = aw - self.PAD * 2
        sp = pdfmetrics.stringWidth(' ', FONT_B, self.FS)
        self.placed = []          # (行番号, x, 文字列, 判定)
        self.soft_break = set()   # 群と群の間で折り返した行（行末に空白を入れる）
        self.sp = sp
        row = 0
        for words in self.lines:
            indent = words[0][1] if words and words[0][0] == '' else 0
            words = words[1:] if words and words[0][0] == '' else words
            x = sp * indent
            lead_x = x
            for i, (w, lv) in enumerate(words):
                ww = pdfmetrics.stringWidth(w, FONT_B, self.FS)
                if x > lead_x and x + ww > inner:
                    self.soft_break.add(row)
                    row += 1
                    lead_x = lead_x + sp * 2 if self.indent_cont else 0
                    x = lead_x
                # 1群が1行に入らないときは文字で折り返す
                piece = ''
                for ch in w:
                    if x + pdfmetrics.stringWidth(piece + ch, FONT_B, self.FS) > inner and piece:
                        self.placed.append((row, x, piece, lv))
                        row += 1
                        x = lead_x
                        piece = ch
                    else:
                        piece += ch
                self.placed.append((row, x, piece, lv))
                x += pdfmetrics.stringWidth(piece, FONT_B, self.FS) + sp
            row += 1
        self.rows = row
        self.height = self.rows * self.LEAD + self.PAD * 2 - (self.LEAD - self.FS) + 2
        return aw, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(PANEL)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.75)
        c.roundRect(0, 0, self.width, self.height, 3, stroke=1, fill=1)
        top = self.height - self.PAD - self.FS + 1
        # コピーしたときに群の間の空白が残るよう、空白も文字として1行ずつ書く
        rows = {}
        for row, x, text, lv in self.placed:
            rows.setdefault(row, []).append((x, text, lv))
        for row, items in rows.items():
            t = c.beginText(self.PAD, top - row * self.LEAD)
            t.setFont(FONT_B, self.FS)
            cursor = 0.0
            for x, text, lv in sorted(items):
                n = int(round((x - cursor) / self.sp))
                if n > 0:
                    t.setFillColor(INK)
                    t.textOut(' ' * n)
                t.setFillColor(RAW_TEXT_COLOR.get(lv, INK))
                t.textOut(text)
                cursor = x + pdfmetrics.stringWidth(text, FONT_B, self.FS)
            if row in self.soft_break:
                t.setFillColor(INK)
                t.textOut(' ')
            c.drawText(t)


class Pill(Flowable):
    def __init__(self, level):
        super().__init__()
        self.level = level

    def wrap(self, aw, ah):
        self.aw = aw
        return aw, 13.5 if self.level else 0

    def draw(self):
        if not self.level:
            return
        bg, tx, bd = LEVEL_COLOR[self.level]
        label = LEVEL_LABEL[self.level]
        w = pdfmetrics.stringWidth(label, FONT_B, 9) + 9
        x = (self.aw - w) / 2
        c = self.canv
        c.setFillColor(bg)
        c.setStrokeColor(bd)
        c.setLineWidth(0.75)
        if self.level == 'unk':
            c.setDash(2, 1.5)
        c.roundRect(x, 0, w, 13.5, 2, stroke=1, fill=1)
        c.setDash()
        c.setFillColor(tx)
        c.setFont(FONT_B, 9)
        c.drawCentredString(x + w / 2, 3.6, label)


class NumberedCanvas(rl_canvas.Canvas):
    """フッター（凡例・ページ番号）と2ページ目以降の見出しを描く。"""

    def __init__(self, *args, running='', footer_right='', **kwargs):
        super().__init__(*args, **kwargs)
        self._saved = []
        self._running = running
        self._footer_right = footer_right

    def showPage(self):
        self._saved.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved)
        for state in self._saved:
            self.__dict__.update(state)
            self._decorate(total)
            super().showPage()
        super().save()

    def _decorate(self, total):
        page = self._pageNumber
        y = MARGIN_BOTTOM - 22
        self.setStrokeColor(RULE)
        self.setLineWidth(0.75)
        self.line(MARGIN_X, y + 12, PAGE_W - MARGIN_X, y + 12)
        x = MARGIN_X
        for lv in ('red', 'org', 'unk'):
            bg, tx, bd = LEVEL_COLOR[lv]
            label = LEVEL_LABEL[lv]
            w = pdfmetrics.stringWidth(label, FONT_B, 8.5) + 8
            self.setFillColor(bg)
            self.setStrokeColor(bd)
            if lv == 'unk':
                self.setDash(2, 1.5)
            self.roundRect(x, y - 2.5, w, 11.5, 2, stroke=1, fill=1)
            self.setDash()
            self.setFillColor(tx)
            self.setFont(FONT_B, 8.5)
            self.drawCentredString(x + w / 2, y + 0.5, label)
            x += w + 4
        self.setFillColor(MUTED)
        self.setFont(FONT, 9)
        self.drawString(x + 4, y + 0.5, '判定は目安。最終判断は各自の気象最低条件による')
        self.drawRightString(PAGE_W - MARGIN_X, y + 0.5, f'{self._footer_right}　{page} / {total}')
        if page > 1:
            self.setFont(FONT_B, 9)
            self.setFillColor(MUTED)
            self.drawString(MARGIN_X, PAGE_H - MARGIN_TOP + 12, self._running)


# ============================================================
# 入力 → 描画用データ、PDF 出力
# ============================================================
def prepare(jpn, eng, warning_flg, path, kind):
    """kind: 1=METAR 2=TAF。描画に必要なデータをまとめて返す。"""
    register_fonts(path)
    raw_lines, body = split_raw(jpn, eng, warning_flg)
    header, rows = build_rows(body, kind)
    raw_text = ' '.join(raw_lines).replace('$', '').strip()
    rows, chips = match_tokens(raw_text, rows, header, kind)
    if kind == 1:
        toks = raw_text.split()
        station_code = toks[1] if len(toks) > 1 else ''
    else:
        m = re.search(r'\b([A-Z]{4})\b\s+\d{6}Z', raw_text)
        station_code = m.group(1) if m else ''
    # 原文：行ごとに群の判定色（赤・橙のみ）を付ける。TAF は行の区切りを残す
    lines = raw_lines if kind == 2 else [raw_text]
    levels = [lv for _, lv in chips]
    colored = []
    k = 0
    # FM で改行した行の字下げ：2行目以降の原文と同じ（無ければ2文字）
    cont_ind = [len(ln) - len(ln.lstrip(' ')) for ln in lines[1:] if ln.strip()]
    cont_ind = max(cont_ind) if cont_ind and max(cont_ind) > 0 else 2
    for ln in lines:
        words = [('', len(ln) - len(ln.lstrip(' ')))]
        for w in ln.replace('$', '').split():
            lv = levels[k] if k < len(levels) else ''
            words.append((w, lv if lv in ('red', 'org') else ''))
            k += 1
        if kind == 2:
            # TAF は FM（FMddhhmm／FM 単独）の前でも改行する
            cur = [words[0]]
            for w in words[1:]:
                if len(cur) > 1 and re.match(r'^FM(\d{6})?$', w[0]):
                    colored.append(cur)
                    cur = [('', cont_ind)]
                cur.append(w)
            colored.append(cur)
        else:
            colored.append(words)
    return {'raw_lines': raw_lines, 'raw_text': raw_text, 'header': header, 'rows': rows,
            'colored': colored, 'station_code': station_code}


def raw_section(colored, indent_cont):
    """原文（見出しなし）。"""
    return [RawText(colored, indent_cont=indent_cont)]


def build_pdf(filename, story, title, running, footer_right):
    doc = SimpleDocTemplate(filename, pagesize=portrait(A4),
                            leftMargin=MARGIN_X, rightMargin=MARGIN_X,
                            topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
                            title=title, author='WX0S0220')

    def _make_canvas(*args, **kwargs):
        return NumberedCanvas(*args, running=running, footer_right=footer_right, **kwargs)

    doc.build(story, canvasmaker=_make_canvas)
    return filename
