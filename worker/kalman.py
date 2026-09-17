import numpy as np
from filterpy.kalman import KalmanFilter


def make_position_filter(initial_lat: float, initial_lon: float) -> KalmanFilter:
    """Constant-velocity Kalman filter over [lat, lon, d_lat, d_lon].

    Smooths noisy/sparse Life360 pings into a cleaner position + velocity estimate,
    used to decide "how long were they actually at place X" instead of trusting
    raw GPS jitter between individual pings.
    """
    kf = KalmanFilter(dim_x=4, dim_z=2)
    kf.x = np.array([initial_lat, initial_lon, 0.0, 0.0])
    kf.F = np.array(
        [
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
    )
    kf.H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]])
    kf.P *= 1000.0
    kf.R = np.eye(2) * 1e-5  # GPS measurement noise
    kf.Q = np.eye(4) * 1e-6  # process noise
    return kf


def smooth_pings(pings: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """pings: list of (lat, lon) in chronological order. Returns smoothed (lat, lon)."""
    if not pings:
        return []
    kf = make_position_filter(*pings[0])
    smoothed = [tuple(kf.x[:2])]
    for lat, lon in pings[1:]:
        kf.predict()
        kf.update(np.array([lat, lon]))
        smoothed.append((float(kf.x[0]), float(kf.x[1])))
    return smoothed
