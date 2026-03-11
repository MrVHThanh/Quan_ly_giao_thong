"""
generate_map_multi.py
---------------------
Đọc 02 hoặc nhiều file GeoJSON tuyến đường và tạo ra một file HTML bản đồ
OpenStreetMap duy nhất, mỗi tuyến có màu riêng và tương tác độc lập.

Cách dùng:
    # Tự động tìm tất cả .geojson trong thư mục hiện tại:
    python generate_map_multi.py

    # Chỉ định rõ từng file:
    python generate_map_multi.py --input QL4E_merged.geojson TL158_merged.geojson

    # Tuỳ chỉnh tên file đầu ra:
    python generate_map_multi.py --output ban_do_tuyen_duong.html
"""

import json
import argparse
import glob
import os
from math import radians, sin, cos, sqrt, atan2


# ── Bảng màu cho từng tuyến ───────────────────────────────────────
ROUTE_COLORS = [
    "#f0a500",  # vàng amber
    "#38bdf8",  # xanh trời
    "#4ade80",  # xanh lá
    "#f472b6",  # hồng
    "#a78bfa",  # tím
    "#fb923c",  # cam
    "#34d399",  # ngọc
    "#f87171",  # đỏ nhạt
]

DEFAULT_OUTPUT = "ban_do_nhieu_tuyen.html"


# ── Hàm tính chiều dài ────────────────────────────────────────────
def haversine_km(coord1, coord2):
    R = 6371.0
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def total_length_km(coordinates):
    length = sum(
        haversine_km(coordinates[i], coordinates[i + 1])
        for i in range(len(coordinates) - 1)
    )
    return round(length, 3)


