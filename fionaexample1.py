#import fiona
#import pprint

"""with fiona.open('ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp') as source:
    source_driver = source.driver
    source_crs = source.crs
    source_schema = source.schema
    rec = next(source)
    pprint.pprint(rec)
"""

#from 

import fiona
with fiona.open('ne_110m_admin_0_countries.shp', 'r') as inp:
    output_schema = inp.schema.copy()
    with fiona.collection(
            "output.geojson", "w",
            crs=inp.crs, 
            driver="GeoJSON", 
            schema=output_schema
            ) as out:
        for f in inp:
            out.write(f)