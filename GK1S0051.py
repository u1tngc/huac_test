#PGM-ID:GK1S0051
#PGM-NAME:GK航空図表示
#最終更新日:2026/10/25

import gzip
import hashlib
import os
import re
import threading

from flask import Response, request

# 航空図（folium で生成した静的HTML）
CHART_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "GK_CHART.html")

# 座標の小数桁数（5桁 = 約1m）
COORD_DIGITS = 5
_RE_COORD = re.compile(r"-?\d+\.\d{%d,}" % (COORD_DIGITS + 1))

# ブラウザのキャッシュ有効時間（秒）。期限切れ後は ETag で確認し、変更がなければ 304 を返す
MAX_AGE = 3600

_lock = threading.Lock()
_cache = {"mtime": None, "raw": b"", "gz": b"", "etag": ""}


def round_coords(text):
    """小数が COORD_DIGITS 桁を超える数値を COORD_DIGITS 桁に丸める"""
    def _r(m):
        v = ("%.*f" % (COORD_DIGITS, float(m.group(0)))).rstrip("0").rstrip(".")
        return "0" if v in ("-0", "") else v
    return _RE_COORD.sub(_r, text)


def _load():
    """HTMLを読み込み、座標の丸めと gzip 圧縮を済ませてメモリに保持する（ファイル更新時のみ再作成）"""
    mtime = os.path.getmtime(CHART_PATH)
    if _cache["mtime"] == mtime:
        return _cache
    with _lock:
        if _cache["mtime"] != mtime:
            with open(CHART_PATH, encoding="utf-8") as f:
                raw = round_coords(f.read()).encode("utf-8")
            _cache["raw"] = raw
            _cache["gz"] = gzip.compress(raw, 6)
            _cache["etag"] = '"' + hashlib.md5(raw).hexdigest() + '"'
            _cache["mtime"] = mtime
    return _cache


def get_chart():
    """航空図のレスポンスを返す"""
    c = _load()
    headers = {
        "Cache-Control": "private, max-age=%d" % MAX_AGE,
        "ETag": c["etag"],
        "Vary": "Accept-Encoding",
    }
    # 前回から変更がなければ本文を送らない
    if c["etag"] in request.headers.get("If-None-Match", ""):
        return Response(status=304, headers=headers)
    if "gzip" in request.headers.get("Accept-Encoding", ""):
        headers["Content-Encoding"] = "gzip"
        body = c["gz"]
    else:
        body = c["raw"]
    return Response(body, mimetype="text/html", content_type="text/html; charset=utf-8", headers=headers)
