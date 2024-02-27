geojson-svg-overlay
===================

Naive overlay of geojson polygons to a given SVG map.

Usage
-----

.. code-block:: text

   usage: geojson-svg-overlay [-h] [--north NORTH] [--east EAST] [--south SOUTH] [--west WEST]
                           [--map MAP] [--offset OFFSET]
                           geojson output

   Overlays geojson polygons on a given SVG map

   positional arguments:
     geojson          geojson file
     output           output image

   options:
     -h, --help       show this help message and exit
     --north NORTH    northern limit of map
     --east EAST      eastern limit of map
     --south SOUTH    southern limit of map
     --west WEST      western limit of map
     --map MAP        SVG map template (default: map.svg)
     --offset OFFSET  offset from area edge to picture edge (default: 100)


Installation
------------

.. code-block:: bash

   $ # system dependencies
   $ sudo apt install python3-venv

   $ # install geojson-svg-overlay
   $ python3 -m venv venv
   $ source venv/bin/activate
   (venv) $ pip install git+https://github.com/freieslabor/geojson-svg-overlay.git


Usage example
-------------

Assuming `wget` and `jq` are installed, geojson-svg-overlay could be used like this:

.. code-block:: bash

   $ # download geojson example
   $ ID=$(wget -q -O - https://nina.api.proxy.bund.dev/api31/dwd/mapData.json | jq -r ".[0].id")
   $ wget -O dwd.geojson "https://nina.api.proxy.bund.dev/api31/warnings/$ID.geojson"

   $ # download map template example
   $ wget -O map.svg https://upload.wikimedia.org/wikipedia/commons/e/e5/Germany%2C_administrative_divisions_%28%2Bdistricts%29_-_de_-_colored.svg

   $ source venv/bin/activate
   (venv) $ # run geojson-svg-overlay
   (venv) geojson-svg-overlay --north 55.1 --south 47.2 --west 5.5 --east 15.5 dwd.geojson out.png

Honorable Mentions
------------------
simcup (he knows what he's done 🫵)
