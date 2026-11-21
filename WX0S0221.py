#PGM-ID:WX0S0221
#PGM-NAME:[P]WX METAR 詳細PDF出力
#最終更新日:2026/11/21
"""
METAR/SPECI 1通を P3 レイアウト（見出し・原文・群｜項目｜解読｜判定の表）で PDF にする。

    WX0S0221.metar_pdf(metarJpn, metarEng, warning_flg, fileName, ix1, path)
        metarJpn    : 解読結果（日本語）のリスト。先頭に原文行、その後に空行が入っている前提
        metarEng    : 各行に対応する原文の群
        warning_flg : WX0S0204.checkWarning の結果（0:黒 1:赤 2:橙）
        fileName    : 出力ファイル名（拡張子・連番なし）
        ix1         : 何通目か（0始まり）。出力名は fileName_{ix1+1}.pdf
        path        : 出力先フォルダ
    戻り値 : 出力した PDF のファイル名

    ・RVR が複数あるときは1行、RMK の天気の開始・終了も1行にまとめる（WX0S0220.build_rows）
    ・解読プログラムが訳せなかった群は「未解読」として表に残す
    ・1ページに収まらないときは次ページに続ける（表の見出し行は次ページにも出す）
"""

from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

import WX0S0220 as C


def metar_pdf(metarJpn, metarEng, warning_flg, fileName, ix1, path):
    FILENAME = path + fileName + '_' + str(ix1 + 1) + '.pdf'
    d = C.prepare(metarJpn, metarEng, warning_flg, path, 1)
    header = d['header']
    kind = header.get('kind') or 'METAR'
    h1 = f"{header.get('time', '')}　{kind}".strip()
    kicker = f"{d['station_code']} {header.get('station', '')}・METAR 詳細".strip()

    story = [C.Header(kicker, h1, header.get('class', ''), ''), Spacer(1, 8)]
    story += C.raw_section(d['colored'], indent_cont=False)
    story += [Spacer(1, 9), _make_table(d['rows'])]
    return C.build_pdf(FILENAME, story, f"{d['station_code']} {h1}",
                       f"{d['station_code']} {h1}（続き）", 'WX0S0221 出力')


# ============================================================
# 表（群｜項目｜解読｜判定）
# ============================================================
def _value_cell(r):
    if r.get('lines'):
        lines = r['lines']
        if len(lines) >= 4:
            half = (len(lines) + 1) // 2
            data = []
            for i in range(half):
                a = lines[i]
                b = lines[i + half] if i + half < len(lines) else ''
                data.append([C.para(a, size=9.75), C.para(b, size=9.75)])
            t = Table(data, colWidths=[C.COL_W[2] / 2 - 6] * 2)
            t.setStyle(_grid_style())
            return t
        return Paragraph('<br/>'.join(escape(x) for x in lines), C.style(9.75))
    if r.get('grid'):
        subs = r['grid']
        data = []
        lw = 44
        vw = C.COL_W[2] / 2 - lw - 6
        for i in range(0, len(subs), 2):
            row = []
            for l, x in subs[i:i + 2]:
                row += [C.para(l, size=9, color=C.SUBTLE), C.para(x, size=9.75)]
            while len(row) < 4:
                row += ['', '']
            data.append(row)
        t = Table(data, colWidths=[lw, vw, lw, vw])
        t.setStyle(_grid_style())
        return t
    return C.para(r['value'], size=9.75, color=C.SUBTLE if r['level'] == 'unk' else C.INK)


def _grid_style():
    return TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ])


def _make_table(rows):
    head = [C.para('群', size=9, bold=True, color=HexColor('#3D4650')),
            C.para('項目', size=9, bold=True, color=HexColor('#3D4650')),
            C.para('解読', size=9, bold=True, color=HexColor('#3D4650')),
            Paragraph('判定', C.style(9, bold=True, color=HexColor('#3D4650'), align=TA_CENTER))]
    data = [head]
    cmds = [
        ('FONT', (0, 0), (-1, -1), C.FONT, 9.75),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4.5),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('BACKGROUND', (0, 0), (-1, 0), C.PANEL),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, C.NAVY),
    ]
    for r in rows:
        ri = len(data)
        if r['type'] == 'section':
            data.append([C.para(r['title'], size=9, bold=True, color=C.NAVY), '', '', ''])
            cmds += [('SPAN', (0, ri), (-1, ri)),
                     ('TOPPADDING', (0, ri), (-1, ri), 7),
                     ('BOTTOMPADDING', (0, ri), (-1, ri), 2.5),
                     ('LINEBELOW', (0, ri), (-1, ri), 0.75, C.NAVY)]
            continue
        code = Paragraph(escape(r['code']), C.style(9, bold=True,
                         color=C.SUBTLE if r['level'] == 'unk' else C.INK))
        item = C.para(r['item'] or '—', size=9.75, bold=True,
                  color=C.SUBTLE if r['level'] == 'unk' else C.INK)
        data.append([code, item, _value_cell(r), C.Pill(r['level'])])
        cmds.append(('LINEBELOW', (0, ri), (-1, ri), 0.75, C.LIGHT_RULE))
        if r['level'] == 'unk':
            cmds.append(('BACKGROUND', (0, ri), (-1, ri), C.UNK_ROW))
    t = Table(data, colWidths=C.COL_W, repeatRows=1)
    t.setStyle(TableStyle(cmds))
    return t