# ── Đọc GeoJSON ───────────────────────────────────────────────────
def load_geojson(file_path):
    print(f"  📂 Đọc file: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_coords(geometry):
    """Trả về danh sách tọa độ phẳng từ LineString hoặc MultiLineString."""
    if geometry["type"] == "LineString":
        return geometry["coordinates"]
    elif geometry["type"] == "MultiLineString":
        # Nối tất cả các đoạn thành một danh sách liên tục
        merged = []
        for seg in geometry["coordinates"]:
            merged.extend(seg)
        return merged
    else:
        raise ValueError(f"Loại geometry không hỗ trợ: {geometry['type']}")


# ── Tạo HTML ──────────────────────────────────────────────────────
def generate_html(routes: list[dict]) -> str:
    """
    routes: danh sách dict, mỗi phần tử gồm:
        - geojson: dict GeoJSON gốc
        - color:   mã màu hex
        - file:    tên file (để fallback tên)
    """

    # --- Tổng hợp thông tin tất cả tuyến ---
    route_metas = []
    all_lats, all_lons = [], []

    for r in routes:
        feat  = r["geojson"]["features"][0]
        props = feat["properties"]
        geom  = feat["geometry"]

        coords     = extract_coords(geom)
        road_name  = props.get("road_name") or props.get("name") or os.path.splitext(r["file"])[0]
        road_ref   = props.get("road_ref", "")
        length_km  = props.get("length_km", total_length_km(coords))
        total_pts  = len(coords)

        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        all_lats.extend(lats)
        all_lons.extend(lons)

        route_metas.append({
            "road_name": road_name,
            "road_ref":  road_ref,
            "length_km": length_km,
            "total_pts": total_pts,
            "coords":    coords,
            "color":     r["color"],
            "geojson":   r["geojson"],
        })

    # Tính trung tâm bản đồ
    center_lat = sum(all_lats) / len(all_lats)
    center_lon = sum(all_lons) / len(all_lons)

    # Tổng chiều dài
    total_all_km = round(sum(m["length_km"] for m in route_metas), 3)

    # --- Sidebar: danh sách tuyến ---
    sidebar_route_items = ""
    for i, m in enumerate(route_metas):
        sidebar_route_items += f"""
        <div class="route-item" id="route-item-{i}" onclick="focusRoute({i})">
          <div class="route-dot" style="background:{m['color']};box-shadow:0 0 8px {m['color']}80"></div>
          <div class="route-info">
            <div class="route-name">{m['road_name']}</div>
            <div class="route-meta">{m['length_km']} km &nbsp;·&nbsp; {m['total_pts']:,} điểm GPS</div>
          </div>
          <div class="route-badge" style="color:{m['color']};border-color:{m['color']}40;background:{m['color']}15">{i+1}</div>
        </div>"""

    # --- Nhúng dữ liệu JS ---
    js_routes_data = json.dumps(
        [
            {
                "road_name": m["road_name"],
                "length_km": m["length_km"],
                "total_pts": m["total_pts"],
                "color":     m["color"],
                "coords":    m["coords"],
            }
            for m in route_metas
        ],
        ensure_ascii=False,
        separators=(",", ":"),
    )

    # --- Template HTML ---
    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bản đồ tuyến đường — Lào Cai</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --bg: #0d1117; --panel: #161b22; --border: #30363d;
      --accent: #f0a500; --text: #e6edf3; --muted: #7d8590;
    }}
    html, body {{ height: 100%; font-family: 'Be Vietnam Pro', sans-serif; background: var(--bg); color: var(--text); overflow: hidden; }}
    #app {{ display: flex; height: 100vh; width: 100vw; }}

    /* ── Sidebar ── */
    #sidebar {{
      width: 310px; min-width: 310px;
      background: var(--panel); border-right: 1px solid var(--border);
      display: flex; flex-direction: column; z-index: 1000; overflow: hidden;
    }}
    #sidebar-header {{
      padding: 24px 22px 18px;
      border-bottom: 1px solid var(--border);
      background: linear-gradient(135deg, #1a1f2e 0%, var(--panel) 100%);
    }}
    .tag-road {{
      display: inline-block; font-family: 'Space Mono', monospace;
      font-size: 10px; font-weight: 700; letter-spacing: 0.12em;
      text-transform: uppercase; color: var(--accent);
      background: rgba(240,165,0,0.12); border: 1px solid rgba(240,165,0,0.3);
      border-radius: 3px; padding: 3px 8px; margin-bottom: 10px;
    }}
    #sidebar-header h1 {{ font-size: 20px; font-weight: 700; line-height: 1.25; margin-bottom: 4px; }}
    #sidebar-header .subtitle {{ font-size: 12px; color: var(--muted); font-weight: 300; }}

    /* ── Tổng quan ── */
    #summary {{
      padding: 16px 22px; border-bottom: 1px solid var(--border);
      display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
    }}
    .stat-card {{
      background: rgba(255,255,255,0.03); border: 1px solid var(--border);
      border-radius: 8px; padding: 12px 14px; transition: border-color .2s;
    }}
    .stat-card:hover {{ border-color: var(--accent); }}
    .stat-label {{ font-size: 10px; text-transform: uppercase; letter-spacing: .1em; color: var(--muted); font-family: 'Space Mono',monospace; margin-bottom: 5px; }}
    .stat-value {{ font-size: 20px; font-weight: 700; color: var(--accent); font-family: 'Space Mono',monospace; line-height: 1; }}
    .stat-unit  {{ font-size: 11px; color: var(--muted); margin-top: 3px; }}

    /* ── Danh sách tuyến ── */
    #routes-section {{ padding: 14px 22px; border-bottom: 1px solid var(--border); overflow-y: auto; flex: 1; }}
    .section-title {{ font-size: 10px; text-transform: uppercase; letter-spacing: .12em; color: var(--muted); font-family: 'Space Mono',monospace; margin-bottom: 12px; }}
    .route-item {{
      display: flex; align-items: center; gap: 12px;
      padding: 10px 12px; border-radius: 8px; cursor: pointer;
      border: 1px solid transparent; transition: all .2s; margin-bottom: 8px;
    }}
    .route-item:hover {{ background: rgba(255,255,255,0.04); border-color: var(--border); }}
    .route-item.active {{ background: rgba(255,255,255,0.06); border-color: var(--border); }}
    .route-dot {{ width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }}
    .route-info {{ flex: 1; min-width: 0; }}
    .route-name {{ font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .route-meta {{ font-size: 11px; color: var(--muted); margin-top: 2px; font-family: 'Space Mono',monospace; }}
    .route-badge {{
      font-family: 'Space Mono',monospace; font-size: 11px; font-weight: 700;
      padding: 2px 8px; border-radius: 4px; border: 1px solid; flex-shrink: 0;
    }}

    /* ── Controls ── */
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

    /* ── Basemap ── */
    #basemap-section {{ padding: 14px 22px; }}
    .basemap-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 8px; }}
    .bm-btn {{
      padding: 7px 4px; background: rgba(255,255,255,.03); border: 1px solid var(--border);
      border-radius: 6px; color: var(--muted); font-size: 11px;
      font-family: 'Be Vietnam Pro',sans-serif; cursor: pointer; text-align: center; transition: all .2s;
    }}
    .bm-btn:hover {{ border-color: var(--accent); color: var(--text); }}
    .bm-btn.active {{ border-color: var(--accent); color: var(--accent); background: rgba(240,165,0,.08); }}

    /* ── Map ── */
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

    /* ── Hover info ── */
    #hover-info {{
      position: absolute; bottom: 28px; right: 16px;
      background: var(--panel); border: 1px solid var(--border); border-radius: 8px;
      padding: 9px 13px; font-size: 12px; color: var(--muted); z-index: 500;
      pointer-events: none; opacity: 0; transition: opacity .2s; font-family: 'Space Mono',monospace;
    }}
    #hover-info.visible {{ opacity: 1; }}
    #hover-info span {{ color: var(--accent); }}

    /* ── Loader ── */
    #loader {{
      position: absolute; inset: 0; background: var(--bg);
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      z-index: 9999; transition: opacity .5s;
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
  <div class="loader-text">Đang tải bản đồ...</div>
