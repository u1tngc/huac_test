
#PGM-ID:GK0S0201
#PGM-NAME:GK擬似谷口AI連携メイン
#最終更新日:2026/02/04


import GK1S0202
import GK1S0203
import GK1S0A1D


def get_taniguchiAll(id):
    ret_array = GK1S0A1D.get_taniguchi(id)
    return ret_array


def get_ai_main(id,bunya,question):
    if bunya == "汎用":
        answer, err = GK1S0203.get_ai_main(id,bunya,question)
        pass
    else:
        answer, err = GK1S0202.get_ai_main(id,bunya,question)
    if err == 1:
        err = "擬似谷口は忙しいので後にしてください。"
        return "", err
    else:
        return answer, ""
    

def insert_taniguchi(id, kbn,bunya, kaiwa):
    ret_cd = GK1S0A1D.insert_taniguchi(id, kbn, bunya, kaiwa)
    return ret_cd