#!/usr/bin/env python3

import subprocess
import tempfile

import geojson


class GeoJsonSVGOverlay:
    def __init__(self, geojson_file, map_template, north, east, south, west):
        self.map = map_template
        self.geo_coord_x = west, east
        self.geo_coord_y = north, south

        # collection of coords of all paths
        self.global_coords = []

        with open(geojson_file) as f:
            self.geojson = geojson.load(f)

        self.template_width, self.template_height = self.get_image_dimensions(self.map)

    @staticmethod
    def map_range(value, inMin, inMax, outMin, outMax):
        """Maps a value from the range (inMin, inMax) to another range (outMin, outMax)."""
        return outMin + (((value - inMin) / (inMax - inMin)) * (outMax - outMin))

    @staticmethod
    def get_image_dimensions(image):
        """Returns the image dimensions."""
        x, y = subprocess.check_output(["identify", "-format", "%w %h", image]).split(
            b" "
        )
        return int(x), int(y)

    def convert(self, image, *, offset=0, output="output.png"):
        """Converts the given svg image with global svg coordinates cropped with given offset."""
        crop_right = (
            self.template_width
            - round(max(self.global_coords, key=lambda x: x[0])[0])
            - offset
        )
        crop_bottom = (
            self.template_height
            - round(max(self.global_coords, key=lambda x: x[1])[1])
            - offset
        )

        crop_left = round(min(self.global_coords, key=lambda x: x[0])[0]) - offset
        crop_top = round(min(self.global_coords, key=lambda x: x[1])[1]) - offset

        subprocess.check_call(
            [
                "convert",
                image,
                "-crop",
                f"+{crop_left}+{crop_top}",
                "-crop",
                f"-{crop_right}-{crop_bottom}",
                output,
            ]
        )

    def get_feature_svg_coords(self, geojson_feature):
        """Returns geo coordinates for given feature with given geo coordinates."""
        # expect only a single entry in coordinates
        [gj_coords] = geojson_feature["geometry"]["coordinates"]
        for x, y in gj_coords:
            svg_x = self.map_range(x, *self.geo_coord_x, 0, self.template_width)
            svg_y = self.map_range(y, *self.geo_coord_y, 0, self.template_height)
            yield svg_x, svg_y

    def get_paths_for_features(self):
        for geojson_feature in self.geojson["features"]:
            coords = list(self.get_feature_svg_coords(geojson_feature))
            self.global_coords.extend(coords)

            svg_coords = [f"{x},{y}" for x, y in coords]
            # add first coordinate as final one to close the path
            svg_coords.append(svg_coords[0])

            yield f'<path class="geojson-area" style="fill: red; fill-opacity: 0.6;" d="M {" L ".join(svg_coords)} Z" />'

    def overlay_map(self, **kwargs):
        with tempfile.NamedTemporaryFile() as temp:
            with open(temp.name, "w") as fw:
                with open(self.map, "r") as fr:
                    fw.write(fr.read().replace("</svg>", ""))

                for path in self.get_paths_for_features():
                    fw.write(path)

                fw.write("</svg>")

                self.convert(temp.name, **kwargs)


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
