#PGM-ID:GK1S0044
#PGM-NAME:GK入所時期シミュレーション
#最終更新日:2026/09/15

from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta

import GK0S0B1D
import GK0S0B2D
import GK0S0B3D

#ソロ要件の発数
SOLO_YOKEN = 28
#２３移行となる発数
SOLO_IKO = 11
#２日に１回ソロに出る場合の所要日数
SOLO_PAIR = 2
#合宿日程が未登録の年度を仮生成する年数
KARI_NENDO = 3
#仮生成した合宿の名称に付与する文字
KARI_MARK = "（仮）"
#ＥＣＷ　0=正常
ECW_SEIJO = 0
#ＥＣＷ　1=試算不可（要件到達済み／ソロ状況未登録／合宿日程不足）
ECW_FUKA = 1
#ＥＣＷ　2=ソロ発数０のため次の合宿で１発出た想定として試算
ECW_SOLO0 = 2


def get_stuList():
    ret_array = GK0S0B1D.get_stuList()
    return ret_array

def nyusho_sim(sim_array):
    """指定した学生の入所時期をシミュレーションする
       引数　：[[学籍番号, 試算区分], ...]　試算区分 0=標準試算 1=最短試算
       戻り値：[[ＥＣＷ, 学籍番号, 氏名, ソロ発数, ２３移行有無, 試算区分,
                 要件到達見込み, 入所時期, 中間チェック①, 中間チェック②,
                 中間チェック③, 中間チェック④, 学生ＣＨＫ, 教官ＣＨＫ], ...]
       中間チェックは①②が２３移行となる合宿基準、③④が学生ＣＨＫ基準
       ＥＣＷ 0=正常
              1=試算不可（要件到達済み／ソロ状況未登録／合宿日程不足）
              2=ソロ発数０のため次の合宿で１発出た想定として試算
       ＥＣＷ（昇順）＞ソロ発数（降順）＞学籍番号（昇順）で並べて返す"""
    ret_array = []
    if not sim_array:
        return ret_array
    ymd = get_shoriYmd()
    #合宿日程は全学生で共用するため、ループの外で1回だけ取得する
    gasshuku_list = get_gasshukuList()
    for ix1 in range(len(sim_array)):
        gakuseiID = sim_array[ix1][0]
        shisanKbn = str(sim_array[ix1][1])
        ret_array.append(sim_gakusei(gakuseiID, shisanKbn, ymd, gasshuku_list))
    ret_array.sort(key=get_sortKey)
    return ret_array


def get_sortKey(info):
    """ＥＣＷ（昇順）＞ソロ発数（降順）＞学籍番号（昇順）で並べるためのキーを返す
       ソロ発数は降順のため符号を反転させる"""
    soloSu = info[3]
    if str(soloSu) == "":
        soloSu = -1
    return (int(info[0]), int(soloSu) * -1, str(info[1]))


