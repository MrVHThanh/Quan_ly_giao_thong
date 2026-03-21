"""
Seed: TuyenDuong → ThongTinTuyen → DoanTuyen → DoanDiChung
Idempotent: INSERT OR IGNORE.

Thứ tự bắt buộc:
1. tuyen_duong     (trigger tự tính chiều dài = 0 lúc đầu)
2. thong_tin_tuyen (9/49 tuyến có mô tả)
3. doan_tuyen      (trigger tự cập nhật chieu_dai_quan_ly)
4. doan_di_chung   (trigger tự cập nhật chieu_dai_thuc_te)

Xử lý đặc biệt:
- cap_quan_ly_ma, don_vi_quan_ly_ma, tuyen_ma, cap_duong_ma,
  tinh_trang_ma, ket_cau_mat_ma, don_vi_bao_duong_ma
  → tra id thực qua lookup dict trước khi INSERT
- ma_doan_di_chung sinh tự động: DDC-{tuyen_di_chung_ma}-{doan_ma}-{stt:03d}
"""

import sqlite3
from typing import Dict

import data.tuyen_duong_data as tuyen_duong_data
import data.doan_tuyen_data as doan_tuyen_data
import data.doan_di_chung_data as doan_di_chung_data


def seed(conn: sqlite3.Connection) -> None:
    _seed_tuyen_duong(conn)
    _seed_thong_tin_tuyen(conn)
    _seed_doan_tuyen(conn)
    _seed_doan_di_chung(conn)


# ── 1. TuyenDuong ──────────────────────────────────────────────────────────

def _seed_tuyen_duong(conn: sqlite3.Connection) -> None:
    cql_map = _build_lookup(conn, "cap_quan_ly", "ma_cap")
    dv_map  = _build_lookup(conn, "don_vi", "ma_don_vi")

    sql = """
        INSERT OR IGNORE INTO tuyen_duong
            (ma_tuyen, ten_tuyen, cap_quan_ly_id, don_vi_quan_ly_id,
             diem_dau, diem_cuoi, lat_dau, lng_dau, lat_cuoi, lng_cuoi,
             nam_xay_dung, nam_hoan_thanh, ghi_chu)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    dem = 0
    for r in tuyen_duong_data.RECORDS:
        cql_id = _tra_id(cql_map, r["cap_quan_ly_ma"], "cap_quan_ly", r["ma_tuyen"])
        dv_id  = _tra_id(dv_map,  r["don_vi_quan_ly_ma"], "don_vi", r["ma_tuyen"])
        conn.execute(sql, (
            r["ma_tuyen"], r["ten_tuyen"], cql_id, dv_id,
            r.get("diem_dau"), r.get("diem_cuoi"),
            r.get("lat_dau"), r.get("lng_dau"),
            r.get("lat_cuoi"), r.get("lng_cuoi"),
            r.get("nam_xay_dung"), r.get("nam_hoan_thanh"),
            r.get("ghi_chu"),
        ))
        dem += 1

    print(f"[seed_tuyen_duong] {dem} tuyến đường.")


# ── 2. ThongTinTuyen ───────────────────────────────────────────────────────

def _seed_thong_tin_tuyen(conn: sqlite3.Connection) -> None:
    td_map = _build_lookup(conn, "tuyen_duong", "ma_tuyen")

    sql = """
        INSERT OR IGNORE INTO thong_tin_tuyen (tuyen_id, mo_ta)
        VALUES (?, ?)
    """
    dem = 0
    for r in tuyen_duong_data.RECORDS:
        if not r.get("thong_tin_mo_ta"):
            continue
        tuyen_id = _tra_id(td_map, r["ma_tuyen"], "tuyen_duong", r["ma_tuyen"])
        conn.execute(sql, (tuyen_id, r["thong_tin_mo_ta"]))
        dem += 1

    print(f"[seed_thong_tin_tuyen] {dem} mô tả tuyến.")


# ── 3. DoanTuyen ───────────────────────────────────────────────────────────

def _seed_doan_tuyen(conn: sqlite3.Connection) -> None:
    td_map  = _build_lookup(conn, "tuyen_duong", "ma_tuyen")
    cd_map  = _build_lookup(conn, "cap_duong", "ma_cap")
    tt_map  = _build_lookup(conn, "tinh_trang", "ma_tinh_trang")
    kcm_map = _build_lookup(conn, "ket_cau_mat_duong", "ma_ket_cau")
    dv_map  = _build_lookup(conn, "don_vi", "ma_don_vi")

    # Map tình trạng từ tên tiếng Việt (trong Excel) sang mã
    ten_to_ma_tt = {
        "Tốt": "TOT", "Trung bình": "TB", "Kém": "KEM",
        "Hư hỏng nặng": "HH_NANG", "Đang thi công": "THI_CONG",
        "Đang bảo trì": "BAO_TRI", "Tạm đóng": "TAM_DONG",
        "Ngưng sử dụng": "NGUNG", "Chưa xây dựng": "CHUA_XD",
    }

    sql = """
        INSERT OR IGNORE INTO doan_tuyen
            (ma_doan, tuyen_id, cap_duong_id, tinh_trang_id, ket_cau_mat_id,
             ly_trinh_dau, ly_trinh_cuoi, chieu_dai_thuc_te,
             chieu_rong_mat_min, chieu_rong_mat_max,
             chieu_rong_nen_min, chieu_rong_nen_max,
             don_vi_bao_duong_id, ghi_chu)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    dem = 0
    for r in doan_tuyen_data.RECORDS:
        # Tình trạng: Excel lưu tên tiếng Việt hoặc mã — chuẩn hóa về mã
        tt_raw = r.get("tinh_trang_ma", "")
        tt_ma  = ten_to_ma_tt.get(tt_raw, tt_raw)  # nếu đã là mã thì giữ nguyên

        tuyen_id = _tra_id(td_map,  r["tuyen_ma"],           "tuyen_duong",      r["ma_doan"])
        cd_id    = _tra_id_nullable(cd_map,  r.get("cap_duong_ma"))
        tt_id    = _tra_id_nullable(tt_map,  tt_ma)
        kcm_id   = _tra_id_nullable(kcm_map, r.get("ket_cau_mat_ma"))
        dv_bd_id = _tra_id_nullable(dv_map,  r.get("don_vi_bao_duong_ma"))

        conn.execute(sql, (
            r["ma_doan"], tuyen_id, cd_id, tt_id, kcm_id,
            r["ly_trinh_dau"], r["ly_trinh_cuoi"],
            r.get("chieu_dai_thuc_te"),
            r.get("chieu_rong_mat_min"), r.get("chieu_rong_mat_max"),
            r.get("chieu_rong_nen_min"), r.get("chieu_rong_nen_max"),
            dv_bd_id, r.get("ghi_chu"),
        ))
        dem += 1

    print(f"[seed_doan_tuyen] {dem} đoạn tuyến. Trigger tự cập nhật chieu_dai_quan_ly.")


