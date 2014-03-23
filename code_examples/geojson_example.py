import json


INPUT_PATH = 'osmjson_example.geojson'
OUTPUT_PATH = 'osmjson_output.geojson'

json_data = open(INPUT_PATH).read()
data = json.loads(json_data)

feature_collection = {
    'type': 'FeatureCollection',
    'features': []
    }

for feature in data["features"]:
    tags = feature["properties"]["tags"]

    if ("building" in tags and "name" in tags):
        osm_id = str(feature["id"])
        name = tags["name"]
        tags.pop("name")
        geom_type = feature["geometry"]["type"]
        coordinates = feature["geometry"]["coordinates"]

        updated_feature = {
            'type': 'Feature',
            'geometry': {
                'type': geom_type,
                'coordinates': coordinates
                },
            'properties': {
                'osm_id': osm_id,
                'name': name,
                'tags': tags
                }
            }

        feature_collection['features'].append(updated_feature)
        print updated_feature

with open(OUTPUT_PATH, 'w') as output:
    output.write(json.dumps(feature_collection))

