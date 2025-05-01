import json

# 输入文件路径（替换为你自己的路径）
input_path = input_path = r"C:\Users\lwj20\Desktop\csv3234\static\data\nsw_boundary.geojson"

output_path = "nsw_cleaned_boundaries.geojson"

# 加载原始文件
with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 提取并清理
cleaned_features = []
for feature in data["features"]:
    geometry = feature.get("geometry", None)
    props = feature.get("properties", {})
    name = (
        props.get("nsw_loca_2") or
        props.get("name") or
        props.get("NAME") or
        props.get("Name") or
        props.get("suburb") or
        "Unnamed"
    )
    if geometry:
        cleaned_features.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": {"name": name}
        })

# 生成新文件
cleaned_geojson = {
    "type": "FeatureCollection",
    "features": cleaned_features
}

# 保存
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(cleaned_geojson, f)

print(f"✔ Cleaned file saved to {output_path}")
