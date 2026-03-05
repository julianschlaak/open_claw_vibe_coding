from __future__ import annotations

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon
from pathlib import Path


# Simplified Saxony boundary in EPSG:4326
SAXONY_BOUNDS = Polygon(
    [
        (11.50, 50.20),
        (12.50, 50.20),
        (13.50, 50.50),
        (14.50, 51.00),
        (15.04, 51.30),
        (14.80, 51.60),
        (13.80, 51.50),
        (12.80, 51.40),
        (12.00, 51.20),
        (11.80, 50.80),
        (11.50, 50.20),
    ]
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_saxony_boundary_gdf() -> gpd.GeoDataFrame:
    """Load official Saxony boundary from shapefile, fallback to simplified polygon."""
    shp = _repo_root() / "code" / "mhm" / "shapes" / "Saxony" / "Saxony" / "Sachsen.shp"
    if shp.exists():
        g = gpd.read_file(shp)
        if g.crs is None:
            g = g.set_crs("EPSG:4326")
        else:
            g = g.to_crs("EPSG:4326")
        g = g[["geometry"]].copy()
        g["name"] = "Sachsen"
        return g[["name", "geometry"]]
    return gpd.GeoDataFrame([{"name": "Sachsen", "geometry": SAXONY_BOUNDS}], crs="EPSG:4326")


def clip_points_to_saxony(df: pd.DataFrame, lat_col: str = "lat", lon_col: str = "lon") -> pd.Series:
    """Return boolean mask for points inside or on Saxony boundary."""
    sax_geom = get_saxony_boundary_gdf().geometry.union_all()
    return df.apply(lambda r: sax_geom.covers(Point(float(r[lon_col]), float(r[lat_col]))), axis=1)
