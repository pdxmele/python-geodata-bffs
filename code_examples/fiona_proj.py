import fiona
from fiona.crs import from_epsg
from pyproj import Proj, transform


with fiona.open('ne_110m_admin_0_countries.shp') as inp:
    output_schema = inp.schema.copy()
    output_schema['geometry'] = 'MultiPolygon'
    p_in = Proj(inp.crs)

    with fiona.open('../project_output/project_output.shp', 'w',
                    crs=from_epsg(2163), 
                    driver='ESRI Shapefile', 
                    schema=output_schema
                    ) as out:
        p_out = Proj(out.crs)
        
        for f in inp:
            if f['properties']['sovereignt'] != 'Antarctica':
                try:
                    g = f['geometry']
                    if g['type'] == 'Polygon':
                        parts = [g['coordinates']]
                    elif g['type'] == 'MultiPolygon':
                        parts = g['coordinates']
                    new_coords = []
                    for part in parts:
                        inner_coords = []
                        for ring in part:
                            x2, y2 = transform(p_in, p_out, *zip(*ring))
                            inner_coords.append(zip(x2, y2))
                        new_coords.append(inner_coords)
                    f['geometry']['type'] = 'MultiPolygon'
                    f['geometry']['coordinates'] = new_coords
                    out.write(f)
                
                except Exception, e:
                    print 'Error transforming feature ' + f['id']
