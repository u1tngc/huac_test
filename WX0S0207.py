#PGM-ID:WX0S0207
#PGM-NAME:[P]WX_METAR/TAFテーブル

import re

import PK0S0100

def get_location(inp_location):
    airport_list = {
        "RJAA": "成田国際空港",
        "RJAF": "松本空港",
        "RJAH": "百里飛行場(茨城空港)",
        "RJAM": "南鳥島飛行場",
        "RJBB": "関西国際空港",
        "RJBD": "南紀白浜空港",
        "RJBE": "神戸空港",
        "RJBT": "但馬空港",
        "RJCC": "新千歳空港",
        "RJCH": "函館空港",
        "RJCK": "釧路空港",
        "RJCM": "女満別空港",
        "RJCO": "丘珠空港",
        "RJEB": "紋別空港",
        "RJEC": "旭川空港",
        "RJEO": "奥尻空港",
        "RJER": "利尻空港",
        "RJFC": "屋久島空港",
        "RJFE": "福江空港",
        "RJFF": "福岡空港",
        "RJFG": "種子島空港",
        "RJFK": "鹿児島空港",
        "RJFM": "宮崎空港",
        "RJFO": "大分空港",
        "RJFR": "北九州空港",
        "RJFS": "佐賀空港",
        "RJFT": "熊本空港",
        "RJFU": "長崎空港",
        "RJGG": "中部国際空港(セントレア)",
        "RJKA": "奄美空港",
        "RJKN": "徳之島空港",
        "RJNA": "名古屋空港",
        "RJNF": "福井空港",
        "RJNG": "岐阜飛行場",
        "RJNK": "小松空港",
        "RJNS": "静岡空港",
        "RJNT": "富山空港",
        "RJNY": "静浜飛行場",
        "RJOA": "広島空港",
        "RJOB": "岡山空港",
        "RJOC": "出雲空港",
        "RJOH": "美保飛行場(米子空港)",
        "RJOI": "岩国空港(米軍)",
        "RJOK": "高知空港",
        "RJOM": "松山空港",
        "RJOO": "大阪国際空港(伊丹空港)",
        "RJOR": "鳥取空港",
        "RJOS": "徳島空港",
        "RJOT": "高松空港",
        "RJOW": "山口宇部空港",
        "RJOW": "石見空港",
        "RJOY": "八尾飛行場",
        "RJSA": "青森空港",
        "RJSC": "山形空港",
        "RJSD": "佐渡空港",
        "RJSF": "福島空港",
        "RJSH": "八戸航空基地",
        "RJSI": "花巻空港",
        "RJSM": "三沢飛行場",
        "RJSN": "新潟空港",
        "RJSS": "仙台空港",
        "RJSY": "庄内空港",
        "RJTA": "厚木飛行場",
        "RJTF": "調布飛行場",
        "RJTI": "東京ヘリポート",
        "RJTJ": "入間飛行場",
        "RJTK": "木更津飛行場",
        "RJTQ": "三宅島空港",
        "RJTR": "キャンプ座間(米軍)",
        "RJTS": "相馬原飛行場",
        "RJTT": "東京国際空港(羽田空港)",
        "RJTU": "宇都宮飛行場",
        "RJTY": "横田飛行場(米軍)",
        "ROAH": "那覇空港",
        "RODN": "嘉手納飛行場(米軍)",
        "ROIG": "新石垣空港",
        "ROKR": "慶良間空港",
        "ROMD": "南大東空港",
        "RORK": "北大東空港",
        "RORS": "下地島空港",
        "ROTM": "普天間飛行場(米軍)",
        "ROYN": "与那国空港",
        "EGLL": "ヒースロー空港(United Kingdom)",
        "LTBA": "アタテュルク国際空港(Turkey)",
        "OAKB": "カブール国際空港(Afganistan)",
        "OEJN": "キング・アブドゥルアズィール国際空港(Saudi Arabia)",
        "OEMA": "Prince Mohammad bin Abdulaziz Airport(Saudi Arabia)",
        "OERK": "キング・ハーリド国際空港(Saudi Arabia)",
        "OIFM": "シャヒード・ベヘシュティー国際空港(Iran)",
        "OIIE": "エマーム・ホメイニー国際空港(Iran)",
        "OMDB": "ドバイ国際空港(U.A.E.)",
        "OPIS": "イスラマバード国際空港(Pakistan)",
        "OPKC": "ジンナー国際空港(Pakistan)",
        "OPLA": "アッラーマ・イクバール国際空港(Pakistan)",
        "OPPS": "バシャ・カーン国際空港(Pakistan)",
        "RKSI": "仁川国際空港(Korea)",
        "RKSS": "金浦国際空港(Korea)",
        "VABB": "チャトラパティ・シヴァージー国際空港(India)",
        "VIDP": "インディラ・ガンディー国際空港(India)",
        "VTBS": "スワンナプーム国際空港(Thailand)",
        "VTCC": "チェンマイ国際空港(Thailand)",
        "WIII": "スカルノ・ハッタ国際空港(Indonesia)",
        "WMKJ": "スルタン・イスマイル空港(Malaysia)",
        "WMKK": "クアラルンプール国際空港(Malaysia)",
        "WSSS": "チャンギ国際空港(Singapore)"
    }
    if inp_location in airport_list:
        ret_location = airport_list[inp_location]
    else:
        ret_location = "不明（プログラムに登録なし）"
    return ret_location

