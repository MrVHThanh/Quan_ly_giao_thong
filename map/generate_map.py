"""
generate_map.py
---------------
Đọc file GeoJSON tuyến đường và tạo ra file HTML bản đồ OpenStreetMap.
Dữ liệu tọa độ được nhúng thẳng vào HTML — chỉ cần mở bằng trình duyệt.

Cách dùng:
    python generate_map.py
    python generate_map.py --input roads_laocai_merged.geojson --output dt158_map.html
"""

import json
import argparse
from math import radians, sin, cos, sqrt, atan2


# ── Cài đặt mặc định ──────────────────────────────────────────────
DEFAULT_INPUT  = "QL4E_merged.geojson"
DEFAULT_OUTPUT = "QL4E_map.html"


# ── Hàm tính chiều dài ────────────────────────────────────────────
def haversine_km(coord1, coord2):
    R = 6371.0
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def total_length_km(coordinates):
    length = sum(haversine_km(coordinates[i], coordinates[i+1])
                 for i in range(len(coordinates) - 1))
    return round(length, 3)


# ── Đọc GeoJSON ───────────────────────────────────────────────────
def load_geojson(file_path):
    print(f"📂 Đọc file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# ── Tạo HTML ──────────────────────────────────────────────────────
def generate_html(geojson_data):
    features = geojson_data['features']

    # Lấy feature đầu tiên (hoặc gộp nhiều feature nếu có)
    feat  = features[0]
    props = feat['properties']
    geom  = feat['geometry']

    road_name  = props.get('road_name', 'Tuyến đường')
    road_ref   = props.get('road_ref', '')
    coords     = geom['coordinates'] if geom['type'] == 'LineString' else geom['coordinates'][0]
    length_km  = props.get('length_km', total_length_km(coords))
    total_pts  = len(coords)

    # Tính center và bbox
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)

    # Nhúng toàn bộ GeoJSON vào JS
    road_json = json.dumps(geojson_data, ensure_ascii=False, separators=(',', ':'))

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{road_name} — Lào Cai</title>
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

    /* Sidebar */
    #sidebar {{
      width: 300px; min-width: 300px;
      background: var(--panel); border-right: 1px solid var(--border);
      display: flex; flex-direction: column; z-index: 1000; overflow: hidden;
    }}
    #sidebar-header {{
      padding: 28px 24px 20px; border-bottom: 1px solid var(--border);
      background: linear-gradient(135deg, #1a1f2e 0%, var(--panel) 100%);
    }}
    .tag-road {{
      display: inline-block; font-family: 'Space Mono', monospace;
      font-size: 10px; font-weight: 700; letter-spacing: 0.12em;
      text-transform: uppercase; color: var(--accent);
      background: rgba(240,165,0,0.12); border: 1px solid rgba(240,165,0,0.3);
      border-radius: 3px; padding: 3px 8px; margin-bottom: 12px;
    }}
    #sidebar-header h1 {{ font-size: 22px; font-weight: 700; line-height: 1.2; margin-bottom: 4px; }}
    #sidebar-header .subtitle {{ font-size: 12px; color: var(--muted); font-weight: 300; }}

    /* Stats */
    #stats {{
      padding: 20px 24px; display: grid; grid-template-columns: 1fr 1fr;
      gap: 12px; border-bottom: 1px solid var(--border);
    }}
    .stat-card {{
      background: rgba(255,255,255,0.03); border: 1px solid var(--border);
      border-radius: 8px; padding: 14px 16px; transition: border-color 0.2s;
    }}
    .stat-card:hover {{ border-color: var(--accent); }}
    .stat-label {{ font-size: 10px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); font-family: 'Space Mono', monospace; margin-bottom: 6px; }}
    .stat-value {{ font-size: 22px; font-weight: 700; color: var(--accent); font-family: 'Space Mono', monospace; line-height: 1; }}
    .stat-unit {{ font-size: 11px; color: var(--muted); margin-top: 3px; }}

    /* Chart */
    #profile-section {{ padding: 20px 24px; border-bottom: 1px solid var(--border); flex: 1; }}
    .section-title {{ font-size: 10px; text-transform: uppercase; letter-spacing: 0.12em; color: var(--muted); font-family: 'Space Mono', monospace; margin-bottom: 14px; }}
    #mini-chart {{ width: 100%; height: 70px; }}

    /* Controls */
    #controls {{ padding: 16px 24px; display: flex; flex-direction: column; gap: 10px; border-bottom: 1px solid var(--border); }}
    .ctrl-row {{ display: flex; align-items: center; justify-content: space-between; }}
    .ctrl-label {{ font-size: 12px; color: var(--muted); }}
    .toggle-btn {{
      cursor: pointer; width: 36px; height: 20px; background: var(--border);
      border-radius: 10px; position: relative; transition: background 0.25s; border: none; outline: none;
    }}
    .toggle-btn.active {{ background: var(--accent); }}
    .toggle-btn::after {{
      content: ''; position: absolute; top: 3px; left: 3px;
      width: 14px; height: 14px; background: white; border-radius: 50%; transition: transform 0.25s;
    }}
    .toggle-btn.active::after {{ transform: translateX(16px); }}

    /* Basemap */
    #basemap-section {{ padding: 16px 24px; }}
    .basemap-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 10px; }}
    .bm-btn {{
      padding: 8px 6px; background: rgba(255,255,255,0.03); border: 1px solid var(--border);
      border-radius: 6px; color: var(--muted); font-size: 11px; font-family: 'Be Vietnam Pro', sans-serif;
      cursor: pointer; text-align: center; transition: all 0.2s;
    }}
    .bm-btn:hover {{ border-color: var(--accent); color: var(--text); }}
    .bm-btn.active {{ border-color: var(--accent); color: var(--accent); background: rgba(240,165,0,0.08); }}

    /* Map */
    #map {{ flex: 1; position: relative; }}
    .leaflet-tile-pane {{ filter: brightness(0.85) saturate(0.9); }}
    .leaflet-control-zoom a {{ background: var(--panel) !important; color: var(--text) !important; border-color: var(--border) !important; }}
    .leaflet-control-attribution {{ background: rgba(13,17,23,0.8) !important; color: var(--muted) !important; font-size: 10px !important; }}
    .leaflet-popup-content-wrapper {{ background: var(--panel); border: 1px solid var(--border); border-radius: 10px; color: var(--text); box-shadow: 0 8px 32px rgba(0,0,0,0.5); }}
    .leaflet-popup-tip {{ background: var(--panel); }}
    .popup-inner h3 {{ font-size: 14px; font-weight: 700; color: var(--accent); margin-bottom: 10px; font-family: 'Space Mono', monospace; }}
    .popup-inner table {{ width: 100%; font-size: 12px; border-collapse: collapse; }}
    .popup-inner td {{ padding: 4px 0; color: var(--muted); }}
    .popup-inner td:last-child {{ color: var(--text); text-align: right; font-weight: 600; }}

    /* Hover info */
    #hover-info {{
      position: absolute; bottom: 30px; right: 20px;
      background: var(--panel); border: 1px solid var(--border); border-radius: 8px;
      padding: 10px 14px; font-size: 12px; color: var(--muted); z-index: 500;
      pointer-events: none; opacity: 0; transition: opacity 0.2s; font-family: 'Space Mono', monospace;
    }}
    #hover-info.visible {{ opacity: 1; }}
    #hover-info span {{ color: var(--accent); }}

    /* Loader */
    #loader {{
      position: absolute; inset: 0; background: var(--bg);
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      z-index: 9999; transition: opacity 0.5s;
    }}
    #loader.hidden {{ opacity: 0; pointer-events: none; }}
    .loader-ring {{
      width: 48px; height: 48px; border: 3px solid var(--border);
      border-top-color: var(--accent); border-radius: 50%;
      animation: spin 0.8s linear infinite; margin-bottom: 16px;
    }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    .loader-text {{ font-family: 'Space Mono', monospace; font-size: 12px; color: var(--muted); }}
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
      <div class="tag-road">ĐT.158 · Lào Cai</div>
      <h1>{road_name}</h1>
      <div class="subtitle">Tuyến đường tỉnh — tỉnh Lào Cai</div>
    </div>

    <div id="stats">
      <div class="stat-card">
        <div class="stat-label">Chiều dài</div>
        <div class="stat-value">{length_km}</div>
        <div class="stat-unit">km toàn tuyến</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Điểm đo</div>
        <div class="stat-value">{total_pts}</div>
        <div class="stat-unit">tọa độ GPS</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Điểm đầu</div>
        <div class="stat-value" style="font-size:13px">{coords[0][1]:.4f}</div>
        <div class="stat-unit">{coords[0][0]:.4f} E</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Điểm cuối</div>
        <div class="stat-value" style="font-size:13px">{coords[-1][1]:.4f}</div>
        <div class="stat-unit">{coords[-1][0]:.4f} E</div>
      </div>
    </div>

    <div id="profile-section">
      <div class="section-title">Phân bố tọa độ theo vĩ độ</div>
      <canvas id="mini-chart"></canvas>
    </div>

    <div id="controls">
      <div class="section-title" style="margin-bottom:8px">Hiển thị</div>
      <div class="ctrl-row">
        <span class="ctrl-label">Hiệu ứng phát sáng</span>
        <button class="toggle-btn active" id="toggleGlow" onclick="toggleGlow(this)"></button>
      </div>
      <div class="ctrl-row">
        <span class="ctrl-label">Điểm đầu / cuối</span>
        <button class="toggle-btn active" id="toggleMarkers" onclick="toggleMarkers(this)"></button>
      </div>
      <div class="ctrl-row">
        <span class="ctrl-label">Fit toàn tuyến</span>
        <button onclick="fitRoute()" style="background:rgba(240,165,0,0.1);border:1px solid rgba(240,165,0,0.4);color:var(--accent);padding:4px 14px;border-radius:5px;cursor:pointer;font-size:12px;font-family:'Be Vietnam Pro',sans-serif;">Zoom về</button>
      </div>
    </div>

    <div id="basemap-section">
      <div class="section-title">Nền bản đồ</div>
      <div class="basemap-grid">
        <button class="bm-btn active" onclick="setBasemap('osm', this)">OSM</button>
        <button class="bm-btn" onclick="setBasemap('topo', this)">Topo</button>
        <button class="bm-btn" onclick="setBasemap('satellite', this)">Vệ tinh</button>
      </div>
    </div>
  </aside>

  <div id="map">
    <div id="hover-info">
      📍 <span id="hover-coord">—</span>
      <span id="hover-dist-wrap" style="display:none"> &nbsp;|&nbsp; 📏 <span id="hover-dist" style="color:var(--accent);font-weight:700;">—</span> km từ đầu tuyến</span>
    </div>
  </div>
</div>

<script>
const ROAD_DATA = {road_json};

const TILES = {{
  osm:       L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{ maxZoom:19, attribution:'© OpenStreetMap' }}),
  topo:      L.tileLayer('https://{{s}}.tile.opentopomap.org/{{z}}/{{x}}/{{y}}.png',  {{ maxZoom:17, attribution:'© OpenTopoMap' }}),
  satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{ attribution:'© Esri' }})
}};

