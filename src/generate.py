import csv
import html
import json
from itertools import groupby
from pathlib import Path

### ファイルの置かれているフォルダをカレントディレクトリに
BASE_DIR = Path(__file__).resolve().parent


### main ###
def main():

    # 対象のフォルダパスを指定
    folder_path = Path("../data")
    # サブフォルダの Path オブジェクトのリストを取得
    subfolders = [f.name for f in folder_path.iterdir() if f.is_dir()]

    index_info = {}
    for station in subfolders:
        folder_pathx = Path("../data/") / station
        json_files = [
            f.stem for f in folder_pathx.iterdir() if f.suffix.lower() == ".json"
        ]
        if len(json_files) == 0:
            return
        station_dict_list = {}
        for year in json_files:
            dict = {}
            with open(
                Path("../data/") / station / f"{year}.json", "r", encoding="utf-8"
            ) as f:
                config = json.load(f)

                dict["line_name"] = html.escape(config.get("line_name", ""))

                dict["station_name"] = html.escape(config.get("station_name", ""))

                direction = config.get("direction", {})
                dict["direction_main"] = html.escape(direction.get("main", ""))
                dict["direction_sub"] = html.escape(direction.get("sub", ""))

                dict["revision_date"] = html.escape(config.get("revision_date", ""))

                ledgends_j = config.get("ledgends", {})
                # print(ledgends_j)
                ledgends_dict = {}
                ## escapeしてない
                for k, v in ledgends_j.items():
                    ledgends_dict[k] = v
                dict["ledgends"] = ledgends_dict

            station_dict_list[year] = dict
        index_info[station] = station_dict_list

    pd_sta = get_station_pulldown(index_info)

    # index ページ書き込み
    with open("./template_index.html", "r", encoding="utf-8") as f:
        index_page = f.read()

    print(get_station_pulldown(index_info,0))
    index_page_new = index_page.format(pulldown_main=get_station_pulldown(index_info,0))
    
    with open("../docs/index.html", "w", encoding="utf-8") as f:
        f.write(index_page_new)


    # 駅ごとに時刻表を更新
    for station in subfolders:
        write_page(station, pd_sta, index_info[station])

    # print(index_info)


def get_station_pulldown(index_info, depth=1):

    pd_html = '<select onchange="if(this.value) location.href=this.value;">\n<option value="">路線・駅を選択してください</option>\n'

    for station in index_info:

        print("../data/" + station)

        latest_year = next(reversed(index_info[station]))

        dict = index_info[station][latest_year]

        # print(dict)
        pd_html += (
            '<option value="'
            + "." * depth
            + "./"
            + station
            + "/"
            + latest_year
            + '.html">'
        )

        pd_html += dict["line_name"] + " " + dict["station_name"] + " "
        pd_html += dict["direction_main"]
        if dict["direction_sub"] != "":
            pd_html += "（" + dict["direction_sub"] + "）"
        pd_html += "</option>\n"
    pd_html += "</select>\n"
    return pd_html


### station の各年の時刻表をまとめて更新
def write_page(station, pd_sta, dict_station):
    # csv読み込み
    folder_path1 = Path("../data") / station
    excel_files = [
        f.stem for f in folder_path1.iterdir() if f.suffix.lower() in [".csv"]
    ]
    # print(excel_files)
    
    # テンプレート読み込み
    with open("template.html", "r", encoding="utf-8") as f:
        template = f.read()
    pd_year = '<div style="text-align: center;">\n<select onchange="if(this.value) location.href=this.value;">\n<option value="">他の年の時刻表を見る</option>\n'

    # 年選択プルダウン作成
    for csv_file in excel_files:
        pd_year += (
            '<option value="../'
            + station
            + "/"
            + csv_file
            + '.html">'
            + csv_file
            + "</option>\n"
        )

    pd_year += "</select>\n<br></div>"

    # 時刻表作成
    for year in excel_files:

        html_codes = (
            get_head(station, year, dict_station[year])
            + pd_year
            + get_table(station, year, dict_station[year])
        )

        final_html = template.format(insert=html_codes, station_pulldown=pd_sta)

        # フォルダが存在しない場合のみ作成
        doc_path = Path("../docs/" + station)
        doc_path.mkdir(parents=True, exist_ok=True)

        # ファイルへの書き出し（encoding="utf-8" を必ず指定）
        with open(
            Path("../docs") / station / f"{year}.html", "w", encoding="utf-8"
        ) as f:
            f.write(final_html)


def get_head(station, year, dict):
    head_codes = (
        '<div style="text-align: center;"><p><b>'
        + dict["line_name"]
        + "　"
        + dict["station_name"]
        + "　時刻表</b><br>"
        + dict["revision_date"]
        + "改正</p></div>\n"
    )

    return head_codes


def get_table(station, year, dict):
    ### json（メタデータ）の読み込み
    with open(f"../data/{station}/{year}.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    ### CSVの読み込み
    # Excelで書くとBOMがつくから -sig をつける
    with open(f"../data/{station}/{year}.csv", "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        # groupbyを使うために hour でソート状態を保証（通常は整列済み）
        rows = list(reader)

    ### HTML 生成
    table_codes = (
        '<table class="timetable"><thead><tr><th>時</th><th>'
        + dict["direction_main"]
        + "</th></tr></thead>"
    )

    # hour ごとにグループ化
    for hour, group in groupby(rows, key=lambda x: x["hour"]):
        table_codes += f'<tr>\n<td class="hour">{hour}</td>\n<td class="minutes">\n'
        for t in group:
            type_span = f'<span class="type">{t["type"]}</span>'
            # if t["type"] else ""
            dest_span = f'<span class="dest">{t["dest"]}{t["rem"]}</span>'
            # if t["dest"] else ""
            table_codes += f'<span class="time-item {t["color"]}"><span class="num">{str(t["minute"]).zfill(2)}</span><span class="labels">{type_span}{dest_span}</span></span>'
        table_codes += "</td></tr>\n"
    table_codes += '<tr><td colspan="2">\n'  # <b>【凡例】</b><br>
    if "ledgends" in dict.keys():
        # print(dict["ledgends"])
        table_codes += (
            '<table class="legends"><thead><tr><th>備考</th><tr></thead><tbody>\n'
        )
        for k, v in dict["ledgends"].items():
            table_codes += "<tr><td>" + k + "</td><td>" + v + "</td></tr>\n"
        table_codes += "</tbody></table></td></tr>"

    table_codes += "</table>"

    return table_codes


if __name__ == "__main__":
    main()