def get_cloudInfo(cloud_amount, cloud_base, cloud_kind, cloud_num):
    cloud_nnn = ['FEW','SCT','BKN','OVC', '///']
    cloud_mean = ['1/8～2/8の雲','3/8～4/8の雲','5/8～7/8の雲','全天を覆う雲', '不明']
    cloudInfo_mean = ""
    for ix1 in range(len(cloud_nnn)):
        if cloud_amount == cloud_nnn[ix1]:
            cloudInfo_mean = cloud_mean[ix1]
    if cloud_base == '///':
        cloudInfo_base = '不明'
    else:
        cloudInfo_base = str(int(cloud_base)) + '00ft'
        cloud_bft = int(cloud_base) * 100
        cloud_bm = PK0S0100.ft_to_m(cloud_bft)
    if cloud_kind == '':
        if cloud_base == '///':
            cloudInfo = '雲情報' + str(cloud_num) + ' ：雲量' + str(cloudInfo_mean) + ' 雲底不明'
        else:
            cloudInfo = '雲情報' + str(cloud_num) + ' ：雲量' + str(cloudInfo_mean) + ' 雲底' + cloudInfo_base + '（' + str(cloud_bm) + 'm）'
    else:
        if cloud_kind == 'CB':
            cloudInfo_kind = '(積乱雲)'
        elif cloud_kind == 'CU':
            cloudInfo_kind = '(積雲)'
        elif cloud_kind == 'TCU':
            cloudInfo_kind = '(塔状積雲)'
        elif cloud_kind == '///':
            cloudInfo_kind = '(雲形不明)'
        if cloud_base == '///':
            cloudInfo = '雲情報' + str(cloud_num) + ' ：雲量' + cloudInfo_mean + cloudInfo_kind + ' 雲底不明'
        else:
            cloudInfo = '雲情報' + str(cloud_num) + ' ：雲量' + cloudInfo_mean + cloudInfo_kind + ' 雲底' + cloudInfo_base + '（' + str(cloud_bm) + 'm）'
    return cloudInfo