def sim_gakusei(gakuseiID, shisanKbn, ymd, gasshuku_list):
    #氏名は学籍番号をユーザーidとしてユーザー管理セグから取得する
    name = GK0S0B1D.get_userName(gakuseiID)
    solo_info = GK0S0B2D.get_soloJokyo(gakuseiID, ymd)
    if not solo_info:
        #ソロ状況が未登録の場合は試算不可とする
        return get_ecwArray(ECW_FUKA, gakuseiID, name, "", "", shisanKbn)
    #ＤＢ項目はｗｋ変数へ格納してから使用する
    soloSu = int(solo_info[1])
    ikoUmu = int(solo_info[2])
    wkSoloSu = soloSu
    wkIkoUmu = ikoUmu
    #要件到達済みの場合は当該学生の処理をスキップする
    if wkSoloSu >= SOLO_YOKEN:
        return get_ecwArray(ECW_FUKA, gakuseiID, name, soloSu, ikoUmu, shisanKbn)
    if not gasshuku_list:
        return get_ecwArray(ECW_FUKA, gakuseiID, name, soloSu, ikoUmu, shisanKbn)

    #ソロ発数＝０の場合は次に予定している合宿でソロ１発出た想定とし、
    #その次の合宿から通常の計算を行う
    wkEcw = ECW_SEIJO
    startIx = 0
    if wkSoloSu == 0:
        nextIx = get_nextGasshuku(gasshuku_list, ymd)
        if nextIx < 0:
            return get_ecwArray(ECW_FUKA, gakuseiID, name, soloSu, ikoUmu, shisanKbn)
        wkEcw = ECW_SOLO0
        wkSoloSu = 1
        startIx = nextIx + 1

    #ソロ算出の対象日を求め、発数が要件に到達する合宿を特定する
    day_list = get_soloDays(gasshuku_list, ymd, startIx)
    tochakuIx = -1
    #２３移行有無＝１となる合宿の添字
    ikoIx = -1
    #２日に１回ソロに出る場合の経過日数
    wkNissu = 0
    for ix1 in range(len(day_list)):
        gasshukuIx = day_list[ix1][1]
        if wkIkoUmu == 0:
            #２３移行前：２日に１回ソロに出る
            wkNissu = wkNissu + 1
            if wkNissu < SOLO_PAIR:
                continue
            wkNissu = 0
            wkSoloSu = wkSoloSu + 1
        else:
            #２３移行後：標準試算は１日１発、最短試算は１日２発
            if str(shisanKbn) == "1":
                wkSoloSu = wkSoloSu + 2
            else:
                wkSoloSu = wkSoloSu + 1
        #１１発に到達した時点で２３移行有無を１とし、以降の計算方法を切り替える
        if wkIkoUmu == 0 and wkSoloSu >= SOLO_IKO:
            wkIkoUmu = 1
            wkNissu = 0
            ikoIx = gasshukuIx
        if wkSoloSu >= SOLO_YOKEN:
            tochakuIx = gasshukuIx
            break
    if tochakuIx < 0:
        #合宿日程が足りず要件到達見込みを算出できない
        return get_ecwArray(ECW_FUKA, gakuseiID, name, soloSu, ikoUmu, shisanKbn)
    #入所時期は要件到達見込みの次の合宿
    nyushoIx = tochakuIx + 1
    if nyushoIx >= len(gasshuku_list):
        return get_ecwArray(ECW_FUKA, gakuseiID, name, soloSu, ikoUmu, shisanKbn)

    tochakuName = gasshuku_list[tochakuIx][3]
    nyushoName = gasshuku_list[nyushoIx][3]
    #教官ＣＨＫは入所時期の合宿の１ヵ月前、学生ＣＨＫはその１ヵ月前
    kyokanChk = add_months(get_ym(gasshuku_list[nyushoIx][4]), -1)
    gakuseiChk = add_months(kyokanChk, -1)
    chukan_array = get_chukanChk(ikoUmu, ikoIx, gasshuku_list, gakuseiChk, ymd)

    ret_array = [wkEcw, gakuseiID, name, soloSu, ikoUmu, shisanKbn, tochakuName, nyushoName]
    ret_array = ret_array + chukan_array
    ret_array.append(gakuseiChk)
    ret_array.append(kyokanChk)
    return ret_array


def get_chukanChk(ikoUmu, ikoIx, gasshuku_list, gakuseiChk, ymd):
    """中間チェック①〜④をYYYYMMの配列で返す
       ①＝２３移行となる合宿の前々月　②＝同合宿の前月
       ③＝学生ＣＨＫの前々月　　　　　④＝学生ＣＨＫの前月
       処理開始時点で２３移行済みの場合、①②は処理年月を基準とする
       ①〜④が同月となる場合は④＞③＞②＞①の優先順で②①を前月へずらす"""
    if str(ikoUmu) == "1" or ikoIx < 0:
        #処理開始時点で２３移行済みのため処理年月を基準とする
        chukan1 = get_ym(ymd)
        chukan2 = get_ym(ymd)
    else:
        ikoYm = get_ym(gasshuku_list[ikoIx][4])
        chukan1 = add_months(ikoYm, -2)
        chukan2 = add_months(ikoYm, -1)
    chukan3 = add_months(gakuseiChk, -2)
    chukan4 = add_months(gakuseiChk, -1)
    #④③は再設定せず、②①の順に前月へずらして同月と順序逆転を解消する
    if chukan2 >= chukan3:
        chukan2 = add_months(chukan3, -1)
    if chukan1 >= chukan2:
        chukan1 = add_months(chukan2, -1)
    return [chukan1, chukan2, chukan3, chukan4]


def get_ecwArray(ecw, gakuseiID, name, soloSu, ikoUmu, shisanKbn):
    """試算不可時の戻り値1件分を編集する"""
    return [ecw, gakuseiID, name, soloSu, ikoUmu, shisanKbn, "", "", "", "", "", "", "", ""]


