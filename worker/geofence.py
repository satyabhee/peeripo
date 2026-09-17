import math

EARTH_RADIUS_M = 6_371_000


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points in meters."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def match_place(lat: float, lon: float, places: list) -> "str | None":
    """places: iterable of objects with .id, .lat, .lon, .radius_m. Returns matching place id or None."""
    for place in places:
        if haversine_m(lat, lon, place.lat, place.lon) <= place.radius_m:
            return place.id
    return None
