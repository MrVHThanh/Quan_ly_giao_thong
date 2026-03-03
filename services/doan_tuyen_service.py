from models.doan_tuyen import DoanTuyen
from services.tuyen_duong_service import lay_theo_id as lay_tuyen
from services.tuyen_duong_service import cap_nhat_chieu_dai_tuyen
from services.cap_duong_service import lay_theo_id_hoat_dong as lay_cap

from repositories import doan_tuyen_repository as repo


# ==========================
# ROW → OBJECT
# Dùng khi repository trả về raw row (tuple),
# ví dụ: lay_tat_ca() trả về list[tuple]
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
        chieu_rong_mat_max=row[8],
        chieu_rong_mat_min=row[9],
        chieu_rong_nen_max=row[10],
        chieu_rong_nen_min=row[11],
        don_vi_bao_duong_id=row[12],
        ghi_chu=row[13],
        created_at=row[14],
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
    """Trả về DoanTuyen object hoặc None."""
    return repo.lay_theo_ma(ma_doan)


# ==========================
# LẤY THEO ID
# ==========================

def lay_theo_id(id):
    """Trả về DoanTuyen object hoặc None."""
    return repo.lay_theo_id(id)


# ==========================
# LẤY THEO TUYẾN
# Repository đã trả về list[DoanTuyen] nên không cần _row_to_object
# ==========================

def lay_theo_tuyen(tuyen_id):
    """Trả về list[DoanTuyen] sắp xếp theo ly_trinh_dau."""
    return repo.lay_theo_tuyen(tuyen_id)


# ==========================
# THÊM
# ==========================

def them_doan_tuyen(doan: DoanTuyen):

    # ---- Kiểm tra tuyến tồn tại ----
    if not lay_tuyen(doan.tuyen_id):
        raise ValueError("Tuyen khong ton tai!")

    # ---- Kiểm tra cấp đường ----
    if not lay_cap(doan.cap_duong_id):
        raise ValueError("Cap duong khong hop le!")

    # ---- Kiểm tra lý trình hợp lệ ----
    if doan.ly_trinh_cuoi <= doan.ly_trinh_dau:
        raise ValueError("Ly trinh cuoi phai lon hon ly trinh dau!")

    # ---- TỰ TÍNH CHIỀU DÀI ----
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

    # ---- CẬP NHẬT LẠI CHIỀU DÀI TUYẾN ----
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