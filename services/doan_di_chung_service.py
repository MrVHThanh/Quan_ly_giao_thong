"""
Service: DoanDiChung — Đoạn đi chung giữa các tuyến
Toàn bộ validation + business logic tập trung ở đây.

Các quy tắc nghiệp vụ:
- Mỗi bản ghi tham chiếu đúng 1 đoạn vật lý (doan_id)
- tuyen_di_chung_id ≠ tuyen_chinh_id (không được đi chung trên chính mình)
- Lý trình của đoạn đi chung phải nằm trong phạm vi lý trình đoạn vật lý tuyến chủ
- Không được có 2 bản ghi trùng (tuyen_di_chung_id, doan_id) — UNIQUE constraint DB
"""

import sqlite3
from typing import Optional, List

import models.doan_di_chung as doan_di_chung_model
import repositories.doan_di_chung_repository as doan_di_chung_repo
import repositories.doan_tuyen_repository as doan_tuyen_repo
import repositories.tuyen_duong_repository as tuyen_duong_repo


class DoanDiChungServiceError(Exception):
    pass


def lay_tat_ca(conn: sqlite3.Connection) -> List[doan_di_chung_model.DoanDiChung]:
    return doan_di_chung_repo.lay_tat_ca(conn)


def lay_theo_id(
    conn: sqlite3.Connection, id: int
) -> doan_di_chung_model.DoanDiChung:
    obj = doan_di_chung_repo.lay_theo_id(conn, id)
    if obj is None:
        raise DoanDiChungServiceError(f"Không tìm thấy đoạn đi chung id={id}.")
    return obj


def lay_theo_tuyen_di_chung(
    conn: sqlite3.Connection, tuyen_di_chung_id: int
) -> List[doan_di_chung_model.DoanDiChung]:
    return doan_di_chung_repo.lay_theo_tuyen_di_chung(conn, tuyen_di_chung_id)


def lay_theo_tuyen_chinh(
    conn: sqlite3.Connection, tuyen_chinh_id: int
) -> List[doan_di_chung_model.DoanDiChung]:
    return doan_di_chung_repo.lay_theo_tuyen_chinh(conn, tuyen_chinh_id)


def them(
    conn: sqlite3.Connection,
    tuyen_di_chung_id: int,
    tuyen_chinh_id: int,
    doan_id: int,
    ly_trinh_dau_di_chung: float,
    ly_trinh_cuoi_di_chung: float,
    ly_trinh_dau_tuyen_chinh: float,
    ly_trinh_cuoi_tuyen_chinh: float,
    ghi_chu: Optional[str] = None,
) -> doan_di_chung_model.DoanDiChung:
    _validate_tuyen_khac_nhau(tuyen_di_chung_id, tuyen_chinh_id)
    _validate_tuyen_ton_tai(conn, tuyen_di_chung_id, "tuyến đi chung")
    _validate_tuyen_ton_tai(conn, tuyen_chinh_id, "tuyến chủ")
    doan = _validate_doan_ton_tai(conn, doan_id)
    _validate_doan_thuoc_tuyen_chinh(doan, tuyen_chinh_id)
    _validate_ly_trinh_cap(ly_trinh_dau_di_chung, ly_trinh_cuoi_di_chung, "tuyến đi chung")
    _validate_ly_trinh_cap(ly_trinh_dau_tuyen_chinh, ly_trinh_cuoi_tuyen_chinh, "tuyến chủ")
    _validate_ly_trinh_nam_trong_doan(
        doan, ly_trinh_dau_tuyen_chinh, ly_trinh_cuoi_tuyen_chinh
    )

    ma = _tao_ma_doan_di_chung(conn, tuyen_di_chung_id, tuyen_chinh_id, doan_id)
    obj = doan_di_chung_model.DoanDiChung(
        ma_doan_di_chung=ma,
        tuyen_di_chung_id=tuyen_di_chung_id,
        tuyen_chinh_id=tuyen_chinh_id,
        doan_id=doan_id,
        ly_trinh_dau_di_chung=ly_trinh_dau_di_chung,
        ly_trinh_cuoi_di_chung=ly_trinh_cuoi_di_chung,
        ly_trinh_dau_tuyen_chinh=ly_trinh_dau_tuyen_chinh,
        ly_trinh_cuoi_tuyen_chinh=ly_trinh_cuoi_tuyen_chinh,
        ghi_chu=ghi_chu,
    )
    try:
        obj.id = doan_di_chung_repo.them(conn, obj)
    except Exception as e:
        if "UNIQUE" in str(e):
            raise DoanDiChungServiceError(
                f"Tuyến id={tuyen_di_chung_id} đã có đoạn đi chung "
                f"trên đoạn vật lý id={doan_id}."
            )
        raise
    return obj


