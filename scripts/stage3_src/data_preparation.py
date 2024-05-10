"""
Data preparation utils for the modeling stage.
"""

import math
from pyspark import keyword_only
from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    dayofweek,
    dayofmonth,
    hour,
    month,
    year,
    sin,
    cos,
    col,
    unix_timestamp,
    when,
)
from pyspark.ml import Transformer, Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable
from pyspark.ml.param.shared import (
    HasInputCol,
    HasOutputCol,
    Param,
    Params,
    TypeConverters,
)
from pyspark.sql.functions import lit

from data_utils import ecef_udf_currying


class CategoryClipTransformer(
    Transformer, HasInputCol, HasOutputCol, DefaultParamsReadable, DefaultParamsWritable
): # pylint: disable=too-many-ancestors
    """
    A transformer to clip categories based on a threshold.

    Parameters:
        input_col (str): Name of the input column.
        output_col (str): Name of the output column.
        threshold (int): Threshold value for clipping.

    Returns:
        DataFrame: DataFrame with clipped categories.
    """

    input_col = Param(
        Params._dummy(), # pylint: disable=protected-access
        "input_col",
        "Name of the input column.",
        typeConverter=TypeConverters.toString,
    )
    output_col = Param(
        Params._dummy(), # pylint: disable=protected-access
        "output_col",
        "Name of the output column.",
        typeConverter=TypeConverters.toString,
    )
    threshold = Param(
        Params._dummy(), # pylint: disable=protected-access
        "threshold",
        "Threshold value for clipping.",
        typeConverter=TypeConverters.toInt,
    )

    _input_kwargs = {}

    @keyword_only
    def __init__(
        self, input_col: str = "input", output_col: str = "output", threshold: int = 20
    ):
        """
        Initialize the transformer with default parameters.

        Parameters:
            input_col (str): Name of the input column.
            output_col (str): Name of the output column.
            threshold (int): Threshold value for clipping.
        """
        super(CategoryClipTransformer, self).__init__() # pylint: disable=super-with-arguments
        self._setDefault(
            input_col=input_col,
            output_col=output_col,
            threshold=threshold
        )
        kwargs = self._input_kwargs
        self.set_params(**kwargs)

    @keyword_only
    def set_params(self,
        input_col=None,
        output_col=None,
        threshold=None
    ): # pylint: disable=unused-argument
        """
        Set kwargs parameters.
        """
        kwargs = self._input_kwargs
        self._set(**kwargs) # pylint: disable=not-a-mapping

    def get_input_col(self):
        """Get the name of the input column."""
        return self.getOrDefault(self.input_col)

    def get_output_col(self):
        """Get the name of the output column."""
        return self.getOrDefault(self.output_col)

    def get_threshold(self):
        """Get the threshold value for clipping."""
        return self.getOrDefault(self.threshold)

    def _transform(self, dataset: DataFrame):
        """
        Apply the clipping logic to the input DataFrame.

        Parameters:
            df (DataFrame): Input DataFrame.

        Returns:
            DataFrame: DataFrame with clipped categories.
        """
        input_col = self.get_input_col()
        output_col = self.get_output_col()
        threshold = self.get_threshold()

        return dataset.withColumn(
            output_col,
            when(col(input_col) >= threshold, threshold).otherwise(col(input_col)),
        )


def with_weight_column(dataframe):
    """
    Add a weight column to the DataFrame based on class proportions.

    Parameters:
        dataframe (DataFrame): Input DataFrame.

    Returns:
        DataFrame: DataFrame with an added weight column.
    """
    df_copy = dataframe.alias("df_copy")
    class_counts = df_copy.groupBy("label").count()
    total_count = df_copy.count()
    class_proportions = class_counts.withColumn(
        "proportion", col("count") / total_count
    )
    class_proportions_dict = {
        row["label"]: row["proportion"] for row in class_proportions.collect()
    }

    weights = {}
    for label, proportion in class_proportions_dict.items():
        weights[label] = 1 / proportion

    df_copy = df_copy.withColumn("weight", lit(0))

    for label, weight in weights.items():
        df_copy = df_copy.withColumn(
            "weight", when(col("label") == label, weight).otherwise(col("weight"))
        )

    return df_copy


def load_dataset(spark_session):
    """
    Load dataset from HDFS.

    Parameters:
        spark_session (SparkSession): Spark session instance.

    Returns:
        DataFrame: Loaded dataset.
    """
    return spark_session.read.format("avro").table("us_accidents1")


