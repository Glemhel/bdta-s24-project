"""
Utility functions for geospatial transformations and dataset management.
"""

import os
import math
import datetime

from pyspark.sql import DataFrame
from pyspark.sql.functions import udf
from pyspark.sql.types import DoubleType

# WGS84 ellipsoid parameters
WGS84_A_DIAM = 6378137.0  # Semi-major axis of the WGS84 ellipsoid
WGS84_E_SQUARED = 0.006694379990141316  # Square of eccentricity of the WGS84 ellipsoid


def lat_lon_to_ecef(lat: float, lon: float, axis: str) -> float:
    """
    Convert latitude and longitude coordinates to Earth-Centered Earth-Fixed (ECEF) coordinates.

    Parameters:
        lat (float): Latitude in degrees.
        lon (float): Longitude in degrees.
        axis (str): Axis to return ('x', 'y', or 'z').

    Returns:
        float: The ECEF coordinate for the specified axis.

    Raises:
        ValueError: If an invalid axis is specified.
    """
    # Convert latitude and longitude to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)

    # Calculate trigonometric functions
    lat_sin = math.sin(lat_rad)
    lat_cos = math.cos(lat_rad)
    lon_sin = math.sin(lon_rad)
    lon_cos = math.cos(lon_rad)

    # Calculate the radius of curvature in the prime vertical
    prime_vertical_radius = WGS84_A_DIAM / math.sqrt(1 - WGS84_E_SQUARED * lat_sin**2)

    # Calculate ECEF coordinates
    x_cord = prime_vertical_radius * lat_cos * lon_cos
    y_cord = prime_vertical_radius * lat_cos * lon_sin
    z_cord = prime_vertical_radius * (1 - WGS84_E_SQUARED) * lat_sin

    # Return the requested axis
    if axis == "x":
        return x_cord
    if axis == "y":
        return y_cord
    if axis == "z":
        return z_cord

    raise ValueError("Invalid axis specified. Use 'x', 'y', or 'z'.")


def ecef_udf_currying(cord: str) -> udf:
    """
    Create a curried User Defined Function (UDF) for converting coordinates to ECEF.

    Parameters:
        cord (str): Axis to return ('x', 'y', or 'z').

    Returns:
        udf: A PySpark UDF for converting coordinates to ECEF.
    """
    return udf(lambda lat, lon: lat_lon_to_ecef(lat, lon, cord), DoubleType())


def run_os_command(command: str) -> str:
    """
    Execute an OS command and return the output.

    Parameters:
        command (str): The command to execute.

    Returns:
        str: The output of the command.
    """
    return os.popen(command).read()


def save_dataset(dataset: DataFrame, name: str) -> None:
    """
    Save a dataset to a JSON file and consolidate it to local storage.

    Parameters:
        dataset (DataFrame): The Spark DataFrame to save.
        name (str): The name of the dataset.
    """
    dataset.select("features", "label").coalesce(1).write.mode("overwrite").format(
        "json"
    ).save(f"project/data/{name}")

    # Consolidate the JSON file to local storage
    run_os_command(f"hdfs dfs -cat project/data/{name}/*.json > data/{name}.json")


def custom_log(message):
    """
    Write log message to file.
    """
    current_time = str(datetime.datetime.now()).split('.', maxsplit=1)[0]
    with open("output/run.log", "a", encoding="utf-8") as file:
        file.write(f"{current_time}: {message}")
        file.write("\n")
