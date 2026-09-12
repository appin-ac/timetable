import csv
import html
import json
import sys
from itertools import groupby
from pathlib import Path

### ファイルの置かれているフォルダをカレントディレクトリに
BASE_DIR = Path(__file__).resolve().parent
# 対象のフォルダパスを指定
folder_path = Path("../data")
# サブフォルダの Path オブジェクトのリストを取得
subfolders = [f.name for f in folder_path.iterdir() if f.is_dir()]
print(subfolders)

pd_html = ""


def get_pulldown():
    global pd_html
    pd_html += '<select onchange="if(this.value) location.href=this.value;">\n            <option value="">路線・駅を選択してください</option>'

    for station in subfolders:
        print("../data/" + station)
        folder_pathx = Path("../data/" + station)
        json_files = [
            f.stem for f in folder_pathx.iterdir() if f.suffix.lower()==".json"
        ]
        if len(json_files)==0:
            return
        with open(
            "../data/" + station + "/" + json_files[0] + ".json", "r", encoding="utf-8"
        ) as f:
            config = json.load(f)
        station_name = config.get("station_name", {})
        station_name_s = html.escape(str(station_name))
        line_name = config.get("line_name", {})
        line_name_s = html.escape(str(line_name))
        direction = config.get("direction", {})
        direction_main = direction.get("main", {})
        direction_main_s = html.escape(str(direction_main))
        direction_sub = direction.get("sub", {})
        direction_sub_s = html.escape(str(direction_sub))
        pd_html+='<option value="../' +station+ "/"+json_files[-1]+'.html">'
        pd_html+=(line_name_s+station_name_s+"（"+direction_sub_s+"）"+direction_main_s+"方面</option>\n")
    pd_html+="</select>\n"

### station の各年の時刻表をまとめて更新
def write_page(station):
    # csv読み込み
    folder_path1 = Path("../data/" + station)
    excel_files = [
        f.stem for f in folder_path1.iterdir() if f.suffix.lower() in [".csv"]
    ]
    # print(excel_files)
    # テンプレート読み込み
    with open("template.html", "r", encoding="utf-8") as f:
        template = f.read()
    pulldown = '<div style="text-align: center;">\n<select onchange="if(this.value) location.href=this.value;">\n<option value="">他の年の時刻表を見る</option>\n'

    # プルダウン作成
    for csv_file in excel_files:
        pulldown += (
            '<option value="../miyazaki_a/'
            + csv_file
            + '.html">'
            + csv_file
            + "</option>\n"
        )

    pulldown += "</select>\n　\n</div>"

    # 時刻表作成
    for year in excel_files:

        html_codes = get_head(station, year) + pulldown + get_table(station, year)

        final_html = template.format(insert=html_codes, station_pulldown=pd_html)

        # フォルダが存在しない場合のみ作成
        doc_path = Path("../docs/" + station)
        doc_path.mkdir(parents=True, exist_ok=True)

        # ファイルへの書き出し（encoding="utf-8" を必ず指定）
        with open(
            "../docs/" + station + "/" + year + ".html", "w", encoding="utf-8"
        ) as f:
            f.write(final_html)


def get_head(station, year):
    ### json（メタデータ）の読み込み
    with open(f"../data/{station}/{year}.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    line_name = config.get("line_name", {})
    line_name_s = html.escape(str(line_name))

    station_name = config.get("station_name", {})
    station_name_s = html.escape(str(station_name))
    revision_date = config.get("revision_date", {})
    revision_date_s = html.escape(str(revision_date))

    head_codes = f'<div style="text-align: center;"><p><b>{line_name_s}　{station_name_s}　時刻表</b><br>{revision_date_s}改正</p></div>\n'

    return head_codes


def get_table(station, year):
    ### json（メタデータ）の読み込み
    with open(f"../data/{station}/{year}.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    ### CSVの読み込み
    # Excelで書くとBOMがつくから -sig をつける
    with open(f"../data/{station}/{year}.csv", "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        # groupbyを使うために hour でソート状態を保証（通常は整列済み）
        rows = list(reader)

    # 時刻表のタイトルなど
    direction = config.get("direction", {})
    direction_main = direction.get("main", {})
    direction_main_s = html.escape(str(direction_main))

    ### HTML 生成
    table_codes = f'<table class="timetable"> <thead><tr><th>時</th><th>{direction_main_s}</th></tr></thead>'

    # hour ごとにグループ化
    for hour, group in groupby(rows, key=lambda x: x["hour"]):
        table_codes += (
            f'  <tr>\n    <td class="hour">{hour}</td>\n    <td class="minutes">\n'
        )
        for t in group:
            type_span = f'<span class="type">{t["type"]}</span>'
            # if t["type"] else ""
            dest_span = f'<span class="dest">{t["dest"]}{t["rem"]}</span>'
            # if t["dest"] else ""
            table_codes += f'<span class="time-item {t["color"]}"><span class="num">{str(t["minute"]).zfill(2)}</span><span class="labels">{type_span}{dest_span}</span></span>\n'
        table_codes += "    </td>\n  </tr>\n"

    table_codes += "</table></body></html>"

    return table_codes


### main ###

get_pulldown()

for station in subfolders:
    write_page(station)