def preprocess_dataset(dataset):
    """
    Preprocess the dataset by applying feature selection, transformations, and encoding.

    Parameters:
        dataset (DataFrame): Input dataset.

    Returns:
        DataFrame: Preprocessed dataset with added weight column.
    """
    # Select needed columns
    data = dataset.select(
        "start_lat",
        "start_lng",
        "start_time",
        "distance_mi",
        "description",
        "street",
        "city",
        "county",
        "state",
        "zipcode",
        "timezone",
        "airport_code",
        "weather_timestamp",
        "temperature_f",
        "humidity_percent",
        "pressure_in",
        "visibility_mi",
        "wind_direction",
        "wind_speed_mph",
        "weather_condition",
        "amenity",
        "bump",
        "crossing",
        "give_way",
        "junction",
        "no_exit",
        "railway",
        "roundabout",
        "station",
        "stop",
        "traffic_calming",
        "traffic_signal",
        "sunrise_sunset",
        "civil_twilight",
        "nautical_twilight",
        "astronomical_twilight",
        "severity",
    )

    # Drop null rows
    data = data.dropna()

    # Rename target
    data = data.withColumnRenamed("severity", "label")

    # Time-related transformations
    data = data.withColumn(
        "month_sin", sin(2 * math.pi * month(col("start_time")) / 12)
    )
    data = data.withColumn(
        "month_cos", cos(2 * math.pi * month(col("start_time")) / 12)
    )
    data = data.withColumn(
        "dayofweek_sin", sin(2 * math.pi * dayofweek(col("start_time")) / 7)
    )
    data = data.withColumn(
        "dayofweek_cos", cos(2 * math.pi * dayofweek(col("start_time")) / 7)
    )
    data = data.withColumn(
        "day_sin", sin(2 * math.pi * dayofmonth(col("start_time")) / 31)
    )
    data = data.withColumn(
        "day_cos", cos(2 * math.pi * dayofmonth(col("start_time")) / 31)
    )
    data = data.withColumn("hour_sin", sin(2 * math.pi * hour(col("start_time")) / 24))
    data = data.withColumn("hour_cos", cos(2 * math.pi * hour(col("start_time")) / 24))
    data = data.withColumn("year", year(col("start_time")))
    data = data.withColumn(
        "weather_time",
        unix_timestamp(col("start_time")) - unix_timestamp(col("weather_timestamp")),
    )

    # Coordinates-related transformations
    data = data.withColumn(
        "ecef_x", ecef_udf_currying("x")(col("start_lat"), col("start_lng"))
    )
    data = data.withColumn(
        "ecef_y", ecef_udf_currying("y")(col("start_lat"), col("start_lng"))
    )
    data = data.withColumn(
        "ecef_z", ecef_udf_currying("z")(col("start_lat"), col("start_lng"))
    )

    # Drop unnecessary columns
    data = data.drop(
        "start_lat",
        "start_lng",
        "start_time",
        "weather_timestamp",
        "description",
        "distance_mi",
    )

    # Define categorical and numerical columns
    categorical_cols = [
        "street",
        "city",
        "county",
        "state",
        "zipcode",
        "timezone",
        "airport_code",
        "wind_direction",
        "weather_condition",
        "sunrise_sunset",
        "civil_twilight",
        "nautical_twilight",
        "astronomical_twilight",
    ]
    numerical_cols = [
        "ecef_x",
        "ecef_y",
        "ecef_z",
        "year",
        "hour_sin",
        "hour_cos",
        "day_sin",
        "day_cos",
        "month_sin",
        "month_cos",
        "dayofweek_sin",
        "dayofweek_cos",
        "temperature_f",
        "humidity_percent",
        "pressure_in",
        "visibility_mi",
        "wind_speed_mph",
        "weather_time",
        "amenity",
        "bump",
        "crossing",
        "give_way",
        "junction",
        "no_exit",
        "railway",
        "roundabout",
        "station",
        "stop",
        "traffic_calming",
        "traffic_signal",
    ]

    # Create String indexer for categorical columns
    indexers = [
        StringIndexer(inputCol=c, outputCol=f"{c}_indexed", handleInvalid="error")
        for c in categorical_cols
    ]

    # Clip categories
    clippers = [
        CategoryClipTransformer( # pylint: disable=no-member
            input_col=indexer.getOutputCol(),
            output_col=f"{indexer.getOutputCol()}_clipped",
            threshold=20,
        )
        for indexer in indexers
    ]

    # Encode the strings using One Hot encoding
    encoders = [
        OneHotEncoder(
            inputCol=clipper.get_output_col(),
            outputCol=f"{clipper.get_output_col()}_encoded",
        )
        for clipper in clippers
    ]

    # Assemble features
    assembler = VectorAssembler(
        inputCols=[encoder.getOutputCol() for encoder in encoders] + numerical_cols,
        outputCol="features",
    )

    # Transform the dataset
    transform_pipeline = Pipeline(stages=indexers + clippers + encoders + [assembler])
    transformed_dataset = transform_pipeline.fit(data).transform(data)

    # Select only needed columns
    transformed_dataset = transformed_dataset.select("features", "label")

    # Add weight column
    output_data = with_weight_column(transformed_dataset)

    return output_data
