import fiona


with fiona.open('ne_110m_admin_0_countries.shp') as src:
    with fiona.open(
            'output.geojson', 'w',
            crs=src.crs,
            driver='GeoJSON',
            schema=src.schema
            ) as dst:
        for f in src:
            if f['properties']['sovereignt'] != 'Antarctica':
                dst.write(f)