def sua(
    conn: sqlite3.Connection,
    id: int,
    ly_trinh_dau_di_chung: float,
    ly_trinh_cuoi_di_chung: float,
    ly_trinh_dau_tuyen_chinh: float,
    ly_trinh_cuoi_tuyen_chinh: float,
    ghi_chu: Optional[str] = None,
) -> doan_di_chung_model.DoanDiChung:
    obj = lay_theo_id(conn, id)
    doan = _validate_doan_ton_tai(conn, obj.doan_id)
    _validate_ly_trinh_cap(ly_trinh_dau_di_chung, ly_trinh_cuoi_di_chung, "tuyến đi chung")
    _validate_ly_trinh_cap(ly_trinh_dau_tuyen_chinh, ly_trinh_cuoi_tuyen_chinh, "tuyến chủ")
    _validate_ly_trinh_nam_trong_doan(doan, ly_trinh_dau_tuyen_chinh, ly_trinh_cuoi_tuyen_chinh)

    obj.ly_trinh_dau_di_chung = ly_trinh_dau_di_chung
    obj.ly_trinh_cuoi_di_chung = ly_trinh_cuoi_di_chung
    obj.ly_trinh_dau_tuyen_chinh = ly_trinh_dau_tuyen_chinh
    obj.ly_trinh_cuoi_tuyen_chinh = ly_trinh_cuoi_tuyen_chinh
    obj.ghi_chu = ghi_chu
    doan_di_chung_repo.sua(conn, obj)
    return obj


def xoa(conn: sqlite3.Connection, id: int) -> None:
    lay_theo_id(conn, id)
    doan_di_chung_repo.xoa(conn, id)


# ── Validation + helpers nội bộ ────────────────────────────────────────────

def _validate_tuyen_khac_nhau(tuyen_di_chung_id: int, tuyen_chinh_id: int) -> None:
    if tuyen_di_chung_id == tuyen_chinh_id:
        raise DoanDiChungServiceError(
            "Tuyến đi chung và tuyến chủ không thể là cùng một tuyến."
        )


def _validate_tuyen_ton_tai(
    conn: sqlite3.Connection, tuyen_id: int, nhan: str
) -> None:
    if tuyen_duong_repo.lay_theo_id(conn, tuyen_id) is None:
        raise DoanDiChungServiceError(f"{nhan.capitalize()} id={tuyen_id} không tồn tại.")


def _validate_doan_ton_tai(conn: sqlite3.Connection, doan_id: int):
    doan = doan_tuyen_repo.lay_theo_id(conn, doan_id)
    if doan is None:
        raise DoanDiChungServiceError(f"Đoạn vật lý id={doan_id} không tồn tại.")
    return doan


def _validate_doan_thuoc_tuyen_chinh(doan, tuyen_chinh_id: int) -> None:
    if doan.tuyen_id != tuyen_chinh_id:
        raise DoanDiChungServiceError(
            f"Đoạn vật lý id={doan.id} (mã: {doan.ma_doan}) "
            f"không thuộc tuyến chủ id={tuyen_chinh_id}."
        )


def _validate_ly_trinh_cap(dau: float, cuoi: float, nhan: str) -> None:
    if dau < 0 or cuoi < 0:
        raise DoanDiChungServiceError(f"Lý trình {nhan} không được âm.")
    if cuoi <= dau:
        raise DoanDiChungServiceError(
            f"Lý trình cuối {nhan} ({cuoi}) phải lớn hơn lý trình đầu ({dau})."
        )


def _validate_ly_trinh_nam_trong_doan(doan, ly_trinh_dau: float, ly_trinh_cuoi: float) -> None:
    """Lý trình đoạn đi chung (theo tuyến chủ) phải nằm trong phạm vi đoạn vật lý."""
    if doan.ly_trinh_dau is None or doan.ly_trinh_cuoi is None:
        return  # không đủ dữ liệu để kiểm tra
    if ly_trinh_dau < doan.ly_trinh_dau or ly_trinh_cuoi > doan.ly_trinh_cuoi:
        raise DoanDiChungServiceError(
            f"Lý trình đoạn đi chung [{ly_trinh_dau}–{ly_trinh_cuoi}] "
            f"vượt ngoài phạm vi đoạn vật lý "
            f"[{doan.ly_trinh_dau}–{doan.ly_trinh_cuoi}]."
        )


def _tao_ma_doan_di_chung(
    conn: sqlite3.Connection,
    tuyen_di_chung_id: int,
    tuyen_chinh_id: int,
    doan_id: int,
) -> str:
    """Sinh mã tự động: DDC-{MA_TUYEN_DI_CHUNG}-{MA_DOAN}-{STT:03d}"""
    tuyen_di_chung = tuyen_duong_repo.lay_theo_id(conn, tuyen_di_chung_id)
    doan = doan_tuyen_repo.lay_theo_id(conn, doan_id)
    so_hien_co = len(doan_di_chung_repo.lay_theo_doan_id(conn, doan_id))
    stt = so_hien_co + 1
    return f"DDC-{tuyen_di_chung.ma_tuyen}-{doan.ma_doan}-{stt:03d}"
