import json
import shapely
from shapely.geometry import shape


PORTLAND_PATH = 'portland.geojson'
TRACKS_PATH = 'tracks_output.geojson'
OUTPUT_PATH = 'tracks_portland.geojson'

feature_collection = {
    'type': 'FeatureCollection',
    'features': []
    }

portland_json = open(PORTLAND_PATH).read()
portland_geom = shape(json.loads(portland_json)["features"][0]["geometry"])

tracks_json = open(TRACKS_PATH).read()
for feature in json.loads(tracks_json)["features"]:
    feature_geom = shape(feature["geometry"])
    if feature_geom.within(portland_geom.convex_hull):
        feature_collection['features'].append(feature)

with open(OUTPUT_PATH, 'w') as output:
    output.write(json.dumps(feature_collection))

