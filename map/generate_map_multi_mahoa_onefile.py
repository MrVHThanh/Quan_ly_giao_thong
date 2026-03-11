"""
generate_map_multi.py  (v3 — file HTML duy nhất, dữ liệu mã hóa tích hợp)
---------------------------------------------------------------------------
Tạo bản đồ HTML từ nhiều file GeoJSON tuyến đường.
Toàn bộ dữ liệu mã hóa được nhúng thẳng vào HTML — chỉ cần 1 file duy nhất.

Cơ chế bảo vệ tọa độ (3 lớp):
  1. Delta encoding   — lưu hiệu số thay vì tọa độ tuyệt đối
  2. XOR cipher       — XOR từng byte với key ngẫu nhiên 32 byte
  3. Base64 encode    — chuỗi kết quả trông như văn bản ngẫu nhiên

Output: 1 file HTML duy nhất, mở thẳng bằng trình duyệt.

Cách dùng:
    python generate_map_multi.py
    python generate_map_multi.py --input QL4E_merged.geojson TL158_merged.geojson
    python generate_map_multi.py --output ban_do.html
"""

import json
import argparse
import glob
import os
import base64
import secrets
from math import radians, sin, cos, sqrt, atan2


# ── Bảng màu ──────────────────────────────────────────────────────
ROUTE_COLORS = [
    "#f0a500", "#38bdf8", "#4ade80", "#f472b6",
    "#a78bfa", "#fb923c", "#34d399", "#f87171",
]

DEFAULT_HTML   = "Giao_thong_map_onefile.html"
PRECISION      = 6      # số chữ số thập phân giữ lại (≈ 0.1m)
SCALE          = 10 ** PRECISION


# ── Haversine ─────────────────────────────────────────────────────
def haversine_km(c1, c2):
    R = 6371.0
    lon1, lat1, lon2, lat2 = c1[0], c1[1], c2[0], c2[1]
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def total_length_km(coords):
    return round(sum(haversine_km(coords[i], coords[i+1])
                     for i in range(len(coords)-1)), 3)


