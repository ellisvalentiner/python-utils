import json

class Point:
    def __init__(self, **geometry):
        self.longitude = geometry['coordinates'][0]
        self.latitude = geometry['coordinates'][1]

    @property
    def json(self):
        return json.dumps({
            'type': 'Point',
            'coordinates': list(self.coordinates)
        })

def bounding_box(geom):
    vertices = [point for shape in geom['coordinates'] for point in shape]
    lons, lats = zip(*vertices)
    return {'lat_min': min(lats),
            'lat_max': max(lats),
            'lon_min': min(lons),
            'lon_max': max(lons)}
