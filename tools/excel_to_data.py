"""
Tool: excel_to_data.py
Đọc file Excel và sinh lại 9 file data/*.py.

Cách dùng:
    python tools/excel_to_data.py
    python tools/excel_to_data.py --excel data/giao_thong_data_upadate.xlsx
    python tools/excel_to_data.py --excel data/giao_thong_data_upadate.xlsx --out data/
"""

import argparse
import math
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

EXCEL_MAC_DINH = os.path.join(_ROOT, "data", "giao_thong_data_upadate.xlsx")
OUT_MAC_DINH   = os.path.join(_ROOT, "data")


def v(val):
    if val is None:
        return None
    try:
        if math.isnan(float(val)):
            return None
    except Exception:
        pass
    s = str(val).strip()
    return None if s in ("", "nan", "NaN", "None") else s


def vf(val):
    x = v(val)
    return round(float(x), 3) if x is not None else None


def vi(val):
    x = v(val)
    return int(float(x)) if x is not None else None


def sinh_tat_ca(excel_path: str, out_dir: str) -> None:
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("Cần cài pandas: pip install pandas openpyxl")

    sheets = pd.read_excel(excel_path, sheet_name=None)
    os.makedirs(out_dir, exist_ok=True)

    _sinh_cap_quan_ly(sheets["CapQuanLy"].dropna(how="all"), out_dir)
    _sinh_cap_duong(sheets["CapDuong"].dropna(how="all"), out_dir)
    _sinh_ket_cau_mat(sheets["KetCauMat"].dropna(how="all"), out_dir)
    _sinh_tinh_trang(sheets["TinhTrang"].dropna(how="all"), out_dir)
    _sinh_don_vi(sheets["DonVi"].dropna(how="all"), out_dir)
    _sinh_nguoi_dung(sheets["NguoiDung"].dropna(how="all"), out_dir)
    _sinh_tuyen_duong(
        sheets["TuyenDuong"].dropna(how="all"),
        sheets["ThongTinTuyen"].dropna(how="all"),
        out_dir,
    )
    _sinh_doan_tuyen(sheets["DoanTuyen"].dropna(how="all"), out_dir)
    _sinh_doan_di_chung(sheets["DoanDiChung"].dropna(how="all"), out_dir)

    print(f"\n✓ Đã sinh 9 file data vào: {out_dir}\n")


def _ghi_file(out_dir: str, ten_file: str, noi_dung: str) -> None:
    path = os.path.join(out_dir, ten_file)
    with open(path, "w", encoding="utf-8") as f:
        f.write(noi_dung)
    print(f"  ✓ {ten_file}")


def _sinh_cap_quan_ly(df, out_dir):
    lines = ['"""\nData: CapQuanLy\nSinh tự động bởi tools/excel_to_data.py\n"""\n\nRECORDS = [']
    for _, r in df.iterrows():
        lines.append(f'    {{"ma_cap": {repr(v(r["ma_cap"]))}, "ten_cap": {repr(v(r["ten_cap"]))}, '
                     f'"mo_ta": {repr(v(r["mo_ta"]))}, "thu_tu_hien_thi": {repr(vi(r["thu_tu_hien_thi"]))}}},')
    lines.append("]")
    _ghi_file(out_dir, "cap_quan_ly_data.py", "\n".join(lines))


def _sinh_cap_duong(df, out_dir):
    lines = ['"""\nData: CapDuong\nSinh tự động bởi tools/excel_to_data.py\n"""\n\nRECORDS = [']
    for _, r in df.iterrows():
        ma_col = "Ma_cap" if "Ma_cap" in df.columns else "ma_cap"
        lines.append(f'    {{"ma_cap": {repr(v(r[ma_col]))}, "ten_cap": {repr(v(r["ten_cap"]))}, '
                     f'"mo_ta": {repr(v(r["mo_ta"]))}, "thu_tu_hien_thi": {repr(vi(r["thu_tu_hien_thi"]))}}},')
    lines.append("]")
    _ghi_file(out_dir, "cap_duong_data.py", "\n".join(lines))


def _sinh_ket_cau_mat(df, out_dir):
    lines = ['"""\nData: KetCauMat\nSinh tự động bởi tools/excel_to_data.py\n"""\n\nRECORDS = [']
    for _, r in df.iterrows():
        mo_ta = v(r["mo_ta"])
        if mo_ta:
            mo_ta = mo_ta.replace("\\n", "").strip()
        lines.append(f'    {{"ma_ket_cau": {repr(v(r["ma_ket_cau"]))}, "ten_ket_cau": {repr(v(r["ten_ket_cau"]))}, '
                     f'"mo_ta": {repr(mo_ta)}, "thu_tu_hien_thi": {repr(vi(r["thu_tu_hien_thi"]))}}},')
    lines.append("]")
    _ghi_file(out_dir, "ket_cau_mat_data.py", "\n".join(lines))


