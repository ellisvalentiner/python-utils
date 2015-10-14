import json

class Point:
    def __init__(self, **geometry):
        self.longitude = geometry['lon'] or geometry['coordinates'][0]
        self.latitude = geometry['lat'] or geometry['coordinates'][1]
        self.geodict = {'type': 'Point', 'coordinates': [self.longitude, self.latitude]}

    @classmethod
    def from_lat_lon(cls, lat, lon):
        return cls(lon=lon, lat=lat)

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