def get_wx1(wx, kino_flg):
    ix_wx = 0
    eof_wx = 0
    wx_info = []
    retCd = 0
    wx_kigo = ['DZ','RA','SN','SG','PL','GR','GS','BR','FG','FU','VA','DU','SA','HZ','PO','SQ','FC','SS','DS','TS','RE']
    wx_jp = ['霧雨','雨','雪','霧雪','凍雨','雹','あられ','もや','霧','煙','火山灰','塵','砂','煙霧','塵旋風','スコール','ろうと雲','砂塵嵐(sand)','砂塵嵐(dust)', '雷','(運航上重要な気象)']
    wx_with = ['VC','MI','BC','PR','DR','BL','SH','TS','FZ','DZ','RA','SN','SG','PL','GR','GS','BR','FG','FU','VA','DU','SA','HZ','PO','SQ','FC','SS','DS']
    wx_withJp = ['周囲で','地','散在','部分','低い','高い','驟雨性の','雷','着氷性','霧雨','雨','雪','霧雪','凍雨','雹','あられ','もや','霧','煙','火山灰','塵','砂','煙霧','塵旋風','スコール','ろうと雲','砂塵嵐(sand)','砂塵嵐(dust)']    
    if kino_flg == 1:
        for ix1 in range(len(wx_kigo)):
            if wx == wx_kigo[ix1]:
                wx_info.append(wx_kigo[ix1])
                wx_info.append(wx_jp[ix1])
                retCd = 1
    elif kino_flg == 2:
        if wx == "VCSH":
            wx_kigo_x = "VCSH"
            wx_kigoJp_x = "周囲で降水現象(種類と強度は不明)"
            retCd = 1
        else:
            wx_kigo_x = ""
            wx_kigoJp_x = ""
            ix_wx = 0
            while eof_wx == 0:
                if wx[ix_wx:ix_wx + 4] == "SNRA" or wx[ix_wx:ix_wx + 4] == "RASN":
                    wx_kigo_x =  wx_kigo_x + wx[ix_wx:ix_wx + 4]
                    wx_kigoJp_x = wx_kigoJp_x + "みぞれ"
                    ix_wx = ix_wx + 2
                    retCd = 1
                else:
                    for ix1 in range(len(wx_with)):
                        if wx[ix_wx:ix_wx + 2] == wx_with[ix1]:
                            wx_kigo_x = wx_kigo_x + wx_with[ix1]
                            wx_kigoJp_x = wx_kigoJp_x + wx_withJp[ix1] 
                            retCd = 1
                if len(wx) <= ix_wx + 2:
                    eof_wx = 1
                ix_wx = ix_wx + 2
        if re.search("SNRA", wx_kigo_x):
            wx_kigoJp_x = f"{wx_kigoJp_x}(雪が強いみぞれ)"
        elif re.search("RASN", wx_kigo_x):
            wx_kigoJp_x = f"{wx_kigoJp_x}(雨が強いみぞれ)"
        wx_info.append(wx_kigo_x)
        wx_info.append(wx_kigoJp_x)
    elif kino_flg == 3:
        rmkWx_info = []
        for ix1 in range(len(wx_kigo)):
            if wx == wx_kigo[ix1]:
                rmkWx_info.append(wx_kigo[ix1])
                rmkWx_info.append(wx_jp[ix1])
                return rmkWx_info
    return wx_info, retCd

def check_wx(wx_num, wx):
    """
    retCd = 1 天気
    retCd = 2 記号あり
    """
    retCd = 0
    wx_modify = ''
    if wx[0:1] == '-':
        wx_modify = '弱い'
        retCd = 1
        wx_x = wx[1:]
    elif wx[0:1] == '+':
        wx_modify = '強い'
        retCd = 1
        wx_x = wx[1:]
    else:
        wx_x = wx
    wx_info, retCd =  get_wx1(wx_x, 2)

    if retCd != 0:
        if wx_modify == '':
            wxInfo = '天気 ' + str(wx_num) +'  ：' + wx_info[1]
        else:
            wxInfo = '天気 ' + str(wx_num) +'  ：' + wx_modify + wx_info[1]
        return wxInfo, retCd
    else:
        return "", retCd
    
def check_rmkWx(metarInfo_x):
    rmkWx_flg = 0
    if metarInfo_x[0:3] != "RWY":
        try: #天気2文字
            dummy = int(metarInfo_x[3:4])
            if metarInfo_x[2:3] == 'B' or metarInfo_x[2:3] == 'E':
                dummy, rmkwx_retcd = get_wx1(metarInfo_x[0:2], 1)
                if rmkwx_retcd == 1:
                        rmkWx_flg = 1
        except ValueError: #天気4文字
            try:
                dummy = int(metarInfo_x[5:6])
                if metarInfo_x[4:5] == 'B' or metarInfo_x[4:5] == 'E':
                    dummy, rmkwx_retcd = get_wx1(metarInfo_x[0:4], 2)
                    if rmkwx_retcd == 1:
                        rmkWx_flg = 1
            except ValueError:
                rmkWx_flg = 0
    return rmkWx_flg

