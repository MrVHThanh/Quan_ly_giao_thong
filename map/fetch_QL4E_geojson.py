"""
fetch_QL4E_geojson.py
---------------------
Lấy dữ liệu GeoJSON của Quốc lộ 4E từ OpenStreetMap theo danh sách ID trong file Excel.

Cách dùng:
    python fetch_QL4E_geojson.py                    # chế độ đơn (ổn định)
    python fetch_QL4E_geojson.py --batch            # chế độ batch (nhanh hơn)
    python fetch_QL4E_geojson.py --input ID_4E_Road_Laocai.xlsx --output QL4E.geojson
"""

import requests
import pandas as pd
import json
import time
import argparse
from datetime import datetime

# ── Cài đặt ───────────────────────────────────────────────────────
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]
DELAY   = 2    # giây giữa các request
RETRIES = 3    # số lần thử lại
TIMEOUT = 30   # giây timeout
BATCH   = 10   # số way mỗi batch


# ── Đọc Excel ─────────────────────────────────────────────────────
def read_ids_from_excel(file_path):
    df = pd.read_excel(file_path, header=0)
    df.columns = ['Ten_duong', 'ID', 'Ghi_chu']
    df['ID'] = df['ID'].astype(int)
    df['Ghi_chu'] = df['Ghi_chu'].fillna('')
    print("📋 Đọc được " + str(len(df)) + " dòng từ file Excel")
    return df


# ── Gửi query Overpass ────────────────────────────────────────────
def query_overpass(query):
    for attempt in range(RETRIES):
        url = OVERPASS_URLS[attempt % len(OVERPASS_URLS)]
        try:
            resp = requests.get(
                url,
                params={'data': query},
                timeout=TIMEOUT,
                headers={'Accept': 'application/json'}
            )
            if resp.status_code != 200:
                print("   ⚠️  HTTP " + str(resp.status_code) + " từ " + url + " — thử lại...")
                time.sleep(DELAY * (attempt + 1))
                continue

            text = resp.text.strip()
            if not text:
                print("   ⚠️  Response rỗng từ " + url + " — thử lại...")
                time.sleep(DELAY * (attempt + 1))
                continue

            if not text.startswith('{'):
                print("   ⚠️  Không phải JSON: " + text[:80] + " — thử lại...")
                time.sleep(DELAY * (attempt + 1))
                continue

            return json.loads(text)

        except requests.exceptions.Timeout:
            print("   ⚠️  Timeout lần " + str(attempt+1) + "/" + str(RETRIES))
            time.sleep(DELAY * (attempt + 1))
        except requests.exceptions.ConnectionError:
            print("   ⚠️  Lỗi kết nối lần " + str(attempt+1) + "/" + str(RETRIES))
            time.sleep(DELAY * (attempt + 1))
        except json.JSONDecodeError as e:
            print("   ⚠️  JSONDecodeError: " + str(e))
            time.sleep(DELAY * (attempt + 1))

    print("   ❌ Thất bại sau " + str(RETRIES) + " lần thử")
    return None


# ── Lấy 1 way ────────────────────────────────────────────────────
def get_way_data(way_id):
    query = "[out:json][timeout:25];\nway(" + str(way_id) + ");\n(._;>;);\nout body;"
    data = query_overpass(query)
    if not data or not data.get('elements'):
        print("   ⚠️  Không có dữ liệu cho way " + str(way_id))
        return None

    nodes = {}
    for el in data['elements']:
        if el['type'] == 'node':
            nodes[el['id']] = (el['lon'], el['lat'])

    ways = [el for el in data['elements'] if el['type'] == 'way']
    if not ways:
        return None

    way_el = ways[0]
    coordinates = [
        [nodes[nid][0], nodes[nid][1]]
        for nid in way_el['nodes'] if nid in nodes
    ]
    if len(coordinates) < 2:
        print("   ⚠️  Way " + str(way_id) + " có ít hơn 2 điểm, bỏ qua")
        return None

    return {
        "id":          way_el['id'],
        "coordinates": coordinates,
        "tags":        way_el.get('tags', {})
    }


# ── Lấy nhiều way (batch) ─────────────────────────────────────────
def get_batch_way_data(way_ids):
    ids_str = ','.join(str(i) for i in way_ids)
    query = "[out:json][timeout:60];\nway(id:" + ids_str + ");\n(._;>;);\nout body;"
    data = query_overpass(query)
    if not data or not data.get('elements'):
        return {}

    nodes = {}
    for el in data['elements']:
        if el['type'] == 'node':
            nodes[el['id']] = (el['lon'], el['lat'])

    result = {}
    for el in data['elements']:
        if el['type'] != 'way':
            continue
        wid = el['id']
        coordinates = [
            [nodes[nid][0], nodes[nid][1]]
            for nid in el['nodes'] if nid in nodes
        ]
        if len(coordinates) >= 2:
            result[wid] = {
                "id":          wid,
                "coordinates": coordinates,
                "tags":        el.get('tags', {})
            }
    return result