const map = L.map('map', {{ center: [{center_lat:.6f}, {center_lon:.6f}], zoom: 11, layers: [TILES.osm] }});

const feat    = ROAD_DATA.features[0];
const coords  = feat.geometry.type === 'LineString' ? feat.geometry.coordinates : feat.geometry.coordinates[0];
const latLngs = coords.map(c => [c[1], c[0]]);

// ── Tính mảng khoảng cách lũy tích từ đầu tuyến ─────────────────
// cumulDist[i] = tổng km từ coords[0] đến coords[i]
function haversineKm(a, b) {{
  const R = 6371;
  const toRad = x => x * Math.PI / 180;
  const dLat = toRad(b[0] - a[0]);
  const dLon = toRad(b[1] - a[1]);
  const sinDLat = Math.sin(dLat/2), sinDLon = Math.sin(dLon/2);
  const h = sinDLat*sinDLat + Math.cos(toRad(a[0]))*Math.cos(toRad(b[0]))*sinDLon*sinDLon;
  return R * 2 * Math.atan2(Math.sqrt(h), Math.sqrt(1-h));
}}

const cumulDist = new Float64Array(latLngs.length);
for (let i = 1; i < latLngs.length; i++) {{
  cumulDist[i] = cumulDist[i-1] + haversineKm(latLngs[i-1], latLngs[i]);
}}
const totalKm = cumulDist[cumulDist.length - 1];

