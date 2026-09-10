import csv
import html
import json
import sys
from itertools import groupby

### フォルダーの名前を受け取る

# print("folder name:")
# folder_name = sys.argv[1]

def write_page(station,year):
    ### json（メタデータ）の読み込み
    with open(f"../data/{station}/{year}.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    ### CSVの読み込み
    # Excelで書くとBOMがつくから -sig をつける
    with open(f"../data/{station}/{year}.csv", "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        # groupbyを使うために hour でソート状態を保証（通常は整列済み）
        rows = list(reader)

    with open("template.html", "r", encoding="utf-8") as f:
        template = f.read()

    line_name = config.get("line_name", {})
    line_name_s = html.escape(str(line_name))

    station_name = config.get("station_name", {})
    station_name_s = html.escape(str(station_name))

    direction = config.get("direction", {})
    direction_main= direction.get("main",{})
    direction_main_s = html.escape(str(direction_main))

    revision_date = config.get("revision_date", {})
    revision_date_s = html.escape(str(revision_date))

    ### HTML 生成
    html_codes = f'<div style="text-align: center;"><p><b>{line_name_s}　{station_name_s}　時刻表</b><br>{revision_date_s}改正</p></div>\n'

    html_codes +='<div style="text-align: center;">\n<select onchange="if(this.value) location.href=this.value;">\n<option value="">他の年の時刻表を見る</option>\n<option value="../miyazaki_a/2026.html">2026</option>\n<option value="../miyazaki_a/2025.html">2025</option><option value="../miyazaki_a/2024.html">2024</option><option value="../miyazaki_a/2022.html">2022</option><option value="../miyazaki_a/2020.html">2020</option><option value="../miyazaki_a/2019.html">2019</option><option value="../miyazaki_a/2016.html">2016</option></select>\n　\n</div>'

    html_codes += f'<table class="timetable"> <thead><tr><th>時</th><th>{direction_main_s}</th></tr></thead>'

    # hour ごとにグループ化
    for hour, group in groupby(rows, key=lambda x: x["hour"]):
        html_codes += f'  <tr>\n    <td class="hour">{hour}</td>\n    <td class="minutes">\n'
        for t in group:
            type_span = f'<span class="type">{t["type"]}</span>'
            # if t["type"] else ""
            dest_span = f'<span class="dest">{t["dest"]}{t["rem"]}</span>'
            # if t["dest"] else ""
            html_codes += f'      <span class="time-item {t["color"]}"><span class="num">{str(t["minute"]).zfill(2)}</span><span class="labels">{type_span}{dest_span}</span></span>\n'
        html_codes += "    </td>\n  </tr>\n"

    html_codes += "</table></body></html>"

    final_html = template.format(insert=html_codes)

    # ファイルへの書き出し（encoding="utf-8" を必ず指定）
    with open(f"../docs/{station}/{year}.html", "w", encoding="utf-8") as f:
        f.write(final_html)

page_list=['2016','2019','2020','2022','2024','2025','2026']

for i in page_list:
    write_page("miyazaki_a",i)