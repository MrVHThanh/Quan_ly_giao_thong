"""
Tool: import_geojson.py
Import file *.geojson vào bảng tuyen_duong_geo trong DB.

Cách dùng:
    python tools/import_geojson.py data/QL4E.geojson
    python tools/import_geojson.py data/TL158.geojson --ma-tuyen DT158
    python tools/import_geojson.py data/geojson/          # import cả thư mục

Quy ước tự động:
    - Tên file QL4E.geojson → tìm tuyến mã QL4E trong DB
    - Nếu không khớp, thử dùng property road_name để tra
    - Dùng --ma-tuyen để chỉ định rõ khi tên file khác mã tuyến (VD: TL158 → DT158)
"""

import argparse
import json
import math
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.database import get_connection


def import_file(db_path: str, geojson_path: str, ma_tuyen_override: str = None) -> dict:
    """
    Import 1 file GeoJSON vào DB.
    Trả về dict kết quả: {ma_tuyen, so_diem, chieu_dai_gps, da_cap_nhat}
    """
    if not os.path.isfile(geojson_path):
        raise FileNotFoundError(f"Không tìm thấy file: {geojson_path}")

    ten_file = os.path.basename(geojson_path)

    with open(geojson_path, encoding="utf-8") as f:
        geojson = json.load(f)

    coordinates = _trich_xuat_coordinates(geojson, ten_file)
    so_diem = len(coordinates)
    chieu_dai_gps = round(_tinh_chieu_dai_km(coordinates), 3)

    conn = get_connection(db_path)
    try:
        # Xác định mã tuyến
        ma_tuyen = ma_tuyen_override or _suy_ma_tuyen(geojson, ten_file, conn)

        # Kiểm tra tuyến tồn tại trong DB
        row = conn.execute(
            "SELECT id, ten_tuyen FROM tuyen_duong WHERE ma_tuyen = ?", (ma_tuyen,)
        ).fetchone()
        if row is None:
            raise ValueError(
                f"Không tìm thấy tuyến mã '{ma_tuyen}' trong DB.\n"
                f"  → Dùng --ma-tuyen <MA> để chỉ định rõ (VD: --ma-tuyen DT158)"
            )

        tuyen_id = row["id"]

        # INSERT OR REPLACE
        da_co = conn.execute(
            "SELECT id FROM tuyen_duong_geo WHERE tuyen_id = ?", (tuyen_id,)
        ).fetchone()

        sql = """
            INSERT INTO tuyen_duong_geo (tuyen_id, coordinates, so_diem, chieu_dai_gps, nguon, updated_at)
            VALUES (?, ?, ?, ?, ?, datetime('now','localtime'))
            ON CONFLICT(tuyen_id) DO UPDATE SET
                coordinates   = excluded.coordinates,
                so_diem       = excluded.so_diem,
                chieu_dai_gps = excluded.chieu_dai_gps,
                nguon         = excluded.nguon,
                updated_at    = datetime('now','localtime')
        """
        conn.execute(sql, (tuyen_id, json.dumps(coordinates), so_diem, chieu_dai_gps, ten_file))
        conn.commit()

        return {
            "ma_tuyen": ma_tuyen,
            "ten_tuyen": row["ten_tuyen"],
            "so_diem": so_diem,
            "chieu_dai_gps": chieu_dai_gps,
            "da_cap_nhat": da_co is not None,
            "nguon": ten_file,
        }
    finally:
        conn.close()


def import_thu_muc(db_path: str, thu_muc: str) -> list:
    """Import tất cả file *.geojson trong thư mục."""
    results = []
    files = sorted(f for f in os.listdir(thu_muc) if f.lower().endswith(".geojson"))
    if not files:
        print(f"Không tìm thấy file .geojson nào trong: {thu_muc}")
        return results

    for ten_file in files:
        path = os.path.join(thu_muc, ten_file)
        try:
            ket_qua = import_file(db_path, path)
            results.append({"file": ten_file, "ok": True, **ket_qua})
            trang_thai = "CẬP NHẬT" if ket_qua["da_cap_nhat"] else "MỚI"
            print(f"  ✓ [{trang_thai}] {ten_file} → {ket_qua['ma_tuyen']} "
                  f"({ket_qua['so_diem']} điểm, {ket_qua['chieu_dai_gps']} km)")
        except Exception as e:
            results.append({"file": ten_file, "ok": False, "loi": str(e)})
            print(f"  ✗ {ten_file}: {e}")
    return results