# ── Đọc GeoJSON ───────────────────────────────────────────────────
def load_geojson(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_coords(geometry):
    if geometry["type"] == "LineString":
        return geometry["coordinates"]
    elif geometry["type"] == "MultiLineString":
        merged = []
        for seg in geometry["coordinates"]:
            merged.extend(seg)
        return merged
    raise ValueError(f"Geometry không hỗ trợ: {geometry['type']}")


# ══════════════════════════════════════════════════════════════════
#  BẢO VỆ DỮ LIỆU
# ══════════════════════════════════════════════════════════════════

def delta_encode(coords):
    """
    Lớp 1 — Delta encoding
    Thay vì lưu [lon, lat] tuyệt đối, lưu hiệu số nguyên so với điểm trước.
    Ví dụ: [(104.123456, 22.345678), (104.123789, 22.345901)]
           → [(1041234560, 223456780), (333, 223)]   (nhân SCALE rồi lấy delta)
    Lợi ích:
      - Giá trị nhỏ hơn nhiều → nén tốt hơn
      - Không thể đọc tọa độ thật trực tiếp từ từng số
    """
    result = []
    prev_lon = 0
    prev_lat = 0
    for lon, lat in coords:
        ilon = round(lon * SCALE)
        ilat = round(lat * SCALE)
        result.append(ilon - prev_lon)
        result.append(ilat - prev_lat)
        prev_lon = ilon
        prev_lat = ilat
    return result


def xor_encrypt(data_bytes: bytes, key: bytes) -> bytes:
    """
    Lớp 2 — XOR cipher với key 32 byte ngẫu nhiên
    Mỗi lần chạy script sinh key mới → cùng dữ liệu cho kết quả khác nhau.
    """
    key_len = len(key)
    return bytes(b ^ key[i % key_len] for i, b in enumerate(data_bytes))


def encode_route(coords, key: bytes) -> str:
    """
    Lớp 3 — Base64
    Áp dụng đủ 3 lớp: delta → pack → XOR → base64
    Kết quả: chuỗi ASCII trông như văn bản ngẫu nhiên, không lộ số tọa độ.
    """
    deltas   = delta_encode(coords)
    # Pack thành JSON nhỏ gọn (có thể thay bằng msgpack nếu muốn nhỏ hơn nữa)
    raw_json = json.dumps(deltas, separators=(",", ":")).encode("utf-8")
    encrypted = xor_encrypt(raw_json, key)
    return base64.b64encode(encrypted).decode("ascii")


def decode_js_function(key_hex: str) -> str:
    """
    Trả về đoạn JS thực hiện giải mã ngược:
    base64 → XOR → delta decode → [[lon, lat], ...]
    Hàm này nhúng vào HTML, KHÔNG nhúng key vào đây.
    Key được load từ file data riêng.
    """
    return f"""
// ── Giải mã tọa độ ──────────────────────────────────────────────
// Key được load từ routes_data.js (file riêng biệt)
const _SCALE = {SCALE};

function _b64ToBytes(b64) {{
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}}

function _xorDecrypt(buf, key) {{
  const out = new Uint8Array(buf.length);
  for (let i = 0; i < buf.length; i++) out[i] = buf[i] ^ key[i % key.length];
  return out;
}}

function _deltaDecodeCoords(deltas) {{
  const coords = [];
  let plon = 0, plat = 0;
  for (let i = 0; i < deltas.length; i += 2) {{
    plon += deltas[i];
    plat += deltas[i+1];
    coords.push([plon / _SCALE, plat / _SCALE]);
  }}
  return coords;
}}

function decodeRoute(b64, key) {{
  const encrypted = _b64ToBytes(b64);
  const decrypted = _xorDecrypt(encrypted, key);
  const jsonStr   = new TextDecoder().decode(decrypted);
  const deltas    = JSON.parse(jsonStr);
  return _deltaDecodeCoords(deltas);
}}
"""


# ══════════════════════════════════════════════════════════════════
#  SINH HTML
# ══════════════════════════════════════════════════════════════════

def generate_html(route_metas, key: bytes) -> str:

    center_lat = sum(c[1] for m in route_metas for c in m["coords"]) / sum(m["total_pts"] for m in route_metas)
    center_lon = sum(c[0] for m in route_metas for c in m["coords"]) / sum(m["total_pts"] for m in route_metas)
    total_all_km = round(sum(m["length_km"] for m in route_metas), 3)

    # Sidebar route items
    sidebar_items = ""
    for i, m in enumerate(route_metas):
        c = m["color"]
        sidebar_items += f"""
        <div class="route-item" id="route-item-{i}" onclick="focusRoute({i})">
          <div class="route-dot" style="background:{c};box-shadow:0 0 8px {c}80"></div>
          <div class="route-info">
            <div class="route-name">{m['road_name']}</div>
            <div class="route-meta">{m['length_km']} km &nbsp;·&nbsp; {m['total_pts']:,} điểm GPS</div>
          </div>
          <div class="route-badge" style="color:{c};border-color:{c}40;background:{c}15">{i+1}</div>
        </div>"""

    # Dữ liệu mã hóa nhúng thẳng vào HTML
    key_array = list(key)
    encoded_routes = []
    for m in route_metas:
        encoded_routes.append({
            "road_name": m["road_name"],
            "length_km": m["length_km"],
            "total_pts": m["total_pts"],
            "color":     m["color"],
            "enc":       encode_route(m["coords"], key),
        })
    key_js      = json.dumps(key_array)
    routes_json = json.dumps(encoded_routes, ensure_ascii=False, separators=(",", ":"))

    inline_data = f"""const _ROUTE_KEY = new Uint8Array({key_js});
const ROUTES_ENC = {routes_json};"""

    decode_js = decode_js_function(key.hex())

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bản đồ tuyến đường — Lào Cai</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
  <!-- Dữ liệu tuyến đường nhúng inline (đã mã hóa 3 lớp: Delta + XOR + Base64) -->
  <script>
const _ROUTE_KEY = new Uint8Array({key_js});
const ROUTES_ENC = {routes_json};
  </script>
  <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --bg: #0d1117; --panel: #161b22; --border: #30363d;
      --accent: #f0a500; --text: #e6edf3; --muted: #7d8590;
    }}
    html, body {{ height: 100%; font-family: 'Be Vietnam Pro', sans-serif; background: var(--bg); color: var(--text); overflow: hidden; }}
    #app {{ display: flex; height: 100vh; width: 100vw; position: relative; }}

    /* ── Sidebar ── */
    #sidebar {{
      width: 310px; min-width: 310px;
      background: var(--panel); border-right: 1px solid var(--border);
      display: flex; flex-direction: column; z-index: 1000; overflow: hidden;
      transition: transform .3s cubic-bezier(.4,0,.2,1), margin .3s cubic-bezier(.4,0,.2,1);
      flex-shrink: 0;
    }}
    #sidebar.collapsed {{ transform: translateX(-100%); margin-right: -310px; }}

    /* ── Nút toggle sidebar ── */
    #sidebar-toggle {{
      position: absolute; top: 14px; left: 258px; z-index: 1100;
      width: 38px; height: 38px;
      background: var(--panel); border: 1px solid var(--border);
      border-radius: 10px; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      transition: left .3s cubic-bezier(.4,0,.2,1), border-color .2s, color .2s;
      box-shadow: 0 4px 16px rgba(0,0,0,.5); color: var(--text);
    }}
    #sidebar-toggle:hover {{ border-color: var(--accent); color: var(--accent); }}
    #sidebar-toggle svg {{ width: 17px; height: 17px; stroke: currentColor; fill: none; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round; }}
    #app.sb-collapsed #sidebar-toggle {{ left: 14px; }}

    /* ── Overlay mobile ── */
    #sidebar-overlay {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,.55); z-index: 999; }}
    #sidebar-overlay.visible {{ display: block; }}

    @media (max-width: 680px) {{
      #sidebar {{
        position: absolute; top: 0; left: 0; bottom: 0;
        margin-right: 0 !important; box-shadow: 4px 0 32px rgba(0,0,0,.7);
      }}
      #sidebar.collapsed {{ transform: translateX(-100%); box-shadow: none; }}
      #sidebar-toggle {{ left: 258px; }}
      #app.sb-collapsed #sidebar-toggle {{ left: 14px; }}
    }}

    #sidebar-header {{
      padding: 20px 56px 16px 22px; border-bottom: 1px solid var(--border);
      background: linear-gradient(135deg, #1a1f2e 0%, var(--panel) 100%);
    }}
    .tag-road {{
      display: inline-block; font-family: 'Space Mono', monospace;
      font-size: 10px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase;
      color: var(--accent); background: rgba(240,165,0,.12);
      border: 1px solid rgba(240,165,0,.3); border-radius: 3px; padding: 3px 8px; margin-bottom: 10px;
    }}
    #sidebar-header h1 {{ font-size: 20px; font-weight: 700; line-height: 1.25; margin-bottom: 4px; }}
    #sidebar-header .subtitle {{ font-size: 12px; color: var(--muted); font-weight: 300; }}

    #summary {{
      padding: 16px 22px; border-bottom: 1px solid var(--border);
      display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
    }}
    .stat-card {{
      background: rgba(255,255,255,.03); border: 1px solid var(--border);
      border-radius: 8px; padding: 12px 14px; transition: border-color .2s;
    }}
    .stat-card:hover {{ border-color: var(--accent); }}
    .stat-label {{ font-size: 10px; text-transform: uppercase; letter-spacing: .1em; color: var(--muted); font-family: 'Space Mono',monospace; margin-bottom: 5px; }}
    .stat-value {{ font-size: 20px; font-weight: 700; color: var(--accent); font-family: 'Space Mono',monospace; line-height: 1; }}
    .stat-unit  {{ font-size: 11px; color: var(--muted); margin-top: 3px; }}

    #routes-section {{ padding: 14px 22px; border-bottom: 1px solid var(--border); overflow-y: auto; flex: 1; }}
    .section-title {{ font-size: 10px; text-transform: uppercase; letter-spacing: .12em; color: var(--muted); font-family: 'Space Mono',monospace; margin-bottom: 12px; }}
    .route-item {{
      display: flex; align-items: center; gap: 12px; padding: 10px 12px;
      border-radius: 8px; cursor: pointer; border: 1px solid transparent;
      transition: all .2s; margin-bottom: 8px;
    }}
    .route-item:hover {{ background: rgba(255,255,255,.04); border-color: var(--border); }}
    .route-item.active {{ background: rgba(255,255,255,.06); border-color: var(--border); }}
    .route-dot {{ width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }}
    .route-info {{ flex: 1; min-width: 0; }}
    .route-name {{ font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .route-meta {{ font-size: 11px; color: var(--muted); margin-top: 2px; font-family: 'Space Mono',monospace; }}
    .route-badge {{
      font-family: 'Space Mono',monospace; font-size: 11px; font-weight: 700;
      padding: 2px 8px; border-radius: 4px; border: 1px solid; flex-shrink: 0;
    }}

    #controls {{ padding: 14px 22px; display: flex; flex-direction: column; gap: 9px; border-bottom: 1px solid var(--border); }}
    .ctrl-row {{ display: flex; align-items: center; justify-content: space-between; }}
    .ctrl-label {{ font-size: 12px; color: var(--muted); }}
    .toggle-btn {{
      cursor: pointer; width: 36px; height: 20px; background: var(--border);
      border-radius: 10px; position: relative; transition: background .25s; border: none; outline: none;
    }}
    .toggle-btn.active {{ background: var(--accent); }}
    .toggle-btn::after {{
      content: ''; position: absolute; top: 3px; left: 3px;
      width: 14px; height: 14px; background: white; border-radius: 50%; transition: transform .25s;
    }}
    .toggle-btn.active::after {{ transform: translateX(16px); }}
    .fit-btn {{
      background: rgba(240,165,0,.1); border: 1px solid rgba(240,165,0,.4);
      color: var(--accent); padding: 4px 14px; border-radius: 5px;
      cursor: pointer; font-size: 12px; font-family: 'Be Vietnam Pro',sans-serif;
    }}
    .fit-btn:hover {{ background: rgba(240,165,0,.2); }}

    #basemap-section {{ padding: 14px 22px; }}
    .basemap-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 8px; }}
    .bm-btn {{
      padding: 7px 4px; background: rgba(255,255,255,.03); border: 1px solid var(--border);
      border-radius: 6px; color: var(--muted); font-size: 11px;
      font-family: 'Be Vietnam Pro',sans-serif; cursor: pointer; text-align: center; transition: all .2s;
    }}
    .bm-btn:hover {{ border-color: var(--accent); color: var(--text); }}
    .bm-btn.active {{ border-color: var(--accent); color: var(--accent); background: rgba(240,165,0,.08); }}

    #map {{ flex: 1; position: relative; }}
    .leaflet-tile-pane {{ filter: brightness(.85) saturate(.9); }}
    .leaflet-control-zoom a {{ background: var(--panel)!important; color: var(--text)!important; border-color: var(--border)!important; }}
    .leaflet-control-attribution {{ background: rgba(13,17,23,.8)!important; color: var(--muted)!important; font-size: 10px!important; }}
    .leaflet-popup-content-wrapper {{ background: var(--panel); border: 1px solid var(--border); border-radius: 10px; color: var(--text); box-shadow: 0 8px 32px rgba(0,0,0,.5); }}
    .leaflet-popup-tip {{ background: var(--panel); }}
    .popup-inner h3 {{ font-size: 14px; font-weight: 700; margin-bottom: 10px; font-family: 'Space Mono',monospace; }}
    .popup-inner table {{ width: 100%; font-size: 12px; border-collapse: collapse; }}
    .popup-inner td {{ padding: 4px 0; color: var(--muted); }}
    .popup-inner td:last-child {{ color: var(--text); text-align: right; font-weight: 600; }}

    #hover-info {{
      position: absolute; bottom: 28px; right: 16px;
      background: var(--panel); border: 1px solid var(--border); border-radius: 8px;
      padding: 9px 13px; font-size: 12px; color: var(--muted); z-index: 500;
      pointer-events: none; opacity: 0; transition: opacity .2s; font-family: 'Space Mono',monospace;
    }}
    #hover-info.visible {{ opacity: 1; }}

    #loader {{
      position: absolute; inset: 0; background: var(--bg);
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      z-index: 9998; transition: opacity .5s;
    }}
    #loader.hidden {{ opacity: 0; pointer-events: none; }}
    .loader-ring {{
      width: 48px; height: 48px; border: 3px solid var(--border);
      border-top-color: var(--accent); border-radius: 50%;
      animation: spin .8s linear infinite; margin-bottom: 16px;
    }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    .loader-text {{ font-family: 'Space Mono',monospace; font-size: 12px; color: var(--muted); }}
  </style>
</head>
<body>

<div id="loader">
  <div class="loader-ring"></div>
  <div class="loader-text">Đang giải mã và tải bản đồ...</div>
</div>

<!-- Overlay mobile -->
<div id="sidebar-overlay" onclick="toggleSidebar()"></div>

<!-- Nút ẩn/hiện sidebar -->
<button id="sidebar-toggle" onclick="toggleSidebar()" title="Ẩn/hiện bảng thông tin">
  <svg id="toggle-icon-open"  viewBox="0 0 24 24"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
  <svg id="toggle-icon-close" viewBox="0 0 24 24" style="display:none"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
</button>

<div id="app">
  <aside id="sidebar">
    <div id="sidebar-header">
      <div class="tag-road">Tuyến đường · Lào Cai</div>
      <h1>Bản đồ tuyến đường</h1>
      <div class="subtitle">Tỉnh Lào Cai — {len(route_metas)} tuyến được hiển thị</div>
    </div>

    <div id="summary">
      <div class="stat-card">
        <div class="stat-label">Tổng chiều dài</div>
        <div class="stat-value">{total_all_km}</div>
        <div class="stat-unit">km tất cả tuyến</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Số tuyến</div>
        <div class="stat-value">{len(route_metas)}</div>
        <div class="stat-unit">tuyến đường</div>
      </div>
    </div>

    <div id="routes-section">
      <div class="section-title">Danh sách tuyến đường</div>
      {sidebar_items}
    </div>

    <div id="controls">
      <div class="section-title" style="margin-bottom:6px">Hiển thị</div>
      <div class="ctrl-row">
        <span class="ctrl-label">Hiệu ứng phát sáng</span>
        <button class="toggle-btn active" onclick="toggleGlow(this)"></button>
      </div>
      <div class="ctrl-row">
        <span class="ctrl-label">Điểm đầu / cuối</span>
        <button class="toggle-btn active" onclick="toggleMarkers(this)"></button>
      </div>
      <div class="ctrl-row">
        <span class="ctrl-label">Fit tất cả tuyến</span>
        <button class="fit-btn" onclick="fitAll()">Zoom về</button>
      </div>
    </div>

    <div id="basemap-section">
      <div class="section-title">Nền bản đồ</div>
      <div class="basemap-grid">
        <button class="bm-btn active" onclick="setBasemap('osm',this)">OSM</button>
        <button class="bm-btn" onclick="setBasemap('topo',this)">Topo</button>
        <button class="bm-btn" onclick="setBasemap('satellite',this)">Vệ tinh</button>
      </div>
    </div>
  </aside>

  <div id="map">
    <div id="hover-info">
      📍 <span id="hover-coord">—</span>
      <span id="hover-dist-wrap" style="display:none">
        &nbsp;|&nbsp; 📏 <span id="hover-dist" style="font-weight:700">—</span> km từ đầu tuyến
      </span>
    </div>
  </div>
</div>

<script>
{decode_js}

// ── Giải mã tất cả tuyến ─────────────────────────────────────────
const ROUTES = ROUTES_ENC.map(r => ({{
  road_name: r.road_name,
  length_km: r.length_km,
  total_pts: r.total_pts,
  color:     r.color,
  coords:    decodeRoute(r.enc, _ROUTE_KEY),
}}));

// ── Bản đồ ───────────────────────────────────────────────────────
const TILES = {{
  osm:       L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{ maxZoom:19, attribution:'© OpenStreetMap' }}),
  topo:      L.tileLayer('https://{{s}}.tile.opentopomap.org/{{z}}/{{x}}/{{y}}.png',  {{ maxZoom:17, attribution:'© OpenTopoMap' }}),
  satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{ attribution:'© Esri' }}),
}};
const map = L.map('map', {{ center: [{center_lat:.6f}, {center_lon:.6f}], zoom: 10, layers: [TILES.osm] }});

