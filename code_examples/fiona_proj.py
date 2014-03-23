import fiona
from fiona.crs import from_epsg
from pyproj import Proj, transform


with fiona.open('ne_110m_admin_0_countries.shp', 'r') as inp:
    
    output_schema = inp.schema.copy()
    p_in = Proj(inp.crs)

    with fiona.collection(
            "output_project/output_project.shp", "w",
            crs=from_epsg(2163), 
            driver="ESRI Shapefile", 
            schema=output_schema
            ) as out:

        p_out = Proj(out.crs)
        
        for f in inp:
            if f["properties"]["sovereignt"] != "Antarctica":
                try:
                    if f['geometry']['type'] == "Polygon":
                        new_coords = []
                        for ring in f['geometry']['coordinates']:
                            x2, y2 = transform(p_in, p_out, *zip(*ring))
                            new_coords.append(zip(x2, y2))
                        f['geometry']['coordinates'] = new_coords
                    elif f['geometry']['type'] == "MultiPolygon":
                        new_coords = []
                        inner_coords = []
                        for polygon in f['geometry']['coordinates']:
                            for ring in polygon:
                                x2, y2 = transform(p_in, p_out, *zip(*ring))
                                inner_coords.append(zip(x2, y2))
                        new_coords.append(inner_coords)
                        f['geometry']['coordinates'] = new_coords
                    out.write(f)
                
                except Exception, e:
                    print "Error transforming feature " + f['id']
