from models.doan_di_chung import DoanDiChung
from services.tuyen_duong_service import lay_theo_id as lay_tuyen
from services.doan_tuyen_service import lay_theo_id as lay_doan
from services.tuyen_duong_service import cap_nhat_chieu_dai_tuyen
from repositories import doan_di_chung_repository as repo


# ==========================
# LẤY THEO TUYẾN
# ==========================

def lay_theo_tuyen(tuyen_id):
    """Lấy danh sách đoạn đi chung của một tuyến, sắp xếp theo ly_trinh_dau."""
    return repo.lay_theo_tuyen(tuyen_id)


# ==========================
# LẤY THEO ID
# ==========================

def lay_theo_id(id):
    return repo.lay_theo_id(id)


# ==========================
# THÊM
# ==========================

def them_doan_di_chung(ddc: DoanDiChung):
    # ---- Kiểm tra tuyến đi chung tồn tại ----
    if not lay_tuyen(ddc.tuyen_id):
        raise ValueError("Tuyen di chung khong ton tai!")

    # ---- Kiểm tra đoạn vật lý tồn tại ----
    doan = lay_doan(ddc.doan_id)
    if not doan:
        raise ValueError("Doan tuyen khong ton tai!")

    # ---- Đoạn không được thuộc chính tuyến đi chung ----
    if doan.tuyen_id == ddc.tuyen_id:
        raise ValueError(
            "Doan nay da thuoc tuyen nay (tuyen chu so huu). "
            "Khong the them vao doan di chung cua chinh tuyen do!"
        )

    # ---- Kiểm tra trùng lặp ----
    existing = repo.lay_theo_tuyen_va_doan(ddc.tuyen_id, ddc.doan_id)
    if existing:
        raise ValueError("Doan nay da duoc dang ky di chung voi tuyen nay roi!")

    try:
        last_id = repo.them_doan_di_chung(
            ddc.tuyen_id,
            ddc.doan_id,
            ddc.ly_trinh_dau,
            ddc.ly_trinh_cuoi,
            ddc.ghi_chu
        )
        ddc.id = last_id
    except Exception:
        raise ValueError("Them doan di chung that bai!")

    # ---- Cập nhật lại chiều dài tuyến đi chung ----
    cap_nhat_chieu_dai_tuyen(ddc.tuyen_id)

    return ddc


# ==========================
# XOÁ
# ==========================

def xoa_doan_di_chung(id):
    ddc = lay_theo_id(id)
    if not ddc:
        raise ValueError("Doan di chung khong ton tai!")

    tuyen_id = ddc.tuyen_id
    repo.xoa_doan_di_chung(id)

    # ---- Cập nhật lại chiều dài tuyến ----
    cap_nhat_chieu_dai_tuyen(tuyen_id)


# ==========================
# GET OR CREATE
# ==========================

def get_or_create_doan_di_chung(ddc: DoanDiChung):
    existing = repo.lay_theo_tuyen_va_doan(ddc.tuyen_id, ddc.doan_id)
    if existing:
        return existing
    return them_doan_di_chung(ddc)