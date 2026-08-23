import csv
import html
import json
import sys
from itertools import groupby

### フォルダーの名前を受け取る

# print("folder name:")
folder_name = sys.argv[1]

### json（メタデータ）の読み込み
with open(f"{folder_name}/{folder_name}.json", "r", encoding="utf-8") as f:
    config = json.load(f)

### CSVの読み込み

# Excelで書くとBOMがつくから -sig をつける
with open(f"{folder_name}/{folder_name}.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    # groupbyを使うために hour でソート状態を保証（通常は整列済み）
    rows = list(reader)

with open("template.html", "r", encoding="utf-8") as f:
    template = f.read()

line_name = config.get("line_name", {})
line_name_s = html.escape(str(line_name))

station_name = config.get("station_name", {})
station_name_s = html.escape(str(station_name))

revision_date = config.get("revision_date", {})
revision_date_s = html.escape(str(revision_date))

### HTML 生成
html = f'<div style="text-align: center;"><p><b>{line_name_s}　{station_name_s}　時刻表</b><br>{revision_date_s}改正</p></div>\n'

html += '<table class="timetable"> <thead><tr><th>時</th><th></th></tr></thead>'

# hour ごとにグループ化
for hour, group in groupby(rows, key=lambda x: x["hour"]):
    html += f'  <tr>\n    <td class="hour">{hour}</td>\n    <td class="minutes">\n'
    for t in group:
        type_span = f'<span class="type">{t["type"]}</span>'
        # if t["type"] else ""
        dest_span = f'<span class="dest">{t["dest"]}{t["rem"]}</span>'
        # if t["dest"] else ""
        html += f'      <span class="time-item {t["color"]}"><span class="num">{str(t["minute"]).zfill(2)}</span><span class="labels">{type_span}{dest_span}</span></span>\n'
    html += "    </td>\n  </tr>\n"

html += "</table></body></html>"

final_html = template.format(insert=html)

# ファイルへの書き出し（encoding="utf-8" を必ず指定）
with open(f"{folder_name}/index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("index.html を出力しました。")