def _sinh_tinh_trang(df, out_dir):
    MAU = {
        "TOT": "#2ECC71", "TB": "#F39C12", "KEM": "#E67E22",
        "HH_NANG": "#E74C3C", "THI_CONG": "#3498DB", "BAO_TRI": "#9B59B6",
        "TAM_DONG": "#95A5A6", "NGUNG": "#7F8C8D", "CHUA_XD": "#BDC3C7",
    }
    lines = ['"""\nData: TinhTrang\nSinh tự động bởi tools/excel_to_data.py\n"""\n\nRECORDS = [']
    for i, (_, r) in enumerate(df.iterrows(), 1):
        ma = v(r["ma"])
        lines.append(f'    {{"ma_tinh_trang": {repr(ma)}, "ten_tinh_trang": {repr(v(r["ten"]))}, '
                     f'"mo_ta": {repr(v(r["mo_ta"]))}, '
                     f'"mau_hien_thi": {repr(MAU.get(ma))}, "thu_tu_hien_thi": {i}}},')
    lines.append("]")
    _ghi_file(out_dir, "tinh_trang_data.py", "\n".join(lines))


def _sinh_don_vi(df, out_dir):
    lines = ['"""\nData: DonVi\nSinh tự động bởi tools/excel_to_data.py\n"""\n\nRECORDS = [']
    for _, r in df.iterrows():
        parent = v(r["parent_id"])
        lines.append(f'    {{"ma_don_vi": {repr(v(r["Mã đơn vị"]))}, '
                     f'"ten_don_vi": {repr(v(r["Tên đơn vị"]))}, '
                     f'"cap_don_vi": {repr(v(r["Loại đơn vị"]))}, '
                     f'"parent_ma": {repr(parent)}, '
                     f'"ten_viet_tat": None, "dia_chi": None, "so_dien_thoai": None, "email": None}},')
    lines.append("]")
    _ghi_file(out_dir, "don_vi_data.py", "\n".join(lines))


def _sinh_nguoi_dung(df, out_dir):
    lines = [
        '"""\nData: NguoiDung\nSinh tự động bởi tools/excel_to_data.py\n"""\n\n'
        'MAT_KHAU_MAC_DINH = "Laocai@2024"\n\nRECORDS = ['
    ]
    loai_quyen = ["ADMIN", "BIEN_TAP", "BIEN_TAP"]
    for i, (_, r) in enumerate(df.iterrows()):
        ten = v(r["Họ và tên"]) or ""
        ten_dl = ten.lower().replace(" ", "").replace("ữ","u").replace("ọ","o") or f"user{i+1}"
        lines.append(f'    {{"ten_dang_nhap": {repr(ten_dl)}, '
                     f'"ho_ten": {repr(ten)}, '
                     f'"chuc_vu": {repr(v(r["Chức vụ"]))}, '
                     f'"don_vi_ma": {repr(v(r["Mã đơn vị"]))}, '
                     f'"so_dien_thoai": {repr("0" + str(int(r["Số điện thoại"])) if v(r["Số điện thoại"]) else None)}, '
                     f'"email": {repr(v(r["Email"]))}, '
                     f'"loai_quyen": {repr(loai_quyen[i] if i < len(loai_quyen) else "XEM")}}},')
    lines.append("]")
    _ghi_file(out_dir, "nguoi_dung_data.py", "\n".join(lines))