# ── 4. DoanDiChung ─────────────────────────────────────────────────────────

def _seed_doan_di_chung(conn: sqlite3.Connection) -> None:
    td_map   = _build_lookup(conn, "tuyen_duong", "ma_tuyen")
    doan_map = _build_lookup(conn, "doan_tuyen", "ma_doan")

    # Đếm số DDC đã có trên mỗi doan_id (để sinh STT mã)
    stt_counter: Dict[int, int] = {}

    sql = """
        INSERT OR IGNORE INTO doan_di_chung
            (ma_doan_di_chung, tuyen_di_chung_id, tuyen_chinh_id, doan_id,
             ly_trinh_dau_di_chung, ly_trinh_cuoi_di_chung,
             ly_trinh_dau_tuyen_chinh, ly_trinh_cuoi_tuyen_chinh,
             ghi_chu)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    dem = 0
    for r in doan_di_chung_data.RECORDS:
        tdc_id  = _tra_id(td_map,   r["tuyen_di_chung_ma"], "tuyen_duong",  r["doan_ma"])
        tc_id   = _tra_id(td_map,   r["tuyen_chinh_ma"],    "tuyen_duong",  r["doan_ma"])
        doan_id = _tra_id(doan_map, r["doan_ma"],           "doan_tuyen",   r["doan_ma"])

        stt_counter[doan_id] = stt_counter.get(doan_id, 0) + 1
        ma_ddc = f"DDC-{r['tuyen_di_chung_ma']}-{r['doan_ma']}-{stt_counter[doan_id]:03d}"

        # Kiểm tra trùng (ma_doan_di_chung là UNIQUE)
        da_co = conn.execute(
            "SELECT id FROM doan_di_chung WHERE ma_doan_di_chung = ?", (ma_ddc,)
        ).fetchone()
        if da_co:
            continue

        conn.execute(sql, (
            ma_ddc, tdc_id, tc_id, doan_id,
            r["ly_trinh_dau_di_chung"], r["ly_trinh_cuoi_di_chung"],
            r["ly_trinh_dau_tuyen_chinh"], r["ly_trinh_cuoi_tuyen_chinh"],
            r.get("ghi_chu"),
        ))
        dem += 1

    print(f"[seed_doan_di_chung] {dem} đoạn đi chung. Trigger tự cập nhật chieu_dai_thuc_te.")


# ── Helpers ────────────────────────────────────────────────────────────────

def _build_lookup(conn: sqlite3.Connection, table: str, ma_col: str) -> Dict[str, int]:
    """Tạo dict {ma: id} từ bảng."""
    rows = conn.execute(f"SELECT id, {ma_col} FROM {table}").fetchall()
    return {row[ma_col]: row["id"] for row in rows}


def _tra_id(lookup: Dict[str, int], ma: str, table: str, context: str) -> int:
    if ma not in lookup:
        raise ValueError(
            f"[seed] Không tìm thấy '{ma}' trong bảng '{table}' (context: {context}). "
            "Kiểm tra thứ tự seed hoặc dữ liệu."
        )
    return lookup[ma]


def _tra_id_nullable(lookup: Dict[str, int], ma) -> int:
    """Tra id, trả None nếu ma là None hoặc không tìm thấy."""
    if not ma:
        return None
    return lookup.get(str(ma).strip())