// ── Tìm điểm gần nhất trên tuyến + khoảng cách từ đầu ───────────
function nearestOnRoute(latlng) {{
  const px = latlng.lat, py = latlng.lng;
  let bestDist = Infinity, bestIdx = 0, bestFrac = 0;

  for (let i = 0; i < latLngs.length - 1; i++) {{
    const ax = latLngs[i][0],   ay = latLngs[i][1];
    const bx = latLngs[i+1][0], by = latLngs[i+1][1];
    const dx = bx - ax, dy = by - ay;
    const lenSq = dx*dx + dy*dy;
    let t = lenSq > 0 ? ((px-ax)*dx + (py-ay)*dy) / lenSq : 0;
    t = Math.max(0, Math.min(1, t));
    const cx = ax + t*dx, cy = ay + t*dy;
    const d = (px-cx)*(px-cx) + (py-cy)*(py-cy);
    if (d < bestDist) {{
      bestDist = d;
      bestIdx  = i;
      bestFrac = t;
    }}
  }}

  // Nội suy khoảng cách lũy tích tại điểm chiếu
  const segLen = haversineKm(latLngs[bestIdx], latLngs[bestIdx+1]);
  const distFromStart = cumulDist[bestIdx] + bestFrac * segLen;
  const projLat = latLngs[bestIdx][0] + bestFrac*(latLngs[bestIdx+1][0]-latLngs[bestIdx][0]);
  const projLng = latLngs[bestIdx][1] + bestFrac*(latLngs[bestIdx+1][1]-latLngs[bestIdx][1]);

  return {{ distFromStart, projLat, projLng }};
}}