def _sinh_tuyen_duong(td_df, ttt_df, out_dir):
    ttt_map = {str(r["Mã tuyến"]).strip(): str(r["Thông tin mô tả"]).strip()
               for _, r in ttt_df.iterrows()}
    lines = ['"""\nData: TuyenDuong + ThongTinTuyen\nSinh tự động bởi tools/excel_to_data.py\n"""\n\nRECORDS = [']
    for _, r in td_df.iterrows():
        ma = str(r["Mã tuyến"]).strip()
        mo_ta = ttt_map.get(ma)
        lines.append(f'    {{')
        lines.append(f'        "ma_tuyen": {repr(ma)}, "ten_tuyen": {repr(v(r["Tên tuyến"]))},')
        lines.append(f'        "cap_quan_ly_ma": {repr(v(r["Cấp quản lý"]))}, "don_vi_quan_ly_ma": {repr(v(r["Đơn vị quản lý"]))},')
        lines.append(f'        "diem_dau": {repr(v(r["Điểm đầu"]))}, "diem_cuoi": {repr(v(r["Điểm cuối"]))},')
        lines.append(f'        "lat_dau": {repr(vf(r["Lat đầu"]))}, "lng_dau": {repr(vf(r["Lng đầu"]))},')
        lines.append(f'        "lat_cuoi": {repr(vf(r["Lat cuối"]))}, "lng_cuoi": {repr(vf(r["Lng cuối"]))},')
        lines.append(f'        "nam_xay_dung": {repr(vi(r["Năm xây dựng"]))}, "nam_hoan_thanh": {repr(vi(r["Năm hoàn thành"]))},')
        lines.append(f'        "ghi_chu": {repr(v(r["Ghi chú"]))}, "thong_tin_mo_ta": {repr(mo_ta)},')
        lines.append(f'    }},')
    lines.append("]")
    _ghi_file(out_dir, "tuyen_duong_data.py", "\n".join(lines))


def _sinh_doan_tuyen(df, out_dir):
    lines = ['"""\nData: DoanTuyen\nSinh tự động bởi tools/excel_to_data.py\n"""\n\nRECORDS = [']
    for _, r in df.iterrows():
        lines.append(f'    {{')
        lines.append(f'        "ma_doan": {repr(v(r["Mã đoạn"]))}, "tuyen_ma": {repr(v(r["Mã tuyến"]))},')
        lines.append(f'        "cap_duong_ma": {repr(v(r["Cấp đường"]))}, "tinh_trang_ma": {repr(v(r["Tình trạng"]))},')
        lines.append(f'        "ket_cau_mat_ma": {repr(v(r["Mã kết cấu mặt"]))},')
        lines.append(f'        "ly_trinh_dau": {repr(vf(r["Lý trình đầu (km)"]))}, "ly_trinh_cuoi": {repr(vf(r["Lý trình cuối (km)"]))},')
        lines.append(f'        "chieu_dai_thuc_te": {repr(vf(r["Chiều dài thực tế (km)"]))},')
        lines.append(f'        "chieu_rong_mat_min": {repr(vf(r["Rộng mặt min (m)"]))}, "chieu_rong_mat_max": {repr(vf(r["Rộng mặt max (m)"]))},')
        lines.append(f'        "chieu_rong_nen_min": {repr(vf(r["Rộng nền min (m)"]))}, "chieu_rong_nen_max": {repr(vf(r["Rộng nền max (m)"]))},')
        lines.append(f'        "don_vi_bao_duong_ma": {repr(v(r["Đơn vị bảo dưỡng"]))}, "ghi_chu": {repr(v(r["Ghi chú"]))},')
        lines.append(f'    }},')
    lines.append("]")
    _ghi_file(out_dir, "doan_tuyen_data.py", "\n".join(lines))


def _sinh_doan_di_chung(df, out_dir):
    lines = ['"""\nData: DoanDiChung\nSinh tự động bởi tools/excel_to_data.py\n"""\n\nRECORDS = [']
    for _, r in df.iterrows():
        lines.append(f'    {{')
        lines.append(f'        "tuyen_di_chung_ma": {repr(v(r["Tuyến đi chung"]))}, "tuyen_chinh_ma": {repr(v(r["Tuyến chính"]))},')
        lines.append(f'        "doan_ma": {repr(v(r["Mã đoạn (tuyến chủ)"]))},')
        lines.append(f'        "ly_trinh_dau_di_chung": {repr(vf(r["Lý trình đầu đi chung"]))}, "ly_trinh_cuoi_di_chung": {repr(vf(r["Lý trình cuối đi chung"]))},')
        lines.append(f'        "ly_trinh_dau_tuyen_chinh": {repr(vf(r["Lý trình đầu tuyến chính"]))}, "ly_trinh_cuoi_tuyen_chinh": {repr(vf(r["Lý trình cuối tuyến chính"]))},')
        lines.append(f'        "ghi_chu": {repr(v(r["Ghi chú"]))},')
        lines.append(f'    }},')
    lines.append("]")
    _ghi_file(out_dir, "doan_di_chung_data.py", "\n".join(lines))


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Sinh 9 file data/*.py từ Excel")
    parser.add_argument("--excel", default=EXCEL_MAC_DINH, help="Đường dẫn file Excel")
    parser.add_argument("--out",   default=OUT_MAC_DINH,   help="Thư mục xuất data files")
    args = parser.parse_args()

    print(f"\nĐọc Excel: {args.excel}")
    sinh_tat_ca(args.excel, args.out)


if __name__ == "__main__":
    main()
