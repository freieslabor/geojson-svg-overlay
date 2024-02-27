#!/usr/bin/env python3

import cairosvg
import geojson


class GeoJsonSVGOverlay:
    def __init__(self, geojson_file, map_template, north, east, south, west):
        self.map = map_template
        self.geo_coord_x = west, east
        self.geo_coord_y = north, south
        self.tree = cairosvg.parser.Tree(url=map_template)

        # collection of coords of all paths
        self.global_coords = []

        with open(geojson_file) as f:
            self.geojson = geojson.load(f)

    @staticmethod
    def map_range(value, inMin, inMax, outMin, outMax):
        """Maps a value from the range (inMin, inMax) to another range (outMin, outMax)."""
        return outMin + (((value - inMin) / (inMax - inMin)) * (outMax - outMin))

    @property
    def svg_width(self):
        width = self.tree["width"]
        assert width.endswith("px")
        return float(width[:-2])

    @property
    def svg_height(self):
        height = self.tree["height"]
        assert height.endswith("px")
        return float(height[:-2])


    def convert(self, *, offset=0, output="output.png"):
        """Converts the given svg image with global svg coordinates cropped with given offset."""
        x1 = round(min(self.global_coords, key=lambda x: x[0])[0]) - offset
        x1 = max(x1, 0)

        y1 = round(min(self.global_coords, key=lambda x: x[1])[1]) - offset
        y1 = max(y1, 0)

        x2 = round(max(self.global_coords, key=lambda x: x[0])[0]) + offset
        x2 = min(x2, self.svg_width)

        y2 = round(max(self.global_coords, key=lambda x: x[1])[1]) + offset
        y2 = min(y2, self.svg_height)

        self.tree["viewBox"] = f"{x1} {y1} {x2-x1} {y2-y1}"
        self.tree["width"] = f"{x2-x1}px"
        self.tree["height"] = f"{y2-y1}px"

        with open(output, "wb") as f:
            surface = cairosvg.surface.PNGSurface(self.tree, f, 0, output_width=1920)
            surface.finish()

    def get_feature_svg_coords(self, geojson_feature):
        """Returns geo coordinates for given feature with given geo coordinates."""
        # expect only a single entry in coordinates
        gj_coords = geojson_feature["geometry"]["coordinates"]

        for gj_coord in gj_coords:
            for x, y in gj_coord:
                svg_x = self.map_range(x, *self.geo_coord_x, 0, self.svg_width)
                svg_y = self.map_range(y, *self.geo_coord_y, 0, self.svg_height)
                yield svg_x, svg_y

    def get_paths_for_features(self):
        for geojson_feature in self.geojson["features"]:
            coords = list(self.get_feature_svg_coords(geojson_feature))
            self.global_coords.extend(coords)

            svg_coords = [f"{x},{y}" for x, y in coords]
            # add first coordinate as final one to close the path
            svg_coords.append(svg_coords[0])

            color = geojson_feature["properties"]["fillColor"]

            yield f'<path class="geojson-area" style="fill: {color}; fill-opacity: 0.6;" d="M {" L ".join(svg_coords)} Z" />'

    def overlay_map(self, **kwargs):
        for path in self.get_paths_for_features():
            node = cairosvg.parser.Tree(bytestring=path)
            self.tree.children.append(node)
        self.convert(**kwargs)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Overlays geojson polygons on a given SVG map"
    )
    parser.add_argument("--north", type=float, required=True, help="northern limit of map")
    parser.add_argument("--east", type=float, required=True, help="eastern limit of map")
    parser.add_argument("--south", type=float, required=True, help="southern limit of map")
    parser.add_argument("--west", type=float, required=True, help="western limit of map")
    parser.add_argument(
        "--map", default="map.svg", help="SVG map template (default: %(default)s)"
    )
    parser.add_argument(
        "--offset",
        default=100,
        type=int,
        help="offset from area edge to picture edge (default: %(default)s)",
    )
    parser.add_argument("geojson", help="geojson file")
    parser.add_argument("output", help="output image")

    args = parser.parse_args()

    overlay = GeoJsonSVGOverlay(
        args.geojson, args.map, args.north, args.east, args.south, args.west
    )

    overlay.overlay_map(output=args.output, offset=args.offset)


if __name__ == "__main__":
    main()
