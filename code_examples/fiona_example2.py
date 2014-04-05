import fiona
import os


ROOT_DIR = '../moves_export'
EXAMPLE_FILE = '../moves_export/storylines_20131201_to_20131207.gpx'

with fiona.open(EXAMPLE_FILE, layer='tracks') as example:
    in_schema = example.schema
    in_crs = example.crs

with fiona.open('tracks.geojson', 'w',
                crs=in_crs,
                driver='GeoJSON',
                schema=in_schema
                ) as out:
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            file_str = ROOT_DIR + '/' + file
            if file_str[-4:len(file_str)] == '.gpx':
                with fiona.open(file_str,
                                layer='tracks'
                                ) as inp:
                    for feature in inp:
                        out.write(feature)