# ── Helpers ────────────────────────────────────────────────────────────────

def _suy_ma_tuyen(geojson: dict, ten_file: str, conn) -> str:
    """
    Suy mã tuyến theo thứ tự ưu tiên:
    1. Tên file (QL4E.geojson → QL4E)
    2. Property road_id trong GeoJSON
    3. Tra road_name → ten_tuyen trong DB
    """
    # 1. Từ tên file
    ma_tu_file = os.path.splitext(ten_file)[0].upper()
    row = conn.execute(
        "SELECT id FROM tuyen_duong WHERE ma_tuyen = ?", (ma_tu_file,)
    ).fetchone()
    if row:
        return ma_tu_file

    # 2. Từ property road_id
    for feature in geojson.get("features", []):
        road_id = feature.get("properties", {}).get("road_id")
        if road_id:
            row = conn.execute(
                "SELECT id FROM tuyen_duong WHERE ma_tuyen = ?", (road_id.upper(),)
            ).fetchone()
            if row:
                return road_id.upper()

    # 3. Từ road_name → khớp ten_tuyen
    for feature in geojson.get("features", []):
        road_name = feature.get("properties", {}).get("road_name", "")
        if road_name:
            row = conn.execute(
                "SELECT ma_tuyen FROM tuyen_duong WHERE ten_tuyen = ?", (road_name,)
            ).fetchone()
            if row:
                return row["ma_tuyen"]

    raise ValueError(
        f"Không thể tự xác định mã tuyến cho file '{ten_file}'.\n"
        f"  → Dùng --ma-tuyen <MA> để chỉ định rõ (VD: --ma-tuyen DT158)"
    )


def _trich_xuat_coordinates(geojson: dict, ten_file: str) -> list:
    for feature in geojson.get("features", []):
        geom = feature.get("geometry", {})
        if geom.get("type") == "LineString":
            return geom["coordinates"]
        if geom.get("type") == "MultiLineString":
            coords = []
            for part in geom["coordinates"]:
                coords.extend(part)
            return coords
    if geojson.get("type") == "LineString":
        return geojson["coordinates"]
    raise ValueError(f"Không tìm thấy geometry LineString trong {ten_file}")


def _tinh_chieu_dai_km(coords: list) -> float:
    R = 6371.0
    tong = 0.0
    for i in range(1, len(coords)):
        lng1, lat1 = coords[i - 1]
        lng2, lat2 = coords[i]
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = (math.sin(dlat / 2) ** 2
             + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
             * math.sin(dlng / 2) ** 2)
        tong += R * 2 * math.asin(math.sqrt(a))
    return tong


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Import file GeoJSON vào bảng tuyen_duong_geo"
    )
    parser.add_argument("duong_dan", help="File .geojson hoặc thư mục chứa .geojson")
    parser.add_argument("--db", default=os.path.join(_ROOT, "giao_thong.db"),
                        help="Đường dẫn DB SQLite (mặc định: giao_thong.db)")
    parser.add_argument("--ma-tuyen", dest="ma_tuyen",
                        help="Chỉ định rõ mã tuyến (VD: DT158 khi file tên TL158.geojson)")
    args = parser.parse_args()

    if os.path.isdir(args.duong_dan):
        print(f"\nImport thư mục: {args.duong_dan}")
        import_thu_muc(args.db, args.duong_dan)
    else:
        ket_qua = import_file(args.db, args.duong_dan, args.ma_tuyen)
        trang_thai = "CẬP NHẬT" if ket_qua["da_cap_nhat"] else "MỚI"
        print(f"\n✓ [{trang_thai}] {ket_qua['ten_tuyen']} ({ket_qua['ma_tuyen']})")
        print(f"  Số điểm    : {ket_qua['so_diem']}")
        print(f"  Chiều dài  : {ket_qua['chieu_dai_gps']} km")
        print(f"  File nguồn : {ket_qua['nguon']}\n")


if __name__ == "__main__":
    main()