# ── Ghi GeoJSON ───────────────────────────────────────────────────
def save_to_geojson(roads_data, filename):
    features = []
    for road in roads_data:
        wd = road['way_data']
        if not wd:
            continue
        features.append({
            "type": "Feature",
            "geometry": {
                "type":        "LineString",
                "coordinates": wd["coordinates"]
            },
            "properties": {
                "way_id":    wd["id"],
                "road_name": road["Ten_duong"],
                "notes":     road["Ghi_chu"],
                "tags":      wd["tags"]
            }
        })

    # Ghi file với tọa độ mỗi feature trên 1 dòng
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('{\n  "type": "FeatureCollection",\n  "features": [\n')
        parts = []
        for feat in features:
            coords_str = json.dumps(feat["geometry"]["coordinates"],
                                    ensure_ascii=False, separators=(',', ':'))
            props_str  = json.dumps(feat["properties"],
                                    indent=4, ensure_ascii=False)
            part = (
                '    {\n'
                '      "type": "Feature",\n'
                '      "geometry": {\n'
                '        "type": "LineString",\n'
                '        "coordinates": ' + coords_str + '\n'
                '      },\n'
                '      "properties": ' + props_str + '\n'
                '    }'
            )
            parts.append(part)
        f.write(',\n'.join(parts))
        f.write('\n  ]\n}')

    valid = len(features)
    total = len(roads_data)
    print("\n✅ Đã lưu: " + filename)
    print("   Tổng ID:     " + str(total))
    print("   Có dữ liệu: " + str(valid))
    print("   Thất bại:   " + str(total - valid))


# ── Main ──────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Lấy GeoJSON tuyến đường từ OpenStreetMap')
    parser.add_argument('--input',  '-i', default='ID_4E_Road_Laocai.xlsx')
    parser.add_argument('--output', '-o', default='')
    parser.add_argument('--batch',  '-b', action='store_true',
                        help='Dùng batch query (10 way/lần, nhanh hơn)')
    args = parser.parse_args()

    if not args.output:
        ts = datetime.now().strftime('%Y%m%d_%H%M')
        args.output = 'QL4E_laocai_' + ts + '.geojson'

    roads_df = read_ids_from_excel(args.input)
    way_ids  = roads_df['ID'].tolist()
    roads_data = []

    if args.batch:
        print("\n🚀 Chế độ BATCH — " + str(BATCH) + " way/lần")
        for i in range(0, len(way_ids), BATCH):
            batch    = way_ids[i:i + BATCH]
            batch_no = i // BATCH + 1
            end_no   = min(i + BATCH, len(way_ids))
            print("\n📦 Batch " + str(batch_no) + ": way " + str(i+1) + "–" + str(end_no))

            batch_result = get_batch_way_data(batch)

            for _, row in roads_df.iloc[i:i + BATCH].iterrows():
                wid = int(row['ID'])
                wd  = batch_result.get(wid)
                roads_data.append({
                    "Ten_duong": row['Ten_duong'],
                    "ID":        wid,
                    "Ghi_chu":   str(row['Ghi_chu']),
                    "way_data":  wd
                })
                status = '✅' if wd else '❌'
                n_pts  = len(wd['coordinates']) if wd else 0
                print("   " + status + " Way " + str(wid) + " — " + str(n_pts) + " điểm")

            if i + BATCH < len(way_ids):
                print("   ⏳ Chờ " + str(DELAY) + "s...")
                time.sleep(DELAY)

    else:
        total = len(way_ids)
        print("\n🔍 Chế độ ĐƠN — " + str(total) + " way")
        for idx, (_, row) in enumerate(roads_df.iterrows(), 1):
            wid = int(row['ID'])
            print("\n[" + str(idx).rjust(2) + "/" + str(total) + "] Way " + str(wid))
            wd = get_way_data(wid)
            if wd:
                print("   ✅ " + str(len(wd['coordinates'])) + " điểm tọa độ")
            roads_data.append({
                "Ten_duong": row['Ten_duong'],
                "ID":        wid,
                "Ghi_chu":   str(row['Ghi_chu']),
                "way_data":  wd
            })
            if idx < total:
                time.sleep(DELAY)

    save_to_geojson(roads_data, args.output)


if __name__ == "__main__":
    main()


# python fetch_QL4E_geojson.py --batch
# 