def get_aircraft(inp_aircraft):
    aircraft_list = {
        "A19N": "A319neo",
        "A20N": "A320neo",
        "A21N": "A321neo",
        "A306": "A300-600",
        "A30B": "A300B2/A300B4/A300C4",
        "A310": "A310-200",
        "A318": "A318",
        "A319": "A319",
        "A320": "A320",
        "A321": "A321",
        "A332": "A330-200",
        "A333": "A330-300",
        "A337": "A330-700",
        "A338": "A330-800",
        "A339": "A330-900",
        "A342": "A340-200",
        "A343": "A340-300",
        "A345": "A340-500",
        "A346": "A340-600",
        "A359": "A350-900",
        "A35K": "A350-1000",
        "A388": "A380-800",
        "AT43": "ATR 42-300/320",
        "AT45": "ATR 42-500",
        "AT46": "ATR 42-600",
        "AT72": "ATR 72-201/202",
        "AT73": "ATR 72-211/212",
        "AT75": "ATR 72-212A(500)",
        "AT76": "ATR 72-212A(600)",
        "B37M": "B737 MAX 7",
        "B38M": "B737 MAX 8",
        "B39M": "B737 MAX 9",
        "B3XM": "B737 MAX 10",
        "B703": "B707",
        "B712": "B717",
        "B720": "B720B",
        "B721": "B727-100",
        "B722": "B727-200",
        "B732": "B737-200",
        "B733": "B737-300",
        "B734": "B737-400",
        "B735": "B737-500",
        "B736": "B737-600",
        "B737": "B737-700/700ER",
        "B738": "B737-800",
        "B739": "B737-900/900ER",
        "B741": "B747-100",
        "B742": "B747-200",
        "B743": "B747-300",
        "B744": "B747-400/400ER",
        "B748": "B747-8I",
        "B74R": "B747SR",
        "B74S": "B747SP",
        "B752": "B757-200",
        "B753": "B757-300",
        "B762": "B767-200/200ER",
        "B763": "B767-300",
        "B764": "B767-400ER",
        "B772": "B777-200/200ER",
        "B773": "B777-300",
        "B778": "B777-8",
        "B779": "B777-9",
        "B77L": "B777-200LR",
        "B77W": "B777-300ER",
        "B788": "B787-8",
        "B789": "B787-9",
        "B78X": "B787-10",
        "BCS1": "A220-100",
        "BCS3": "A220-300",
        "BLCF": "B747-400 LCF Dreamlifter",
        "DH8A": "DHC8-100",
        "DH8B": "DHC8-200",
        "DH8C": "DHC8-300",
        "DH8D": "DHC8-400",
        "DHC5": "DHC5 Buffalo",
        "DHC6": "DHC6 Twin Otter",
        "DHC7": "DHC-7 Dash 7",
        "E110": "エンブラルEMB 110 Bandeirante",
        "E120": "エンブラルEMB 120 Brasilia",
        "E135": "エンブラルRJ135",
        "E145": "エンブラルRJ145",
        "E170": "E170",
        "E190": "E190",
        "E195": "E195",
        "E290": "E190-E2",
        "E295": "E195-E2",
        "E35L": "エンブラルLegacy 600/Legacy 650",
        "E50P": "エンブラルPhenom 100",
        "E545": "エンブラルLegacy 450/Praetor 500",
        "E550": "エンブラルLegacy 500/Praetor 600",
        "E55P": "エンブラルPhenom 300",
        "E75L": "E175(long wing)",
        "E75S": "E175(short wing)",
        "G159": "Gulfstream Aerospace G-159 Gulfstream I",
        "G280": "Gulfstream G280",
        "GA7C": "Gulfstream G700",
        "GL5T": "ボンバルディアBD-700 Global 5000",
        "GLEX": "ボンバルディアGlobal Express / Raytheon Sentinel",
        "GLF4": "Gulfstream IV",
        "GLF5": "Gulfstream V",
        "GLF6": "Gulfstream G650",
        "HDJT": "Honda HA-420",
        "I114": "Ilyushin Il-114",
        "IL18": "Ilyushin Il-18",
        "IL62": "Ilyushin Il-62",
        "IL76": "Ilyushin Il-76",
        "IL86": "Ilyushin Il-86",
        "IL96": "Ilyushin Il-96",
        "J328": "Fairchild Dornier 328JET",
        "K35R": "Boeing KC-135 Stratotanker",
        "L101": "Lockheed L-1011 Tristar",
        "L188": "Lockheed L-188 Electra",
        "MD11": "McDonnell Douglas MD-11",
        "MD81": "McDonnell Douglas MD-81",
        "MD82": "McDonnell Douglas MD-82",
        "MD83": "McDonnell Douglas MD-83",
        "MD87": "McDonnell Douglas MD-87",
        "MD88": "McDonnell Douglas MD-88",
        "MD90": "McDonnell Douglas MD-90",
        "MU2": "三菱 Mu-2",
    }
    if inp_aircraft in aircraft_list:
        ret_aircraft  = aircraft_list[inp_aircraft]
    else:
        ret_aircraft = "不明"
    return ret_aircraft