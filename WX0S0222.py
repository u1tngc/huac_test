#PGM-ID:WX0S0222
#PGM-NAME:[P]WX TAF 詳細PDF出力
#最終更新日:2026/11/21
"""
TAF 1通を METAR（WX0S0221）と同じ構成の PDF にする。

    WX0S0222.taf_pdf(tafJpn, tafEng, warning_flg, fileName, ix1, path)
        tafJpn      : 解読結果（日本語）のリスト。先頭に原文行（TAF の各行）、その後に空行が入っている前提
        tafEng      : 各行に対応する原文の群
        warning_flg : WX0S0204.checkWarning の結果（0:黒 1:赤 2:橙）
        fileName    : 出力ファイル名（拡張子・連番なし）
        ix1         : 何通目か（0始まり）。出力名は fileName_{ix1+1}.pdf
        path        : 出力先フォルダ
    戻り値 : 出力した PDF のファイル名

レイアウト
    ・見出し → 原文（行の区切りを残し、赤・橙の群に色） → 基本予報 → 変化群1… の順に1列で並べる
    ・各ブロックの見出し帯（1行）に 種類（BECMG/TEMPO/FM）・一言の説明・時間帯（JST）を出す
    ・同じブロックの雲・乱気流・着氷はそれぞれ1行にまとめ、風や雲の文言は短くする
    ・A4 1枚に収まらないときは次ページに続ける
"""

import re
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Flowable, Paragraph, Spacer, Table, TableStyle

import WX0S0220 as C

FS = 9.75          # 本文の文字サイズ
GAP = 8            # ブロック間
HEAD_BG = {'base': HexColor('#E6EDF5'), 'grp': HexColor('#F1F3F5')}
KIND_TEXT = {
    'BECMG': 'この間に変化し、以後この状態',
    'TEMPO': 'この間、一時的にこの状態',
    'FM': 'この時刻からこの状態',
}
MERGE_KEYS = ('雲', '乱気流', '着氷')


def taf_pdf(tafJpn, tafEng, warning_flg, fileName, ix1, path):
    FILENAME = path + fileName + '_' + str(ix1 + 1) + '.pdf'
    d = C.prepare(tafJpn, tafEng, warning_flg, path, 2)
    header = d['header']
    blocks = _split_blocks(d['rows'])
    n_grp = sum(1 for b in blocks if b['kind'] == 'grp')
    h1 = f"{header.get('time', '')}　TAF".strip()
    kicker = f"{d['station_code']} {header.get('station', '')}・TAF 詳細".strip()
    info = f"変化群 {n_grp}個"

    story = [C.Header(kicker, h1, header.get('class', ''), info), Spacer(1, 8)]
    story += C.raw_section(d['colored'], indent_cont=True)
    story.append(Spacer(1, GAP))
    for i, b in enumerate(blocks):
        if i > 0:
            story.append(Spacer(1, GAP))
        story += _block_flow(b, C.CONTENT_W, FS)
    return C.build_pdf(FILENAME, story, f"{d['station_code']} {h1}",
                       f"{d['station_code']} {h1}（続き）", 'WX0S0222 出力')


# ============================================================
# ブロック分け（基本予報・変化群N）
# ============================================================
def _clean_time(v):
    v = v.replace('(JST)', '').replace('～', '〜')
    return v + ' JST' if v else ''


def _split_blocks(rows):
    blocks = []
    for r in rows:
        if r['type'] == 'section':
            m = re.match(r'変化群(\d+)（(\w+)）', r['title'])
            if m:
                blocks.append({'kind': 'grp', 'no': int(m.group(1)), 'kw': m.group(2),
                               'time': '', 'prob': '', 'rows': []})
            else:
                blocks.append({'kind': 'base', 'kw': '', 'time': '', 'prob': '', 'rows': []})
            continue
        if not blocks:
            blocks.append({'kind': 'base', 'kw': '', 'time': '', 'prob': '', 'rows': []})
        b = blocks[-1]
        if r['item'] in ('対象時刻', '開始時間') and not b['time']:
            b['time'] = _clean_time(r['value'])
            continue
        if r['item'] == '発生確率':
            b['prob'] = r['value']
            continue
        b['rows'].append(r)
    for b in blocks:
        b['rows'] = _compact(b['rows'])
    return blocks


def _short_value(key, v):
    """風・雲・乱気流/着氷の文言を短くする。"""
    m = re.match(r'(\d+)度\((.+?)\)からの風', v)
    if key == '風' and m:
        parts = [p.strip() for p in v.split('／')]
        out = f"{m.group(2)} {int(m.group(1)):03d}°"
        if len(parts) > 1:
            out += ' ' + parts[1]
        if len(parts) > 2:
            out += ' G' + parts[2]
        return out
    v = v.replace('全天を覆う雲', '8/8').replace('の雲', '')
    v = re.sub(r'^雲量', '', v).replace(' 雲底', ' ')
    v = v.replace('強度 ', '').replace('・高度 ', '　')
    return v


