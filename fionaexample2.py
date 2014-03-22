import os, fiona


rootdir = 'moves_export'
examplefile = 'moves_export/storylines_20131201_to_20131207.gpx'
in_crs = ''
in_schema = ''

with fiona.open(examplefile, 'r', layer='tracks') as example:
    in_schema = example.schema
    in_crs = example.crs

with fiona.collection(
    "output3.geojson", "w",
    crs=in_crs,
    driver="GeoJSON",
    schema=in_schema.copy()
    ) as out:
        for root, dirs, files in os.walk(rootdir):
            for file in files:
                filestr = str(file)
                if filestr[-4:len(filestr)] == ".gpx":
                    with fiona.open((rootdir + "/" + file), 'r', 
                        layer='tracks') as inp:
                            for feature in inp:
                                out.write(feature)




"""

import os, fiona

rootdir = 'moves_export'
examplefile = 'moves_export/storylines_20131201_to_20131207.gpx'
in_crs = ''
in_schema = ''

with fiona.open(examplefile, 'r', layer='tracks') as example:
    in_schema = example.schema
    in_crs = example.crs

with fiona.collection(
    "output2.geojson", "w",
    crs=in_crs,
    driver="GeoJSON",
    schema=in_schema.copy()
    ) as out:
        for root, dirs, files in os.walk(rootdir):
            for file in files:
                filestr = str(file)
                print filestr
                if filestr[-4:len(filestr)] == ".gpx":
                    print "working..."
                    with fiona.open((rootdir + "/" + file), 'r', 
                        layer='tracks') as inp:
                            for feature in inp:
                                out.write(feature)
"""



