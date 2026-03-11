"""
merge_roads.py
--------------
Gộp nhiều features cùng tên đường thành 1 LineString duy nhất,
chỉ giữ lại: tên đường + tọa độ tim đường (centerline).

Thuật toán: Chain-linking — nối đầu-cuối các đoạn theo thứ tự liên tục.
"""

import json
from math import radians, sin, cos, sqrt, atan2
from collections import defaultdict


# ── Cài đặt ───────────────────────────────────────────────────────
INPUT_FILE  = "QL4E_all.geojson"
OUTPUT_FILE = "QL4E_merged.geojson"
TOLERANCE   = 0.0001   # ~11m — ngưỡng coi hai điểm là "khớp nhau"


# ── Hàm tiện ích ──────────────────────────────────────────────────
def haversine_km(coord1, coord2):
    """Tính khoảng cách giữa 2 điểm [lon, lat] (km)."""
    R = 6371.0
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def total_length_km(coordinates):
    """Tính tổng chiều dài chuỗi tọa độ (km)."""
    length = 0.0
    for i in range(len(coordinates) - 1):
        length += haversine_km(coordinates[i], coordinates[i+1])
    return round(length, 3)


def euclidean_dist(a, b):
    return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)


# ── Thuật toán Chain-linking ───────────────────────────────────────
def chain_link(segments, tol=TOLERANCE):
    """
    Nhận vào list các đoạn (list of coordinates).
    Trả về list tọa độ đã nối liên tục, và list các đoạn không nối được.
    """
    segs = [{'coords': s, 'used': False} for s in segments]

    def find_next(current_end):
        best = None
        best_dist = tol
        best_rev = False
        for s in segs:
            if s['used']:
                continue
            d_start = euclidean_dist(current_end, s['coords'][0])
            d_end   = euclidean_dist(current_end, s['coords'][-1])
            if d_start < best_dist:
                best_dist = d_start
                best = s
                best_rev = False
            if d_end < best_dist:
                best_dist = d_end
                best = s
                best_rev = True
        return best, best_rev

    # Tìm điểm bắt đầu: start không là end của segment nào khác
    all_ends = set()
    for s in segs:
        all_ends.add(tuple(round(x, 4) for x in s['coords'][-1]))

    start_seg = None
    for s in segs:
        key = tuple(round(x, 4) for x in s['coords'][0])
        if key not in all_ends:
            start_seg = s
            break

    # Fallback: nếu không tìm được điểm đầu rõ ràng, lấy segment đầu tiên
    if start_seg is None:
        start_seg = segs[0]

    # Bắt đầu nối chuỗi
    start_seg['used'] = True
    chain_coords = list(start_seg['coords'])

    for _ in range(len(segs)):
        nxt, rev = find_next(chain_coords[-1])
        if nxt is None:
            break
        nxt['used'] = True
        new_coords = list(reversed(nxt['coords'])) if rev else list(nxt['coords'])
        # Bỏ điểm đầu trùng với điểm cuối chuỗi hiện tại
        chain_coords.extend(new_coords[1:])

    unlinked = [s['coords'] for s in segs if not s['used']]
    return chain_coords, unlinked


# ── Hàm chính ─────────────────────────────────────────────────────
def merge_geojson(input_file, output_file):
    print(f"📂 Đọc file: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    features = data['features']
    print(f"   Tổng features gốc: {len(features)}")

    # Nhóm các features theo tên đường
    road_groups = defaultdict(list)
    for feat in features:
        name = feat['properties'].get('road_name', 'Không rõ tên')
        coords = feat['geometry']['coordinates']
        road_groups[name].append(coords)

    print(f"   Số tên đường unique: {len(road_groups)}")

    # Gộp từng nhóm
    merged_features = []
    for road_name, segments in road_groups.items():
        print(f"\n🔗 Đang gộp: '{road_name}' ({len(segments)} đoạn)")

        if len(segments) == 1:
            merged_coords = segments[0]
            unlinked = []
        else:
            merged_coords, unlinked = chain_link(segments)

        length = total_length_km(merged_coords)

        if unlinked:
            print(f"   ⚠️  Có {len(unlinked)} đoạn không nối được — lưu dưới dạng MultiLineString")
            # Lưu dạng MultiLineString nếu có đoạn rời
            all_lines = [merged_coords] + unlinked
            geometry = {
                'type': 'MultiLineString',
                'coordinates': all_lines
            }
        else:
            geometry = {
                'type': 'LineString',
                'coordinates': merged_coords
            }

        feature = {
            'type': 'Feature',
            'geometry': geometry,
            'properties': {
                'road_name': road_name,
                'total_points': len(merged_coords),
                'length_km': length
            }
        }
        merged_features.append(feature)

        print(f"   ✅ Gộp xong: {len(merged_coords)} điểm tọa độ | {length} km")

    # Tạo GeoJSON mới
    output_geojson = {
        'type': 'FeatureCollection',
        'features': merged_features
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_geojson, f, ensure_ascii=False, indent=2)

    # Thống kê so sánh
    original_size = len(json.dumps(data, ensure_ascii=False))
    new_size = len(json.dumps(output_geojson, ensure_ascii=False))

    print(f"\n{'='*50}")
    print(f"✅ Hoàn thành! Đã lưu: {output_file}")
    print(f"   Features: {len(features)} → {len(merged_features)}")
    print(f"   Kích thước file: {original_size/1024:.1f} KB → {new_size/1024:.1f} KB")
    print(f"   Giảm: {(1 - new_size/original_size)*100:.1f}%")

    return output_geojson


# ── Chạy ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = merge_geojson(INPUT_FILE, OUTPUT_FILE)

    # In ra nội dung file kết quả để kiểm tra
    print(f"\n📄 Nội dung file kết quả:")
    print(json.dumps(result, ensure_ascii=False, indent=2)[:800] + "\n  ...")