</div>

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
      {sidebar_route_items}
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
        &nbsp;|&nbsp; 📏 <span id="hover-dist" style="color:var(--accent);font-weight:700">—</span> km từ đầu tuyến
      </span>
    </div>
  </div>
</div>

<script>
// ── Dữ liệu tuyến ────────────────────────────────────────────────
const ROUTES = {js_routes_data};

// ── Bản đồ ───────────────────────────────────────────────────────
const TILES = {{
  osm:       L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{ maxZoom:19, attribution:'© OpenStreetMap' }}),
  topo:      L.tileLayer('https://{{s}}.tile.opentopomap.org/{{z}}/{{x}}/{{y}}.png',  {{ maxZoom:17, attribution:'© OpenTopoMap' }}),
  satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{ attribution:'© Esri' }})
}};

const map = L.map('map', {{
  center: [{center_lat:.6f}, {center_lon:.6f}],
  zoom: 10,
  layers: [TILES.osm]
}});

// ── Haversine JS ─────────────────────────────────────────────────
function haversineKm(a, b) {{
  const R = 6371, toRad = x => x * Math.PI / 180;
  const dLat = toRad(b[0]-a[0]), dLon = toRad(b[1]-a[1]);
  const s = Math.sin(dLat/2), c = Math.sin(dLon/2);
  return R*2*Math.atan2(Math.sqrt(s*s+Math.cos(toRad(a[0]))*Math.cos(toRad(b[0]))*c*c),
                        Math.sqrt(1-(s*s+Math.cos(toRad(a[0]))*Math.cos(toRad(b[0]))*c*c)));
}}

// ── Tìm điểm chiếu gần nhất trên một tuyến ──────────────────────
function nearestOnLine(latlng, latLngs, cumulDist) {{
  const px = latlng.lat, py = latlng.lng;
  let bestD = Infinity, bestI = 0, bestT = 0;
  for (let i = 0; i < latLngs.length-1; i++) {{
    const ax=latLngs[i][0], ay=latLngs[i][1], bx=latLngs[i+1][0], by=latLngs[i+1][1];
    const dx=bx-ax, dy=by-ay, lenSq=dx*dx+dy*dy;
    let t = lenSq>0 ? ((px-ax)*dx+(py-ay)*dy)/lenSq : 0;
    t = Math.max(0,Math.min(1,t));
    const cx=ax+t*dx, cy=ay+t*dy, d=(px-cx)*(px-cx)+(py-cy)*(py-cy);
    if (d<bestD) {{ bestD=d; bestI=i; bestT=t; }}
  }}
  const seg = haversineKm(latLngs[bestI], latLngs[bestI+1]);
  const dist = cumulDist[bestI] + bestT*seg;
  const pLat = latLngs[bestI][0]+bestT*(latLngs[bestI+1][0]-latLngs[bestI][0]);
  const pLng = latLngs[bestI][1]+bestT*(latLngs[bestI+1][1]-latLngs[bestI][1]);
  return {{ dist, pLat, pLng, bestD }};
}}

// ── Xây dựng từng tuyến ──────────────────────────────────────────
const routeLayers = [];
let glowOn = true, markersOn = true;

const mkIcon = (color) => L.divIcon({{
  html: `<div style="width:14px;height:14px;border-radius:50%;background:${{color}};border:2px solid white;box-shadow:0 0 8px ${{color}}"></div>`,
  iconSize:[14,14], iconAnchor:[7,7], className:''
}});