// ── Haversine ─────────────────────────────────────────────────────
function haversineKm(a, b) {{
  const R = 6371, toRad = x => x * Math.PI / 180;
  const dLat = toRad(b[0]-a[0]), dLon = toRad(b[1]-a[1]);
  const s = Math.sin(dLat/2), c = Math.sin(dLon/2);
  const h = s*s + Math.cos(toRad(a[0]))*Math.cos(toRad(b[0]))*c*c;
  return R * 2 * Math.atan2(Math.sqrt(h), Math.sqrt(1-h));
}}

function nearestOnLine(latlng, latLngs, cumulDist) {{
  const px = latlng.lat, py = latlng.lng;
  let bestD = Infinity, bestI = 0, bestT = 0;
  for (let i = 0; i < latLngs.length-1; i++) {{
    const ax=latLngs[i][0], ay=latLngs[i][1], bx=latLngs[i+1][0], by=latLngs[i+1][1];
    const dx=bx-ax, dy=by-ay, lsq=dx*dx+dy*dy;
    let t = lsq > 0 ? ((px-ax)*dx+(py-ay)*dy)/lsq : 0;
    t = Math.max(0, Math.min(1, t));
    const d = (px-ax-t*dx)**2 + (py-ay-t*dy)**2;
    if (d < bestD) {{ bestD=d; bestI=i; bestT=t; }}
  }}
  const seg  = haversineKm(latLngs[bestI], latLngs[bestI+1]);
  const dist = cumulDist[bestI] + bestT * seg;
  const pLat = latLngs[bestI][0] + bestT*(latLngs[bestI+1][0]-latLngs[bestI][0]);
  const pLng = latLngs[bestI][1] + bestT*(latLngs[bestI+1][1]-latLngs[bestI][1]);
  return {{ dist, pLat, pLng, bestD }};
}}

