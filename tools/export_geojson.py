"""
Tool: export_geojson.py
Xuất tuyến đường từ DB ra file *.geojson.

Cách dùng:
    python tools/export_geojson.py QL4E
    python tools/export_geojson.py DT158 --out data/geojson/
    python tools/export_geojson.py --tat-ca --out data/geojson/
"""

import argparse
import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.database import get_connection

THU_MUC_XUAT_MAC_DINH = os.path.join(_ROOT, "data", "geojson")


def export_mot_tuyen(db_path: str, ma_tuyen: str, thu_muc_xuat: str) -> str:
    """Xuất 1 tuyến ra file. Trả về đường dẫn file đã xuất."""
    conn = get_connection(db_path)
    try:
        tuyen = conn.execute(
            "SELECT id, ma_tuyen, ten_tuyen FROM tuyen_duong WHERE ma_tuyen = ?",
            (ma_tuyen,)
        ).fetchone()
        if tuyen is None:
            raise ValueError(f"Không tìm thấy tuyến mã '{ma_tuyen}'.")

        geo = conn.execute(
            "SELECT coordinates, so_diem, chieu_dai_gps FROM tuyen_duong_geo WHERE tuyen_id = ?",
            (tuyen["id"],)
        ).fetchone()
        if geo is None:
            raise ValueError(
                f"Tuyến '{ma_tuyen}' chưa có dữ liệu GeoJSON.\n"
                f"  → Chạy import_geojson.py trước."
            )

        coordinates = json.loads(geo["coordinates"])
        geojson_obj = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {
                    "road_id": tuyen["ma_tuyen"],
                    "road_name": tuyen["ten_tuyen"],
                    "so_diem": geo["so_diem"],
                    "chieu_dai_gps_km": geo["chieu_dai_gps"],
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates,
                },
            }],
        }

        os.makedirs(thu_muc_xuat, exist_ok=True)
        duong_dan = os.path.join(thu_muc_xuat, f"{tuyen['ma_tuyen']}.geojson")
        with open(duong_dan, "w", encoding="utf-8") as f:
            json.dump(geojson_obj, f, ensure_ascii=False, separators=(",", ":"))

        return duong_dan
    finally:
        conn.close()


def export_tat_ca(db_path: str, thu_muc_xuat: str) -> list:
    """Xuất tất cả tuyến đã có GeoJSON. Trả về list kết quả."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute("""
            SELECT td.ma_tuyen FROM tuyen_duong td
            JOIN tuyen_duong_geo g ON g.tuyen_id = td.id
            ORDER BY td.ma_tuyen
        """).fetchall()
    finally:
        conn.close()

    if not rows:
        print("Chưa có tuyến nào có dữ liệu GeoJSON trong DB.")
        return []

    results = []
    for row in rows:
        ma = row["ma_tuyen"]
        try:
            path = export_mot_tuyen(db_path, ma, thu_muc_xuat)
            results.append({"ma_tuyen": ma, "ok": True, "path": path})
            print(f"  ✓ {ma} → {os.path.basename(path)}")
        except Exception as e:
            results.append({"ma_tuyen": ma, "ok": False, "loi": str(e)})
            print(f"  ✗ {ma}: {e}")
    return results


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Xuất dữ liệu GeoJSON từ DB ra file"
    )
    parser.add_argument("ma_tuyen", nargs="?", help="Mã tuyến cần xuất (VD: QL4E)")
    parser.add_argument("--tat-ca", action="store_true", help="Xuất tất cả tuyến")
    parser.add_argument("--out", default=THU_MUC_XUAT_MAC_DINH,
                        help=f"Thư mục xuất (mặc định: {THU_MUC_XUAT_MAC_DINH})")
    parser.add_argument("--db", default=os.path.join(_ROOT, "giao_thong.db"),
                        help="Đường dẫn DB SQLite")
    args = parser.parse_args()

    if args.tat_ca:
        print(f"\nXuất tất cả tuyến → {args.out}")
        ket_qua = export_tat_ca(args.db, args.out)
        ok = sum(1 for r in ket_qua if r["ok"])
        print(f"\nHoàn thành: {ok}/{len(ket_qua)} tuyến.\n")
    elif args.ma_tuyen:
        path = export_mot_tuyen(args.db, args.ma_tuyen.upper(), args.out)
        print(f"\n✓ Xuất thành công: {path}\n")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