const snapIcon = L.divIcon({{
  html: `<div style="width:12px;height:12px;border-radius:50%;background:#fff;border:2.5px solid #f0a500;box-shadow:0 0 6px rgba(240,165,0,.8)"></div>`,
  iconSize:[12,12], iconAnchor:[6,6], className:''
}});
const snapMarker = L.marker([0,0], {{ icon: snapIcon, interactive: false }});
let snapActive = false;

const allBounds = [];

ROUTES.forEach((r, idx) => {{
  const latLngs = r.coords.map(c => [c[1], c[0]]);
  const color   = r.color;

  // Tính lũy tích khoảng cách
  const cumulDist = new Float64Array(latLngs.length);
  for (let i=1; i<latLngs.length; i++)
    cumulDist[i] = cumulDist[i-1] + haversineKm(latLngs[i-1], latLngs[i]);
  const totalKm = cumulDist[cumulDist.length-1];

  const glowLine  = L.polyline(latLngs, {{ color: color+'30', weight:14, lineCap:'round', lineJoin:'round' }}).addTo(map);
  const routeLine = L.polyline(latLngs, {{ color, weight:3.5, opacity:.95, lineCap:'round', lineJoin:'round' }}).addTo(map);

  const startM = L.marker(latLngs[0], {{icon: mkIcon('#4ade80')}}).bindTooltip(`Đầu tuyến: ${{r.road_name}}`).addTo(map);
  const endM   = L.marker(latLngs[latLngs.length-1], {{icon: mkIcon('#f87171')}}).bindTooltip(`Cuối tuyến: ${{r.road_name}}`).addTo(map);
  const markerGroup = L.layerGroup([startM, endM]).addTo(map);

  allBounds.push(routeLine.getBounds());

  // Popup khi click vào đường
  routeLine.on('click', function(e) {{
    L.DomEvent.stopPropagation(e);
    const {{ dist, pLat, pLng }} = nearestOnLine(e.latlng, latLngs, cumulDist);
    const pct       = (dist/totalKm*100).toFixed(1);
    const remaining = (totalKm-dist).toFixed(3);
    L.popup({{ maxWidth: 300 }})
      .setLatLng([pLat, pLng])
      .setContent(`<div class="popup-inner">
        <h3 style="color:${{color}}">📏 ${{r.road_name}}</h3>
        <table>
          <tr><td>Từ đầu tuyến</td><td style="color:${{color}}">${{dist.toFixed(3)}} km</td></tr>
          <tr><td>Còn lại đến cuối</td><td>${{remaining}} km</td></tr>
          <tr><td>Tỷ lệ</td><td>${{pct}}% toàn tuyến</td></tr>
          <tr><td>Tổng chiều dài</td><td>${{r.length_km}} km</td></tr>
        </table>
      </div>`)
      .openOn(map);
  }});

  routeLayers.push({{ glowLine, routeLine, markerGroup, latLngs, cumulDist, totalKm, color, name: r.road_name }});
}});

// Fit tất cả tuyến
function fitAll() {{
  if (allBounds.length === 0) return;
  let merged = allBounds[0];
  for (let i=1; i<allBounds.length; i++) merged = merged.extend(allBounds[i]);
  map.fitBounds(merged, {{ padding:[40,40], animate:true, duration:.8 }});
}}
fitAll();

// Focus vào một tuyến từ sidebar
function focusRoute(idx) {{
  const rl = routeLayers[idx];
  map.fitBounds(rl.routeLine.getBounds(), {{ padding:[50,50], animate:true, duration:.8 }});
  document.querySelectorAll('.route-item').forEach((el,i) => el.classList.toggle('active', i===idx));
}}

// ── Hover: snap marker + hover info ─────────────────────────────
const hoverInfo      = document.getElementById('hover-info');
const hoverCoord     = document.getElementById('hover-coord');
const hoverDist      = document.getElementById('hover-dist');
const hoverDistWrap  = document.getElementById('hover-dist-wrap');