// ── Vẽ tuyến ─────────────────────────────────────────────────────
const routeLayers = [];
const allBounds   = [];
let glowOn = true, markersOn = true;

const mkIcon = color => L.divIcon({{
  html: `<div style="width:14px;height:14px;border-radius:50%;background:${{color}};border:2px solid white;box-shadow:0 0 8px ${{color}}"></div>`,
  iconSize:[14,14], iconAnchor:[7,7], className:'',
}});
const snapIcon = L.divIcon({{
  html: `<div style="width:12px;height:12px;border-radius:50%;background:#fff;border:2.5px solid #f0a500;box-shadow:0 0 6px rgba(240,165,0,.8)"></div>`,
  iconSize:[12,12], iconAnchor:[6,6], className:'',
}});
const snapMarker = L.marker([0,0], {{ icon: snapIcon, interactive: false }});
let snapActive = false;

ROUTES.forEach((r) => {{
  const latLngs = r.coords.map(c => [c[1], c[0]]);
  const color   = r.color;

  const cumulDist = new Float64Array(latLngs.length);
  for (let i=1; i<latLngs.length; i++)
    cumulDist[i] = cumulDist[i-1] + haversineKm(latLngs[i-1], latLngs[i]);
  const totalKm = cumulDist[cumulDist.length-1];

  const glowLine  = L.polyline(latLngs, {{ color: color+'30', weight:14, lineCap:'round', lineJoin:'round' }}).addTo(map);
  const routeLine = L.polyline(latLngs, {{ color, weight:3.5, opacity:.95, lineCap:'round', lineJoin:'round' }}).addTo(map);
  const startM    = L.marker(latLngs[0], {{icon: mkIcon('#4ade80')}}).bindTooltip(`Đầu tuyến: ${{r.road_name}}`).addTo(map);
  const endM      = L.marker(latLngs[latLngs.length-1], {{icon: mkIcon('#f87171')}}).bindTooltip(`Cuối tuyến: ${{r.road_name}}`).addTo(map);
  const markerGroup = L.layerGroup([startM, endM]).addTo(map);

  allBounds.push(routeLine.getBounds());

  routeLine.on('click', function(e) {{
    L.DomEvent.stopPropagation(e);
    const {{ dist, pLat, pLng }} = nearestOnLine(e.latlng, latLngs, cumulDist);
    const pct = (dist/totalKm*100).toFixed(1);
    L.popup({{ maxWidth:300 }})
      .setLatLng([pLat, pLng])
      .setContent(`<div class="popup-inner">
        <h3 style="color:${{color}}">📏 ${{r.road_name}}</h3>
        <table>
          <tr><td>Từ đầu tuyến</td><td style="color:${{color}}">${{dist.toFixed(3)}} km</td></tr>
          <tr><td>Còn lại đến cuối</td><td>${{(totalKm-dist).toFixed(3)}} km</td></tr>
          <tr><td>Tỷ lệ</td><td>${{pct}}% toàn tuyến</td></tr>
          <tr><td>Tổng chiều dài</td><td>${{r.length_km}} km</td></tr>
        </table>
      </div>`)
      .openOn(map);
  }});

  routeLayers.push({{ glowLine, routeLine, markerGroup, latLngs, cumulDist, totalKm, color, name: r.road_name }});
}});

