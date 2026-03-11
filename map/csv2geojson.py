# Convert CSV coordinates to GeoJSON by replacing LineString coordinates
import pandas as pd, json

csv_path = "polyline.csv"
geojson_path = "QL4E_merged2.geojson"
out_path = "QL4E_updated_from_csv.geojson"

# Read CSV
df = pd.read_csv(csv_path)

# Normalize column names
cols = {c.lower(): c for c in df.columns}
lon_col = cols.get("long") or cols.get("lon") or cols.get("longitude")
lat_col = cols.get("lat") or cols.get("latitude")

coords = df[[lon_col, lat_col]].values.tolist()

# Read GeoJSON
with open(geojson_path, "r", encoding="utf-8") as f:
    geo = json.load(f)

# Replace coordinates
if geo.get("type") == "FeatureCollection":
    for feat in geo["features"]:
        if feat.get("geometry", {}).get("type") == "LineString":
            feat["geometry"]["coordinates"] = coords
elif geo.get("type") == "Feature":
    if geo.get("geometry", {}).get("type") == "LineString":
        geo["geometry"]["coordinates"] = coords

# Save
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(geo, f, ensure_ascii=False)

out_path