map.on('mousemove', function(e) {{
  hoverInfo.classList.add('visible');
  hoverCoord.textContent = e.latlng.lat.toFixed(5)+'° N,  '+e.latlng.lng.toFixed(5)+'° E';

  // Tìm tuyến gần nhất với con trỏ
  let best = null, bestVal = Infinity;
  for (const rl of routeLayers) {{
    const res = nearestOnLine(e.latlng, rl.latLngs, rl.cumulDist);
    if (res.bestD < bestVal) {{ bestVal = res.bestD; best = {{...res, rl}}; }}
  }}

  const near = best && Math.sqrt(best.bestD) < 0.015;
  if (near) {{
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

// Click ngoài tuyến: hiển thị popup với tuyến gần nhất
map.on('click', function(e) {{
  let best = null, bestVal = Infinity;
  for (const rl of routeLayers) {{
    const res = nearestOnLine(e.latlng, rl.latLngs, rl.cumulDist);
    if (res.bestD < bestVal) {{ bestVal = res.bestD; best = {{...res, rl}}; }}
  }}
  if (!best || Math.sqrt(best.bestD) > 0.03) return;
  const rl = best.rl;
  const pct = (best.dist/rl.totalKm*100).toFixed(1);
  L.popup({{ maxWidth:300 }})
    .setLatLng([best.pLat, best.pLng])
    .setContent(`<div class="popup-inner">
      <h3 style="color:${{rl.color}}">📏 ${{rl.name}}</h3>
      <table>
        <tr><td>Từ đầu tuyến</td><td style="color:${{rl.color}}">${{best.dist.toFixed(3)}} km</td></tr>
        <tr><td>Còn lại đến cuối</td><td>${{(rl.totalKm-best.dist).toFixed(3)}} km</td></tr>
        <tr><td>Tỷ lệ</td><td>${{pct}}% toàn tuyến</td></tr>
      </table>
    </div>`)
    .openOn(map);
}});

// ── Điều khiển hiển thị ─────────────────────────────────────────
function toggleGlow(btn) {{
  glowOn = !glowOn;
  btn.classList.toggle('active', glowOn);
  routeLayers.forEach(rl => glowOn ? map.addLayer(rl.glowLine) : map.removeLayer(rl.glowLine));
}}
function toggleMarkers(btn) {{
  markersOn = !markersOn;
  btn.classList.toggle('active', markersOn);
  routeLayers.forEach(rl => markersOn ? map.addLayer(rl.markerGroup) : map.removeLayer(rl.markerGroup));
}}

let currentTile = TILES.osm;
function setBasemap(name, btn) {{
  map.removeLayer(currentTile);
  currentTile = TILES[name];
  map.addLayer(currentTile);
  currentTile.bringToBack();
  document.querySelectorAll('.bm-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}}

window.addEventListener('load', () => {{
  setTimeout(() => document.getElementById('loader').classList.add('hidden'), 600);
}});
</script>
</body>
</html>"""
    return html


# ── Main ──────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Tạo bản đồ HTML từ nhiều file GeoJSON tuyến đường"
    )
    parser.add_argument(
        "--input", "-i", nargs="+", metavar="FILE",
        help="Các file GeoJSON đầu vào. Mặc định: tất cả .geojson trong thư mục hiện tại"
    )
    parser.add_argument(
        "--output", "-o", default=DEFAULT_OUTPUT,
        help=f"File HTML đầu ra (mặc định: {DEFAULT_OUTPUT})"
    )
    args = parser.parse_args()

    # Tìm file đầu vào
    if args.input:
        input_files = args.input
    else:
        input_files = sorted(glob.glob("*.geojson"))
        if not input_files:
            print("❌ Không tìm thấy file .geojson nào trong thư mục hiện tại.")
            print("   Hãy dùng: python generate_map_multi.py --input file1.geojson file2.geojson")
            return

    if len(input_files) < 1:
        print("❌ Cần ít nhất 1 file GeoJSON.")
        return

    print(f"📍 Tìm thấy {len(input_files)} file GeoJSON:")

    routes = []
    for idx, fpath in enumerate(input_files):
        if not os.path.exists(fpath):
            print(f"  ⚠️  Không tìm thấy file: {fpath} — bỏ qua")
            continue
        color = ROUTE_COLORS[idx % len(ROUTE_COLORS)]
        geojson = load_geojson(fpath)
        routes.append({
            "geojson": geojson,
            "color":   color,
            "file":    os.path.basename(fpath),
        })
        feat  = geojson["features"][0]
        props = feat["properties"]
        name  = props.get("road_name") or props.get("name") or os.path.splitext(os.path.basename(fpath))[0]
        lkm   = props.get("length_km", "—")
        print(f"  [{idx+1}] {name}  ({lkm} km)  ● màu {color}")

    if not routes:
        print("❌ Không có file nào hợp lệ.")
        return

    print(f"\n🗺️  Đang tạo bản đồ HTML ({len(routes)} tuyến)...")
    html_content = generate_html(routes)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Hoàn thành! File đã lưu: {args.output}")
    print(f"   Kích thước: {len(html_content)/1024:.1f} KB")
    print(f"   👉 Mở file '{args.output}' bằng trình duyệt để xem bản đồ.")


if __name__ == "__main__":
    main()