def _compact(rows):
    """同じ種類の行（雲・乱気流・着氷）を1行にまとめる。"""
    out = []
    for r in rows:
        r = dict(r)
        key = re.sub(r'( ?\d+)$', '', r['item'] or '')
        key = {'乱気流情報': '乱気流', '着氷情報': '着氷'}.get(key, key)
        if r['value']:
            r['value'] = _short_value(key, r['value'])
        if key in MERGE_KEYS and out and out[-1].get('_key') == key:
            m = out[-1]
            m['lines'] = (m.get('lines') or [m['value']]) + [r['value']]
            m['code'] += ' ' + r['code']
            m['level'] = C.max_level(m['level'], r['level'])
            continue
        r['_key'] = key
        if key in MERGE_KEYS:
            r['item'] = key
        out.append(r)
    return out


# ============================================================
# 描画
# ============================================================
class _BlockHead(Flowable):
    """ブロック見出し帯（1行）：左に名称と説明、右に時間帯。"""

    def __init__(self, title, time, note, fs, kind):
        super().__init__()
        self.title, self.time, self.note, self.fs, self.kind = title, time, note, fs, kind
        self.keepWithNext = True

    def wrap(self, aw, ah):
        self.width = aw
        self.h = self.fs * 2.1
        return aw, self.h

    def draw(self):
        c = self.canv
        fs = self.fs
        c.setFillColor(HEAD_BG[self.kind])
        c.rect(0, 0, self.width, self.h, stroke=0, fill=1)
        c.setStrokeColor(C.NAVY)
        c.setLineWidth(0.9)
        c.line(0, 0, self.width, 0)
        base = self.h - fs * 1.45
        c.setFillColor(C.NAVY)
        c.setFont(C.FONT_B, fs * 1.05)
        c.drawString(4, base, self.title)
        if self.note:
            x = 4 + pdfmetrics.stringWidth(self.title, C.FONT_B, fs * 1.05) + fs * 1.2
            c.setFillColor(C.SUBTLE)
            c.setFont(C.FONT, fs * 0.9)
            c.drawString(x, base, self.note)
        c.setFillColor(C.INK)
        c.setFont(C.FONT_B, fs)
        c.drawRightString(self.width - 4, base, self.time)


class _Pill(Flowable):
    """判定ピル（文字サイズ可変）。"""

    def __init__(self, level, fs):
        super().__init__()
        self.level, self.fs = level, fs

    def wrap(self, aw, ah):
        self.aw = aw
        return aw, (self.fs * 1.5 if self.level else 0)

    def draw(self):
        if not self.level:
            return
        bg, tx, bd = C.LEVEL_COLOR[self.level]
        label = C.LEVEL_LABEL[self.level]
        w = pdfmetrics.stringWidth(label, C.FONT_B, self.fs) + self.fs
        h = self.fs * 1.5
        x = (self.aw - w) / 2
        c = self.canv
        c.setFillColor(bg)
        c.setStrokeColor(bd)
        c.setLineWidth(0.6)
        c.roundRect(x, 0, w, h, 2, stroke=1, fill=1)
        c.setFillColor(tx)
        c.setFont(C.FONT_B, self.fs)
        c.drawCentredString(x + w / 2, h * 0.27, label)


def _block_flow(b, width, fs):
    if b['kind'] == 'base':
        title, note = '基本予報', ''
    else:
        title = f"変化群{b['no']}　{b['kw']}"
        note = KIND_TEXT.get(b['kw'], '')
        if b['prob']:
            note = f"発生確率 {b['prob']}・" + note
    head = _BlockHead(title, b['time'], note, fs, b['kind'])
    # 列幅：群｜項目｜解読｜判定（METAR の表と同じ並び）
    wc, wi, wj = C.COL_W[0], C.COL_W[1], C.COL_W[3]
    wv = width - wc - wi - wj
    data = []
    cmds = [('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4.5), ('RIGHTPADDING', (0, 0), (-1, -1), 4.5),
            ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5)]
    for i, r in enumerate(b['rows']):
        code = Paragraph(escape(r['code']), C.style(fs * 0.92, bold=True))
        item = Paragraph(escape(r['item'] or '—'), C.style(fs, bold=True))
        if r.get('lines'):
            val = Paragraph('<br/>'.join(escape(x) for x in r['lines']), C.style(fs))
        elif r.get('grid'):
            val = Paragraph('<br/>'.join(escape(f'{l} {x}') for l, x in r['grid']), C.style(fs))
        else:
            val = Paragraph(escape(r['value']), C.style(fs))
        data.append([code, item, val, _Pill(r['level'], fs * 0.92)])
        cmds.append(('LINEBELOW', (0, i), (-1, i), 0.75, C.LIGHT_RULE))
    if not data:
        data = [['', '', Paragraph('（変化する要素なし）', C.style(fs, color=C.SUBTLE)), '']]
    t = Table(data, colWidths=[wc, wi, wv, wj])
    t.setStyle(TableStyle(cmds))
    return [head, t]