def get_gasshukuList():
    """合宿日程を取得する。未登録の年度は登録済みの最終年度と同じ日程で仮生成する
       名称は「年度-合宿名」、仮生成分は「（仮）年度-合宿名」に編集する
       戻り値：[[年度, 開始年月, 枝番, 名称, 開始年月日, 終了年月日, ソロ不可日数], ...]"""
    gasshuku_list = GK0S0B3D.get_gasshuku()
    if not gasshuku_list:
        return []
    #登録済みの最終年度を仮生成の基準とする
    maxNendo = gasshuku_list[0][0]
    for ix1 in range(len(gasshuku_list)):
        if gasshuku_list[ix1][0] > maxNendo:
            maxNendo = gasshuku_list[ix1][0]
    base_list = []
    for ix1 in range(len(gasshuku_list)):
        if gasshuku_list[ix1][0] == maxNendo:
            base_list.append(gasshuku_list[ix1])
    #仮生成は登録時の名称を基に編集するため、登録分の名称編集より先に行う
    kari_list = []
    for ix1 in range(1, KARI_NENDO + 1):
        for ix2 in range(len(base_list)):
            temp_array = list(base_list[ix2])
            kariNendo = str(int(base_list[ix2][0]) + ix1)
            temp_array[0] = kariNendo
            temp_array[1] = add_months(base_list[ix2][1], ix1 * 12)
            temp_array[3] = KARI_MARK + get_gasshukuName(kariNendo, base_list[ix2][3])
            temp_array[4] = add_years_ymd(base_list[ix2][4], ix1)
            temp_array[5] = add_years_ymd(base_list[ix2][5], ix1)
            kari_list.append(temp_array)
    for ix1 in range(len(gasshuku_list)):
        gasshuku_list[ix1][3] = get_gasshukuName(gasshuku_list[ix1][0], gasshuku_list[ix1][3])
    gasshuku_list = gasshuku_list + kari_list
    gasshuku_list.sort(key=lambda x: (x[4], x[2]))
    return gasshuku_list


def get_gasshukuName(nendo, name):
    return nendo + "-" + name


def get_nextGasshuku(gasshuku_list, ymd):
    for ix1 in range(len(gasshuku_list)):
        if gasshuku_list[ix1][4] > ymd:
            return ix1
    return -1


def get_soloDays(gasshuku_list, ymd, startIx):
    ret_array = []
    for ix1 in range(len(gasshuku_list)):
        if ix1 < startIx:
            continue
        startYmd = gasshuku_list[ix1][4]
        endYmd = gasshuku_list[ix1][5]
        fukaNissu = int(gasshuku_list[ix1][6])
        if endYmd <= ymd:
            continue
        #初日＋ソロ不可日数はソロの計算に含めない
        wkYmd = add_days(startYmd, 1 + fukaNissu)
        while wkYmd <= endYmd:
            if wkYmd > ymd:
                ret_array.append([wkYmd, ix1])
            wkYmd = add_days(wkYmd, 1)
    return ret_array


def get_shoriYmd():
    return datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d")

def get_ym(ymd):
    return ymd[0:6]

def add_days(ymd, days):
    dt = datetime.strptime(ymd, "%Y%m%d") + timedelta(days=days)
    return dt.strftime("%Y%m%d")

def add_months(ym, months):
    dt = datetime.strptime(ym + "01", "%Y%m%d") + relativedelta(months=months)
    return dt.strftime("%Y%m")

def add_years_ymd(ymd, years):
    dt = datetime.strptime(ymd, "%Y%m%d") + relativedelta(years=years)
    return dt.strftime("%Y%m%d")

def get_simTitle():
    return ["ECW", "氏名", "ソロ発数", "２３移行有無", "試算区分",
            "要件到達見込み", "入所時期", "中間ＣＨＫ①", "中間ＣＨＫ②",
            "中間ＣＨＫ③", "中間ＣＨＫ④", "学生ＣＨＫ", "教官ＣＨＫ"]

def get_simArray(sel_array):
    ret_array = []
    if not sel_array:
        return ret_array
    for ix1 in range(len(sel_array)):
        gakuseiID, _, shisanKbn = str(sel_array[ix1]).partition(",")
        if not gakuseiID or shisanKbn not in ["0", "1"]:
            continue
        #同一学生・同一区分の重複指定は1件にまとめる
        if [gakuseiID, shisanKbn] not in ret_array:
            ret_array.append([gakuseiID, shisanKbn])
    return ret_array

def edit_simResult(sim_result):
    ret_array = []
    if not sim_result:
        return ret_array
    for ix1 in range(len(sim_result)):
        info = sim_result[ix1]
        temp_array = [info[0], info[2], info[3],
                      get_ikoName(info[4]), get_kbnName(info[5]),
                      info[6], info[7]]
        #中間チェック①〜④、学生ＣＨＫ、教官ＣＨＫ
        for ix2 in range(8, 14):
            temp_array.append(get_ymDisp(info[ix2]))
        ret_array.append(temp_array)
    return ret_array

def get_csvArray(sim_result):
    ret_array = [get_simTitle()]
    return ret_array + edit_simResult(sim_result)

def get_ikoName(ikoUmu):
    if str(ikoUmu) == "1":
        return "済"
    if str(ikoUmu) == "0":
        return "-"
    return ikoUmu

def get_kbnName(shisanKbn):
    if str(shisanKbn) == "0":
        return "標準"
    if str(shisanKbn) == "1":
        return "最短"
    return shisanKbn

def get_ymDisp(ym):
    if ym and len(str(ym)) == 6:
        return str(ym)[0:4] + "/" + str(ym)[4:6]
    return ym
