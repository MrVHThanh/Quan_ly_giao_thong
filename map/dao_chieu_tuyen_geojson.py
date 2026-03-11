import json

# File đầu vào
input_file = "TL158_merged.geojson"

# File sau khi đảo chiều
output_file = "TL158_reversed.geojson"

# Đọc file geojson
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Trường hợp phổ biến: FeatureCollection
if data["type"] == "FeatureCollection":
    for feature in data["features"]:
        geom = feature["geometry"]

        if geom["type"] == "LineString":
            geom["coordinates"] = geom["coordinates"][::-1]

        elif geom["type"] == "MultiLineString":
            geom["coordinates"] = [line[::-1] for line in geom["coordinates"]]

# Trường hợp chỉ là Feature
elif data["type"] == "Feature":
    geom = data["geometry"]

    if geom["type"] == "LineString":
        geom["coordinates"] = geom["coordinates"][::-1]

# Ghi lại file
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Đã đảo chiều tuyến và lưu file:", output_file)