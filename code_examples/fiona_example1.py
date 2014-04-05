import fiona


with fiona.open('ne_110m_admin_0_countries.shp') as inp:
    with fiona.open('output.geojson', 'w',
                    crs=inp.crs,
                    driver='GeoJSON',
                    schema=inp.schema
                    ) as out:
        for f in inp:
            if f['properties']['sovereignt'] != 'Antarctica':
                out.write(f)
