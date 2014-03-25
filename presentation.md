#[Python + Geodata = BFFs](http://pdxmele.com/python-geodata-bffs/index.html)

###Mele Sax-Barnett

-------------------


##Introduction

Why do I think Python and geographic data will be best friends forever?

I &lt;3 maps, but making them can be a pain. The worst part is getting the data to cooperate.

It is usually not in the format you need, has several obvious errors, is split up into 50 different files, is in a completely different projection than what you need, and has no metadata, so you have no idea what you're even looking at.

You could point and click all day in GIS software, or you could use Python.

## Conversion tools

###Convert and filter your data with [Fiona](https://pypi.python.org/pypi/Fiona).

Example: Converting [Natural Earth](http://www.naturalearthdata.com/) Shapefile data to GeoJSON

1. Download [some data](http://www.naturalearthdata.com/downloads/110m-cultural-vectors/)
2. Code sample: **LINK**
	
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
		            if f["properties"]["sovereignt"] != "Antarctica":
		                out.write(f)
                
	You can also [filter by bounding box](http://toblerity.org/fiona/manual.html#filtering)

3. Enjoy!

<img src="img/fiona1.png" height=300px>

###Combine Fiona with [Pyproj](https://pypi.python.org/pypi/pyproj) to change the projection

1. Code sample: **LINK**
		
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

 
2. Enjoy!

<img src="img/proj.png" height=300px>


###Another Fiona example: Assembling a bunch of GPX tracks into a single GeoJSON file

1. export all the GPX data from your favorite tracker
2. Code sample: **LINK**

		import fiona
		import os
		
		
		ROOT_DIR = 'moves_export'
		EXAMPLE_FILE = 'moves_export/storylines_20131201_to_20131207.gpx'
		
		with fiona.open(EXAMPLE_FILE, 'r', layer='tracks') as example:
		    in_schema = example.schema
		    in_crs = example.crs
		
		with fiona.collection(
		        "tracks_output.geojson", "w",
		        crs=in_crs,
		        driver="GeoJSON",
		        schema=in_schema.copy()
		        ) as out:
		    for root, dirs, files in os.walk(ROOT_DIR):
		        for file in files:
		            file_str = ROOT_DIR + "/" + file
		            if file_str[-4:len(file_str)] == ".gpx":
		                with fiona.open(
		                        file_str, 
		                        'r', 
		                        layer='tracks'
		                        ) as inp:
		                    for feature in inp:
		                        print(feature)
		                        out.write(feature)


3. Enjoy!

<img src="img/fiona2.png" height=300px>

##GeoJSON diversion

Before we go any further, let's talk about [GeoJSON](http://geojson.org):

* It's JSON for geodata
* Easy to use for web mapping
* Easy to parse with Python

All you need to do is treat it like a dictionary.

###Example: Turning [OpenStreetMap](http://osm.org) data into map-ready GeoJSON

1. Download some data

	<img src="img/osm_start.png" height=300px>

2. Convert to GeoJSON with [your tool of choice](https://github.com/pdxmele/gwyw-osm/blob/master/converters.md), or you can parse the xml directly

3. Code sample: **LINK**

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


    
4. Enjoy!
    
<img src="img/osm_done.png" height=300px>

You can do this with csv/xml data too--just put it in a dictionary and  assemble valid GeoJSON with only the features and attributes that you want. If you have a lot of data, switch to reading and writing line-by-line.

Because it's just a dictionary, you can also create tests for the data:

* Check for required keys
* Check the type of each key's value
* Check the structure
* Check for valid geometry

This is important if your system expects a very particular format, while your data comes from a variety of sources. 

At Urban Airship, we use data from OpenStreetMap, Natural Earth, TIGER, proprietary datasets like Nielsen and Maponics, and custom data from our customers. All of them need to be in just the right format to work with our user interface and backend systems.

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
* See if one contains the other, if they intersect, and more


###Example: Include only the GPX tracks from earlier that are in Portland

1. Get Portland as GeoJSON from your source of choice
2. Code sample: **LINK**

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
    
	In this case, I did a convex hull around Portland before using ```within``` so that the tracks that intersected Maywood Park (the hole in the middle) would also be included. The ```convex_hull``` created the smallest polygon containing all of the points within Portland.

3. Enjoy!

<img src="img/shapelyresult.png" height=300px>

The pink tracks are those that remained after the code was run, which left out my trip to Disneyland.
 
Another option for geoprocessing without GIS software is [PostGIS](http://postgis.net/). Python can talk to it with [Psycopg](https://pypi.python.org/pypi/psycopg2/) or your other Python PostgreSQL tool of choice.


##Finally, GIS software &lt;3s python</div>

###[ArcGIS](http://resources.arcgis.com/en/communities/python/)

<img src="img/arcgis.png" height=300px>

* [ArcPy](http://resources.arcgis.com/en/help/main/10.1/index.html#//000v00000001000000#GUID-4EC90E5F-F497-4FC0-99FB-7703ED4C8F77) package and Python console
* Create tools and [add-ins](http://resources.arcgis.com/en/help/main/10.1/index.html#//014p00000025000000") from Python scripts

###[QGIS](http://www.qgis.org/en/docs/pyqgis_developer_cookbook/intro.html)

<img src="img/qgis.png" height=300px>

* PyQGIS and Python console 
* qgis module for using QGIS functionality and UI in your app
* Development: QGIS is an open source project written in Python and C++
* [Plugins](https://plugins.qgis.org/): more than 250 useful plugins have already been written and it's easy to add your own

<img src="img/qgisplugins2.png" height=300px>

##Thank you!

Questions? [@pdxmele](https://twitter.com/pdxmele) or [file an issue here](https://github.com/pdxmele/python-geodata-bffs).

[More resources here](https://github.com/pdxmele/python-geodata-bffs/blob/master/resources.md)