function fitAll() {{
  if (!allBounds.length) return;
  let b = allBounds[0];
  for (let i=1; i<allBounds.length; i++) b = b.extend(allBounds[i]);
  map.fitBounds(b, {{ padding:[40,40], animate:true, duration:.8 }});
}}
fitAll();

function focusRoute(idx) {{
  map.fitBounds(routeLayers[idx].routeLine.getBounds(), {{ padding:[50,50], animate:true, duration:.8 }});
  document.querySelectorAll('.route-item').forEach((el,i) => el.classList.toggle('active', i===idx));
}}

// ── Hover ─────────────────────────────────────────────────────────
const hoverInfo     = document.getElementById('hover-info');
const hoverCoord    = document.getElementById('hover-coord');
const hoverDist     = document.getElementById('hover-dist');
const hoverDistWrap = document.getElementById('hover-dist-wrap');

map.on('mousemove', function(e) {{
  hoverInfo.classList.add('visible');
  hoverCoord.textContent = e.latlng.lat.toFixed(5)+'° N,  '+e.latlng.lng.toFixed(5)+'° E';
  let best = null, bestVal = Infinity;
  for (const rl of routeLayers) {{
    const res = nearestOnLine(e.latlng, rl.latLngs, rl.cumulDist);
    if (res.bestD < bestVal) {{ bestVal = res.bestD; best = {{...res, rl}}; }}
  }}
  if (best && Math.sqrt(best.bestD) < 0.015) {{
    hoverDistWrap.style.display = 'inline';
    hoverDist.textContent = best.dist.toFixed(3);
    hoverDist.style.color = best.rl.color;
    snapMarker.setLatLng([best.pLat, best.pLng]);
    if (!snapActive) {{ snapMarker.addTo(map); snapActive = true; }}
  }} else {{
    hoverDistWrap.style.display = 'none';
    if (snapActive) {{ map.removeLayer(snapMarker); snapActive = false; }}
  }}
}});
map.on('mouseout', function() {{
  hoverInfo.classList.remove('visible');
  if (snapActive) {{ map.removeLayer(snapMarker); snapActive = false; }}
}});

