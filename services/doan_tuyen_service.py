from models.doan_tuyen import DoanTuyen
from services.tuyen_duong_service import lay_theo_id as lay_tuyen
from services.tuyen_duong_service import cap_nhat_chieu_dai_tuyen
from services.cap_duong_service import lay_theo_id_hoat_dong as lay_cap
from services.tinh_trang_service import lay_theo_id_hoat_dong as lay_tinh_trang

from repositories import doan_tuyen_repository as repo


# ==========================
# ROW → OBJECT
# ==========================

def _row_to_object(row):
    return DoanTuyen(
        id=row[0],
        ma_doan=row[1],
        tuyen_id=row[2],
        cap_duong_id=row[3],
        ly_trinh_dau=row[4],
        ly_trinh_cuoi=row[5],
        chieu_dai_thuc_te=row[7],
        tinh_trang_id=row[8],
        chieu_rong_mat_max=row[9],
        chieu_rong_mat_min=row[10],
        chieu_rong_nen_max=row[11],
        chieu_rong_nen_min=row[12],
        don_vi_bao_duong_id=row[13],
        ghi_chu=row[14],
        created_at=row[15],
    )


# ==========================
# LẤY TẤT CẢ
# ==========================

def lay_tat_ca():
    rows = repo.lay_tat_ca()
    return [_row_to_object(row) for row in rows]


# ==========================
# LẤY THEO MÃ
# ==========================

def lay_theo_ma(ma_doan):
    return repo.lay_theo_ma(ma_doan)


# ==========================
# LẤY THEO ID
# ==========================

def lay_theo_id(id):
    return repo.lay_theo_id(id)


# ==========================
# LẤY THEO TUYẾN
# ==========================

def lay_theo_tuyen(tuyen_id):
    return repo.lay_theo_tuyen(tuyen_id)


# ==========================
# THÊM
# ==========================

def them_doan_tuyen(doan: DoanTuyen):

    if not lay_tuyen(doan.tuyen_id):
        raise ValueError("Tuyen khong ton tai!")

    if not lay_cap(doan.cap_duong_id):
        raise ValueError("Cap duong khong hop le!")

    if doan.tinh_trang_id and not lay_tinh_trang(doan.tinh_trang_id):
        raise ValueError("Tinh trang khong hop le!")

    if doan.ly_trinh_cuoi <= doan.ly_trinh_dau:
        raise ValueError("Ly trinh cuoi phai lon hon ly trinh dau!")

    chieu_dai = doan.ly_trinh_cuoi - doan.ly_trinh_dau

    try:
        last_id = repo.them_doan_tuyen(
            doan.ma_doan,
            doan.tuyen_id,
            doan.cap_duong_id,
            doan.ly_trinh_dau,
            doan.ly_trinh_cuoi,
            chieu_dai,
            doan.chieu_dai_thuc_te,
            doan.tinh_trang_id,
            doan.chieu_rong_mat_max,
            doan.chieu_rong_mat_min,
            doan.chieu_rong_nen_max,
            doan.chieu_rong_nen_min,
            doan.don_vi_bao_duong_id,
            doan.ghi_chu
        )
        doan.id = last_id
    except Exception:
        raise ValueError("Ma doan da ton tai!")

    # Cập nhật lại chiều dài tuyến
    cap_nhat_chieu_dai_tuyen(doan.tuyen_id)

    return doan


# ==========================
# GET OR CREATE
# ==========================

def get_or_create_doan_tuyen(doan: DoanTuyen):
    existing = repo.lay_theo_ma(doan.ma_doan)
    if existing:
        return existing
    return them_doan_tuyen(doan)


# ==========================
# THỐNG KÊ TÌNH TRẠNG TUYẾN
# ==========================

def thong_ke_tinh_trang_tuyen(tuyen_id):
    """
    Trả về dict gồm:
    - chi_tiet: list các đoạn với tình trạng
    - tong_hop: tổng chiều dài theo từng tình trạng + tỷ lệ %
    """
    chi_tiet = repo.thong_ke_tinh_trang_tuyen(tuyen_id)

    # Tổng hợp theo tình trạng
    tong_hop = {}
    tong_km = 0.0

    for doan in chi_tiet:
        km = doan["chieu_dai_tinh"] or 0.0
        tong_km += km
        ma = doan["ma_tinh_trang"] or "CHUA_XAC_DINH"
        ten = doan["ten_tinh_trang"] or "Chưa xác định"
        mau = doan["mau_hien_thi"] or "#cccccc"

        if ma not in tong_hop:
            tong_hop[ma] = {"ten": ten, "mau": mau, "tong_km": 0.0}
        tong_hop[ma]["tong_km"] += km

    # Tính tỷ lệ %
    for ma in tong_hop:
        km = tong_hop[ma]["tong_km"]
        tong_hop[ma]["ty_le"] = round(km / tong_km * 100, 1) if tong_km > 0 else 0.0

    return {
        "chi_tiet": chi_tiet,
        "tong_hop": tong_hop,
        "tong_km":  round(tong_km, 3)
    }