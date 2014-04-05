#[Python + Geodata = BFFs](http://pdxmele.com/python-geodata-bffs/index.html) 

by Mele Sax-Barnett

##Introduction

Why do I think Python and geographic data will be best friends forever?

I &lt;3 maps, but making them can be a pain. The worst part is getting the data to cooperate.

It usually:

* Is not in the [format](http://www.gdal.org/ogr/ogr_formats.html) [you need](http://en.wikipedia.org/wiki/GIS_file_formats)
* Has several [obvious errors](http://en.wikipedia.org/wiki/Null_Island)
* Is split up into 50 different files 
* Is in a completely different [projection](http://en.wikipedia.org/wiki/Map_projection)/coordinate system than what you need
* And has no [metadata](https://www.fgdc.gov/metadata), so you have no idea what you're even looking at

You could point and click all day in out-of-the-box GIS software to get it ready to use, or you could add Python to the mix.

## Conversion tools

###Convert and filter your data with [Fiona](https://pypi.python.org/pypi/Fiona).

Example: Converting [Natural Earth](http://www.naturalearthdata.com/) shapefile data to GeoJSON

1. Download some [free, awesome data](http://www.naturalearthdata.com/downloads/110m-cultural-vectors/)
2. [Put together a script like this](https://github.com/pdxmele/python-geodata-bffs/blob/master/code_examples/fiona_example1.py):

	*Note: all of the scripts included below were based off of examples in the documentation for these libraries (where applicable).*
	

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
                
	This script takes a Natural Earth countries shapefile, copies the schema and coordinate system, and then moves all the data over to a new GeoJSON file--unless the name of the country is Antarctica. In this way, you can filter by any property at the same time as you do your data conversion.
	
	You can also [filter by bounding box](http://toblerity.org/fiona/manual.html#filtering).

3. Enjoy!

<img src="img/fiona1.png" height=300px>

###Combine Fiona with [Pyproj](https://pypi.python.org/pypi/pyproj) to change the projection

It can be a good idea to change the projection/coordinate system to one that suits your needs. For example, if you're mapping the poles, you don't want to use Mercator (in the image above). Similarly, if you're measuring large distances or plotting great circle routes, your accuracy depends on using the correct projection. Remember, the world is not the shape of your screen!

1. [Try a script like this](https://github.com/pdxmele/python-geodata-bffs/blob/master/code_examples/fiona_proj.py):
		
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

	This script uses PyProj to transform each of the coordinates to the new coordinate system that is given with from_epsg via its [EPSG](http://epsg.io/) [SRID code](http://en.wikipedia.org/wiki/SRID). This dataset includes both Polygons and MultiPolygons, and I had to handle them differently because of their data structure differences (MultiPolygon coordinates live one level deeper so they can hold a number of Polygons). [Learn more about geometry types in Fiona here](http://toblerity.org/fiona/manual.html#record-geometry).

2. Enjoy your new coordinate system!

<img src="img/proj.png" height=300px>


###Another Fiona example: Assembling a bunch of GPX tracks into a single GeoJSON file

1. Export all the GPX data from your favorite tracker into one folder
2. Identify an example file, and [use a script like this](https://github.com/pdxmele/python-geodata-bffs/blob/master/code_examples/fiona_example2.py):

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
	
	In this case, I used one of the files I wanted to include as an example so I could set up the schema and coordinate system (this will only work if they all have the exact same structure). Next, it walks a directory looking for .gpx files to assemble. Since [GPX files](http://en.wikipedia.org/wiki/GPS_eXchange_Format) have several layers, I had to tell Fiona that I wanted the "tracks" layer.

3. Now you can visualize everywhere that you've been:

<img src="img/fiona2.png" height=300px>

I used exports from [Moves App](http://www.moves-app.com/) via [Moves Export](http://http://www.moves-export.com/), and visualized them with [TileMill](https://www.mapbox.com/tilemill/) on [MapBox](https://www.mapbox.com/) [OpenStreetMap](http://switch2osm.org) tiles.

##A Diversion into GeoJSON

Before we go any further, let's talk about [GeoJSON](http://geojson.org). Why am I so into GeoJSON?

* It's JSON for geodata
* Easy to use for web mapping
* Easy to parse with Python

All you need to do is treat it like a dictionary.

###Example: Turning OpenStreetMap data into map-ready GeoJSON

1. Download some data from [OpenStreetMap](http://osm.org)

	<img src="img/osm_start.png" height=300px>

2. Convert it to GeoJSON with [your tool of choice](https://github.com/pdxmele/gwyw-osm/blob/master/converters.md), or you can [parse the OSM XML directly](http://wiki.openstreetmap.org/wiki/OSM_XML)

3. Clean it up with a [script like this](https://github.com/pdxmele/python-geodata-bffs/blob/master/code_examples/geojson_example.py):

		import json
		
		
		INPUT_PATH = 'osmjson_example.geojson'
		OUTPUT_PATH = 'osmjson_output.geojson'
		
		json_data = open(INPUT_PATH).read()
		data = json.loads(json_data)
		
		feature_collection = {
		    'type': 'FeatureCollection',
		    'features': []
		    }
		
		for feature in data['features']:
		    tags = feature['properties']['tags']
		
		    if ('building' in tags and 'name' in tags):
		        osm_id = str(feature['id'])
		        name = tags.pop('name')
		        geom_type = feature['geometry']['type']
		        coordinates = feature['geometry']['coordinates']
		
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
		
		with open(OUTPUT_PATH, 'w') as out:
		    out.write(json.dumps(feature_collection))

	It starts by loading all the input file data into a dictionary and setting up the feature_collection output dictionary. Then, I grab only the features that have the OpenStreetMap "building" and "name" tags (only named buildings, nothing else). After putting all of the attributes I want to keep into variables and pulling the name out of the tags dictionary, it puts together the new feature structure. Finally, the feature_collection dictionary (valid GeoJSON) gets written out into a new file.
    
4. Check out these buildings in Shinjuku! I'm ready to plan my trip to Japan. Or maybe I should have grabbed all of the ramen shops in Tokyo instead?
    
<img src="img/osm_done.png" height=300px>

You can follow a similar approach when starting with XML and raw CSV data too--just parse, put it in a dictionary, and assemble GeoJSON with only the features and attributes that you want. You can also run mathematical or geographical operations on your features, creating polygons around points or modifying them in other ways. 

If you have a lot of data (like the whole OSM planet), add some newlines around pseudo-dictionary objects and switch to reading and writing line-by-line.

And, because it's just a dictionary, it's easy to create tests for the data:

* Check for required keys

		if "source" not in data["properties"]:
	
* Check the type of each key's value

		if not (isinstance(data[key], basestring) or data[key] is None):
		
* Check against known values

		boundary_check_list = [data["properties"]["boundary_type"], data["properties"]["boundary_type_string"]]
        	if not boundary_check_list in typelist:
            	print (feature_id + " in file " + filename + " has a boundary_type and boundary_type_string, 
            	but they don't match any pairs in the type names file")

* Check the structure

		if isinstance(data[key][k0][k1], dict):
	
* Validate geometry

		if ("type" not in data["geometry"] or not (data["geometry"]["type"] == "Polygon" or data["geometry"]["type"] == "MultiPolygon")):
		

This can be very important if your system expects a very particular format while your data comes from a variety of sources. At Urban Airship, we use data from OpenStreetMap, Natural Earth, TIGER, proprietary datasets like Nielsen and Maponics, as well as custom lat/long data from our customers. All of them need to be in just the right format to work with our user interface and backend systems.

<img src="img/ua_ss.png" height=300px>

##Geoprocessing and spatial analysis with [Shapely](https://pypi.python.org/pypi/Shapely) 

You can find [tons of examples in the manual](http://toblerity.org/shapely/manual.html):

* Validate 
* Simplify
* Buffer
* Convex hull
* Merge
* Union
* Interpolate
* Create polygons from lines
* Get centroid, bounding box, area, or length of a feature
* Get the distance between two objects, check if they are equal or almost equal
* Get the difference or symmetrical difference
* See if one contains the other, if they intersect, and more...


###Example: Keep only the GPX tracks that are in Portland

1. Get Portland/your city as GeoJSON from your source of choice
2. Try [a script like this](https://github.com/pdxmele/python-geodata-bffs/blob/master/code_examples/shapely_example.py):

		import json
		import shapely
		from shapely.geometry import shape
		
		
		PORTLAND_PATH = 'portland.geojson'
		TRACKS_PATH = 'tracks.geojson'
		OUTPUT_PATH = 'tracks_portland.geojson'
		
		feature_collection = {
		    'type': 'FeatureCollection',
		    'features': []
		    }
		
		portland_json = open(PORTLAND_PATH).read()
		portland_geom = shape(json.loads(portland_json)['features'][0]['geometry'])
		
		tracks_json = open(TRACKS_PATH).read()
		for feature in json.loads(tracks_json)['features']:
		    feature_geom = shape(feature['geometry'])
		    if feature_geom.within(portland_geom.convex_hull):
		        feature_collection['features'].append(feature)
		
		with open(OUTPUT_PATH, 'w') as out:
		    out.write(json.dumps(feature_collection))
    
	After some setup, we create a Shapely shape out of each feature's geometry. In this case, I did a convex hull around Portland before using [within](http://toblerity.org/shapely/manual.html#object.within) so that the tracks that intersected Maywood Park (the hole in the middle of Portland) would also be included. The [convex_hull](http://toblerity.org/shapely/manual.html#object.convex_hull) created the smallest polygon that contains all of the points within Portland.

3. Enjoy! The pink tracks are those that remained after the code was run. As you see, it removed my flight to Disneyland and rovings around southern California.

<img src="img/shapelyresult.png" height=300px>
 
Another option for geoprocessing without GIS software is [PostGIS](http://postgis.net/). Python can talk to it with [Psycopg](https://pypi.python.org/pypi/psycopg2/) or your other Python PostgreSQL tool of choice. There are even more options in the [additional resources doc for this presentation](https://github.com/pdxmele/python-geodata-bffs/blob/master/resources.md).


##Finally, GIS software &lt;3s python</div>

###[ArcGIS](http://resources.arcgis.com/en/communities/python/)

<img src="img/arcgis.png" height=300px>

* [ArcPy](http://resources.arcgis.com/en/help/main/10.1/index.html#//000v00000001000000#GUID-4EC90E5F-F497-4FC0-99FB-7703ED4C8F77) package and Python console
* Create tools and [add-ins](http://resources.arcgis.com/en/help/main/10.1/index.html#//014p00000025000000") from Python scripts

###[QGIS](http://www.qgis.org/en/docs/pyqgis_developer_cookbook/intro.html)

<img src="img/qgis.png" height=300px>

* PyQGIS console 
* Module "qgis" for using QGIS functionality and UI in your external app
* Development: QGIS is an open source project written in Python and C++, you can contribute to it
* [Plugins](https://plugins.qgis.org/): more than 250 useful plugins have already been written and it's easy to add your own

<img src="img/qgisplugins2.png" height=300px>

##Thank you!

Questions? Tweet [@pdxmele](https://twitter.com/pdxmele) or [file an issue here](https://github.com/pdxmele/python-geodata-bffs).

[Additional resources here](https://github.com/pdxmele/python-geodata-bffs/blob/master/resources.md)
