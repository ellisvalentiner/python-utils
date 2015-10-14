import json

class Point:
    def __init__(self, **geometry):
        self.longitude = geometry.get('lon', geometry['coordinates'][0])
        self.latitude = geometry.get('lat', geometry['coordinates'][1])
        self.geodict = {'type': 'Point', 'coordinates': [self.longitude, self.latitude]}

    @property
    def dict(self):
        return self.geodict

    @property
    def json(self):
        return json.dumps(self.geodict)

def bounding_box(geom):
    vertices = [point for shape in geom['coordinates'] for point in shape]
    lons, lats = zip(*vertices)
    return {'lat_min': min(lats),
            'lat_max': max(lats),
            'lon_min': min(lons),
            'lon_max': max(lons)}