// ── Vẽ tuyến ────────────────────────────────────────────────────
const glowLine  = L.polyline(latLngs, {{ color: 'rgba(240,165,0,0.18)', weight: 14, lineCap: 'round', lineJoin: 'round' }}).addTo(map);
const routeLine = L.polyline(latLngs, {{ color: '#f0a500', weight: 3.5, opacity: 0.95, lineCap: 'round', lineJoin: 'round' }}).addTo(map);

// ── Marker điểm chiếu (snap marker) ─────────────────────────────
const snapIcon = L.divIcon({{
  html: `<div style="width:12px;height:12px;border-radius:50%;background:#fff;border:2.5px solid #f0a500;box-shadow:0 0 6px rgba(240,165,0,0.8)"></div>`,
  iconSize:[12,12], iconAnchor:[6,6], className:''
}});
const snapMarker = L.marker([0,0], {{ icon: snapIcon, interactive: false }});

// ── Click: hiển thị popup khoảng cách tại điểm chiếu ────────────
map.on('click', function(e) {{
  const {{ distFromStart, projLat, projLng }} = nearestOnRoute(e.latlng);
  const pct = (distFromStart / totalKm * 100).toFixed(1);
  const remaining = (totalKm - distFromStart).toFixed(3);

  L.popup({{ maxWidth: 300, className: 'dist-popup' }})
    .setLatLng([projLat, projLng])
    .setContent(`
      <div class="popup-inner">
        <h3>📏 Khoảng cách trên tuyến</h3>
        <table>
          <tr><td>Từ đầu tuyến</td><td style="color:#f0a500">${{distFromStart.toFixed(3)}} km</td></tr>
          <tr><td>Còn lại đến cuối</td><td>${{remaining}} km</td></tr>
          <tr><td>Tỷ lệ</td><td>${{pct}}% toàn tuyến</td></tr>
          <tr><td>Tọa độ chiếu</td><td>${{projLat.toFixed(5)}}°N</td></tr>
        </table>
      </div>`)
    .openOn(map);
}});

// ── Hover: snap marker + cập nhật thanh thông tin ────────────────
const hoverInfo     = document.getElementById('hover-info');
const hoverCoord    = document.getElementById('hover-coord');
const hoverDist     = document.getElementById('hover-dist');
const hoverDistWrap = document.getElementById('hover-dist-wrap');

