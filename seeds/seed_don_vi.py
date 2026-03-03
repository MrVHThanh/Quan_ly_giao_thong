from models.don_vi import DonVi
from services.don_vi_service import get_or_create_don_vi


def seed_don_vi():

    # 1️⃣ Sở GTVT
    so = get_or_create_don_vi(DonVi(
        ma_don_vi="SXD",
        ten_don_vi="Sở Xây dựng Lào Cai",
        loai="So"
    ))

    # 2️⃣ Ban Bảo trì
    ban = get_or_create_don_vi(DonVi(
        ma_don_vi="BAN_BT",
        ten_don_vi="Ban Bảo trì đường bộ",
        loai="Ban",
        parent_id=so.id
    ))

    # 3️⃣ Công ty bảo trì
    cong_ty = get_or_create_don_vi(DonVi(
        ma_don_vi="CTY_MD",
        ten_don_vi="Công ty Minh Đức",
        loai="Donvi",
        parent_id=ban.id
    ))

    # 3️⃣ Công ty bảo trì
    cong_ty_2 = get_or_create_don_vi(DonVi(
        ma_don_vi="CTY_BT",
        ten_don_vi="Công ty bảo trì đường bộ",
        loai="Donvi",
        parent_id=ban.id
    ))    

    return {
        "so": so,
        "ban": ban,
        "cong_ty": cong_ty,
        "cong_ty_2": cong_ty_2
    }