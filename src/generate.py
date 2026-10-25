import csv
import html
import json
from itertools import groupby
from pathlib import Path
import markdown
from jinja2 import Environment, FileSystemLoader
from datetime import date

### ファイルの置かれているフォルダをカレントディレクトリに
BASE_DIR = Path(__file__).resolve().parent


ROOT = BASE_DIR.parent
ARTICLES_DIR = ROOT / "articles"
OUTPUT_DIR = ROOT / "docs" / "blog"
env = Environment(
    loader=FileSystemLoader(ROOT/"src"),
    autoescape=True,
)

article_template = env.get_template("article.html")
index_template = env.get_template("template_index.html")

### main ###
def main():

    # 対象のフォルダパスを指定
    folder_path = Path("../data")
    # サブフォルダの Path オブジェクトのリストを取得
    subfolders = [f.name for f in folder_path.iterdir() if f.is_dir()]
    print(subfolders)

    # 時刻表ファイルのデータをリストに格納
    index_info = {}
    correct_data_files(subfolders,index_info)

    pd_sta = get_station_pulldown(index_info)

    # index ページ書き込み
    with open("./template_index.html", "r", encoding="utf-8") as f:
        index_page = f.read()

    print(get_station_pulldown(index_info,0))

    
    # with open("../docs/index.html", "w", encoding="utf-8") as f:
    #     f.write(index_page_new)

    # 駅ごとに時刻表を更新
    for station in subfolders:
        print(station)
        write_page(station, pd_sta, index_info[station])



    # ブログ+infrx更新
    blog_update(get_station_pulldown(index_info,0))


def correct_data_files(subfolders,index_info):
    for station in subfolders:
        folder_pathx = Path("../data/") / station
        json_files = [
            f.stem for f in folder_pathx.iterdir() if f.suffix.lower() == ".json"
        ]
        print(folder_pathx)
        print(json_files)
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
                for k, v in ledgends_j.items():
                    ledgends_dict[k] = html.escape(v)
                dict["ledgends"] = ledgends_dict

            station_dict_list[year] = dict
        index_info[station] = station_dict_list


def get_station_pulldown(index_info, depth=1):

    # pd_html = '<select onchange="if(this.value) location.href=this.value;">\n<option value="">路線・駅を選択してください</option>\n'
    pd_html = "<table class=\"sta_link_list\"><tr><th>路線</th><th>駅</th></tr>\n"#"<b>掲載駅リスト</b>\n" 
    line_dict={}
    for station in index_info:

        print("../data/" + station)

        latest_year = next(reversed(index_info[station]))

        dict = index_info[station][latest_year]

        # pd_html += (
        #     '<option value="'
        #     + "." * depth
        #     + "./"
        #     + station
        #     + "/"
        #     + latest_year
        #     + '.html">'
        # )
        
        # # 日豊本線 宮崎駅
        # page_title = dict["line_name"] + " " + dict["station_name"] + " "
        
        # # 延岡・佐伯方面
        # page_title += dict["direction_main"]

        # # （下り）
        # if dict["direction_sub"] != "":
        #     page_title += "（" + dict["direction_sub"] + "）"
        
        # pd_html += page_title+"</option>\n"

        page_link =  (
            '<a href="'
            + "." * depth + "./" + station + "/" + latest_year  + '.html">'
            + dict["station_name"] + " "
            + ("（" + dict["direction_sub"] + "）" if dict["direction_sub"] != "" else "")
            + dict["direction_main"]
            + "</a><br>\n"
        )

        line_dict.setdefault(dict["line_name"],[]).append(page_link)

    print(line_dict)

    # pd_html += "</select><br><br>\n"

    for k,v in line_dict.items():
        pd_html += ("<tr><td>"+k+"</td>\n<td>")
        for x in v:
            pd_html += x
        pd_html +=("</td></tr>\n")
    pd_html += ("</table>\n")
    print(pd_html)

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
            type_span = f'<span class="type">{html.escape(t["type"])}</span>'
            # if t["type"] else ""
            dest_span = f'<span class="dest">{html.escape(t["dest"])}{html.escape(t["rem"])}</span>'
            # if t["dest"] else ""
            table_codes += f'<span class="time-item {t["color"]}"><span class="num">{str(html.escape(t["minute"])).zfill(2)}</span><span class="labels">{type_span}{dest_span}</span></span>'
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

def load_article(path):
    """Markdownファイルからメタデータと本文を読み込む。"""
    source = path.read_text(encoding="utf-8")

    if not source.startswith("---\n"):
        raise ValueError(f"フロントマターがありません: {path.name}")

    parts = source.split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"フロントマターが不正です: {path.name}")

    metadata = {}

    for line in parts[1].strip().splitlines():
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"メタデータが不正です: {line}")

        metadata[key.strip()] = value.strip()

    title = metadata.get("title")
    date_text = metadata.get("date")

    if not title or not date_text:
        raise ValueError(f"title と date は必須です: {path.name}")

    # 日付形式と実在する日付を検証する
    parsed_date = date.fromisoformat(date_text)
    date_text = parsed_date.isoformat()

    body_source = parts[2].strip()
    body = markdown.markdown(body_source)

    return {
        "title": title,
        "date": date_text,
        "parsed_date": parsed_date,
        "body": body,
        "url": f"{path.stem}.html",
        "url_x": f"./blog/{path.stem}.html",
        "filename": path.stem,
    }


def blog_update(pulldown_part):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    articles = []

    for path in sorted(ARTICLES_DIR.glob("*.md")):
        article = load_article(path)
        articles.append(article)

        html = article_template.render(
            title=article["title"],
            date=article["date"],
            body=article["body"],
        )

        output_path = OUTPUT_DIR / article["url"]
        output_path.write_text(html, encoding="utf-8")

        print(f"生成: {output_path.relative_to(ROOT)}")

    # 日付の新しい順。同じ日付ならファイル名順
    articles.sort(
        key=lambda article: (
            article["parsed_date"],
            article["filename"],
        ),
        reverse=True,
    )

    index_html = index_template.render(pulldown_main=pulldown_part,articles=articles)

    (ROOT / "docs" / "index.html").write_text(
        index_html,
        encoding="utf-8",
    )

    print("生成: blog/index.html")


if __name__ == "__main__":
    main()