let snapActive = false;
map.on('mousemove', function(e) {{
  hoverInfo.classList.add('visible');
  hoverCoord.textContent = e.latlng.lat.toFixed(5) + '° N,  ' + e.latlng.lng.toFixed(5) + '° E';

  const {{ distFromStart, projLat, projLng }} = nearestOnRoute(e.latlng);

  // Chỉ hiện snap + khoảng cách khi chuột đủ gần tuyến (< 0.01 độ ~1km)
  const dx = e.latlng.lat - projLat, dy = e.latlng.lng - projLng;
  const nearRoute = Math.sqrt(dx*dx + dy*dy) < 0.015;

  if (nearRoute) {{
    hoverDistWrap.style.display = 'inline';
    hoverDist.textContent = distFromStart.toFixed(3);
    snapMarker.setLatLng([projLat, projLng]);
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

// ── Popup mặc định tuyến đường (click vào đường) ────────────────
routeLine.on('click', function(e) {{
  L.DomEvent.stopPropagation(e);
  const {{ distFromStart, projLat, projLng }} = nearestOnRoute(e.latlng);
  const pct = (distFromStart / totalKm * 100).toFixed(1);
  const remaining = (totalKm - distFromStart).toFixed(3);
  L.popup({{ maxWidth: 300 }})
    .setLatLng([projLat, projLng])
    .setContent(`
      <div class="popup-inner">
        <h3>📏 {road_name}</h3>
        <table>
          <tr><td>Từ đầu tuyến</td><td style="color:#f0a500">${{distFromStart.toFixed(3)}} km</td></tr>
          <tr><td>Còn lại đến cuối</td><td>${{remaining}} km</td></tr>
          <tr><td>Tỷ lệ</td><td>${{pct}}% toàn tuyến</td></tr>
          <tr><td>Tổng chiều dài</td><td>{length_km} km</td></tr>
        </table>
      </div>`)
    .openOn(map);
}});

const mkIcon = (color) => L.divIcon({{
  html: `<div style="width:14px;height:14px;border-radius:50%;background:${{color}};border:2px solid white;box-shadow:0 0 8px ${{color}}"></div>`,
  iconSize:[14,14], iconAnchor:[7,7], className:''
}});

const startMarker = L.marker(latLngs[0], {{icon: mkIcon('#4ade80')}}).bindTooltip('Điểm đầu tuyến').addTo(map);
const endMarker   = L.marker(latLngs[latLngs.length-1], {{icon: mkIcon('#f87171')}}).bindTooltip('Điểm cuối tuyến').addTo(map);
const markerGroup = L.layerGroup([startMarker, endMarker]).addTo(map);

map.fitBounds(routeLine.getBounds(), {{padding:[30,30]}});

let glowOn = true, markersOn = true;

function toggleGlow(btn) {{
  glowOn = !glowOn;
  btn.classList.toggle('active', glowOn);
  glowOn ? map.addLayer(glowLine) : map.removeLayer(glowLine);
}}
function toggleMarkers(btn) {{
  markersOn = !markersOn;
  btn.classList.toggle('active', markersOn);
  markersOn ? map.addLayer(markerGroup) : map.removeLayer(markerGroup);
}}
function fitRoute() {{
  map.fitBounds(routeLine.getBounds(), {{padding:[40,40], animate:true, duration:0.8}});
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

// Mini chart
(function drawChart() {{
  const canvas = document.getElementById('mini-chart');
  const ctx = canvas.getContext('2d');
  const W = canvas.offsetWidth || 252, H = 70;
  canvas.width = W; canvas.height = H;
  const lats = coords.map(c => c[1]);
  const mn = Math.min(...lats), mx = Math.max(...lats);
  const step = Math.max(1, Math.floor(lats.length / W));
  const pts = [];
  for (let i = 0; i < lats.length; i += step) {{
    pts.push([(i / lats.length) * W, H - ((lats[i] - mn) / (mx - mn)) * (H - 10) - 5]);
  }}
  const grad = ctx.createLinearGradient(0, 0, 0, H);
  grad.addColorStop(0, 'rgba(240,165,0,0.25)');
  grad.addColorStop(1, 'rgba(240,165,0,0)');
  ctx.beginPath();
  ctx.moveTo(pts[0][0], H);
  pts.forEach(([x,y]) => ctx.lineTo(x,y));
  ctx.lineTo(pts[pts.length-1][0], H);
  ctx.closePath();
  ctx.fillStyle = grad; ctx.fill();
  ctx.beginPath();
  pts.forEach(([x,y], i) => i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y));
  ctx.strokeStyle = '#f0a500'; ctx.lineWidth = 1.5; ctx.stroke();
  ctx.fillStyle = '#7d8590'; ctx.font = '9px Space Mono, monospace';
  ctx.fillText(mn.toFixed(3) + '°', 4, H - 3);
  ctx.fillText(mx.toFixed(3) + '°', 4, 12);
}})();

window.addEventListener('load', () => {{
  setTimeout(() => document.getElementById('loader').classList.add('hidden'), 600);
}});
</script>
</body>
</html>"""
    return html


# ── Main ──────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Tạo bản đồ HTML từ file GeoJSON tuyến đường')
    parser.add_argument('--input',  '-i', default=DEFAULT_INPUT,  help=f'File GeoJSON đầu vào (mặc định: {DEFAULT_INPUT})')
    parser.add_argument('--output', '-o', default=DEFAULT_OUTPUT, help=f'File HTML đầu ra (mặc định: {DEFAULT_OUTPUT})')
    args = parser.parse_args()

    geojson_data = load_geojson(args.input)

    print("🗺️  Đang tạo bản đồ HTML...")
    html_content = generate_html(geojson_data)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Hoàn thành! File đã lưu: {args.output}")
    print(f"   Kích thước: {len(html_content)/1024:.1f} KB")
    print(f"   👉 Mở file '{args.output}' bằng trình duyệt để xem bản đồ.")


if __name__ == "__main__":
    main()