map.on('click', function(e) {{
  let best = null, bestVal = Infinity;
  for (const rl of routeLayers) {{
    const res = nearestOnLine(e.latlng, rl.latLngs, rl.cumulDist);
    if (res.bestD < bestVal) {{ bestVal = res.bestD; best = {{...res, rl}}; }}
  }}
  if (!best || Math.sqrt(best.bestD) > 0.03) return;
  const rl = best.rl;
  L.popup({{ maxWidth:300 }})
    .setLatLng([best.pLat, best.pLng])
    .setContent(`<div class="popup-inner">
      <h3 style="color:${{rl.color}}">📏 ${{rl.name}}</h3>
      <table>
        <tr><td>Từ đầu tuyến</td><td style="color:${{rl.color}}">${{best.dist.toFixed(3)}} km</td></tr>
        <tr><td>Còn lại đến cuối</td><td>${{(rl.totalKm-best.dist).toFixed(3)}} km</td></tr>
        <tr><td>Tỷ lệ</td><td>${{(best.dist/rl.totalKm*100).toFixed(1)}}% toàn tuyến</td></tr>
      </table>
    </div>`)
    .openOn(map);
}});

// ── Điều khiển ───────────────────────────────────────────────────
function toggleGlow(btn) {{
  glowOn = !glowOn; btn.classList.toggle('active', glowOn);
  routeLayers.forEach(rl => glowOn ? map.addLayer(rl.glowLine) : map.removeLayer(rl.glowLine));
}}
function toggleMarkers(btn) {{
  markersOn = !markersOn; btn.classList.toggle('active', markersOn);
  routeLayers.forEach(rl => markersOn ? map.addLayer(rl.markerGroup) : map.removeLayer(rl.markerGroup));
}}
let currentTile = TILES.osm;
function setBasemap(name, btn) {{
  map.removeLayer(currentTile); currentTile = TILES[name]; map.addLayer(currentTile);
  currentTile.bringToBack();
  document.querySelectorAll('.bm-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}}

// ── Sidebar toggle ────────────────────────────────────────────────
const appEl     = document.getElementById('app');
const sidebarEl = document.getElementById('sidebar');
const overlay   = document.getElementById('sidebar-overlay');
const iconOpen  = document.getElementById('toggle-icon-open');
const iconClose = document.getElementById('toggle-icon-close');
let sidebarOpen = true;

function toggleSidebar() {{
  sidebarOpen = !sidebarOpen;
  sidebarEl.classList.toggle('collapsed', !sidebarOpen);
  appEl.classList.toggle('sb-collapsed', !sidebarOpen);
  overlay.classList.toggle('visible', sidebarOpen && window.innerWidth <= 680);
  iconOpen.style.display  = sidebarOpen ? 'none' : '';
  iconClose.style.display = sidebarOpen ? ''     : 'none';
  setTimeout(() => map.invalidateSize(), 320);
}}
if (window.innerWidth <= 680) {{ sidebarOpen = true; toggleSidebar(); }}

window.addEventListener('load', () => {{
  setTimeout(() => document.getElementById('loader').classList.add('hidden'), 800);
}});
</script>
</body>
</html>"""


# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Tạo bản đồ HTML (1 file) từ nhiều GeoJSON — dữ liệu tọa độ được mã hóa inline"
    )
    parser.add_argument("--input",  "-i", nargs="+", metavar="FILE",
        help="Các file GeoJSON. Mặc định: tất cả *.geojson trong thư mục hiện tại")
    parser.add_argument("--output", "-o", default=DEFAULT_HTML,
        help=f"File HTML đầu ra (mặc định: {DEFAULT_HTML})")
    args = parser.parse_args()

    # Tìm file GeoJSON
    if args.input:
        input_files = args.input
    else:
        input_files = sorted(glob.glob("*.geojson"))
        if not input_files:
            print("❌ Không tìm thấy file .geojson nào.")
            print("   Dùng: python generate_map_multi.py --input file1.geojson file2.geojson")
            return

    print(f"📍 Xử lý {len(input_files)} file GeoJSON:\n")

    routes = []
    for idx, fpath in enumerate(input_files):
        if not os.path.exists(fpath):
            print(f"  ⚠️  Không tìm thấy: {fpath} — bỏ qua")
            continue
        color   = ROUTE_COLORS[idx % len(ROUTE_COLORS)]
        geojson = load_geojson(fpath)
        feat    = geojson["features"][0]
        props   = feat["properties"]
        coords  = extract_coords(feat["geometry"])
        name    = props.get("road_name") or props.get("name") or os.path.splitext(os.path.basename(fpath))[0]
        lkm     = props.get("length_km", total_length_km(coords))
        pts     = len(coords)
        routes.append({
            "road_name": name,
            "length_km": lkm,
            "total_pts": pts,
            "coords":    coords,
            "color":     color,
        })
        print(f"  [{idx+1}] {name}")
        print(f"       Chiều dài : {lkm} km")
        print(f"       Số điểm   : {pts:,} tọa độ GPS")
        print(f"       Màu       : {color}\n")

    if not routes:
        print("❌ Không có file hợp lệ.")
        return

    # Sinh key ngẫu nhiên (32 byte) — mỗi lần build khác nhau
    key = secrets.token_bytes(32)
    print(f"🔑 Sinh key ngẫu nhiên : {key.hex()[:16]}...  (32 bytes)")
    print(f"🔐 Đang mã hóa tọa độ (Delta → XOR → Base64)...")

    html = generate_html(routes, key)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✅ Hoàn thành!")
    print(f"   📄 {args.output}  ({len(html)/1024:.1f} KB) — 1 file duy nhất, mở bằng trình duyệt là dùng được.")


if __name__ == "__main__":
    main()
