"""
General file for modelling part of the project.
Includes various functions for data loading, transformations, processing.
Also includes models definitions and training functions.
Intended to be run as-is, transforming dataset and training everything at once.
"""

from pyspark.sql import SparkSession
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

from data_preparation import load_dataset, preprocess_dataset
from modeling import (
    make_model1,
    make_model2,
    make_model3,
    make_model4,
    train_model_cv,
    evaluate_model,
    print_and_save_model,
)
from utils import run_os_command

from utils import save_dataset

# Add here your team number teamx
TEAM = 2

# location of your Hive database in HDFS
WAREHOUSE = "project/hive/warehouse"

spark = (
    SparkSession.builder.appName(f"{TEAM} - spark ML")
    .master("yarn")
    .config("hive.metastore.uris", "thrift://hadoop-02.uni.innopolis.ru:9883")
    .config("spark.sql.warehouse.dir", WAREHOUSE)
    .config("spark.sql.avro.compression.codec", "snappy")
    .enableHiveSupport()
    .getOrCreate()
)

spark.sql("USE team2_projectdb;")

# load dataset from the hdfs
initial_dataset = load_dataset(spark)
# perform dataset processing: data cleaning, feature selection
# and feature engineering
processed_dataset = preprocess_dataset(initial_dataset)

# train and test split
train = processed_dataset.sampleBy(
    "label", fractions={1: 0.8, 2: 0.8, 3: 0.8, 4: 0.8}, seed=42
)
test = processed_dataset.subtract(train)

# save dataset
save_dataset(train)
save_dataset(test)

# create models
# Model1: PCA + logistic regression
model1, grid1 = make_model1()

# Model2: PCA + decision tree
model2, grid2 = make_model2()

# Model3: PCA + random forest
model3, grid3 = make_model3()

# Model4: PCA + GBT + OvR
model4, grid4 = make_model4()

# Create evaluation metrics
evaluatorWeightedF = MulticlassClassificationEvaluator(
    labelCol="label",
    predictionCol="prediction",
    weightCol="weight",
    metricName="weightedFMeasure",
)
evaluatorAccuracy = MulticlassClassificationEvaluator(
    labelCol="label", predictionCol="prediction", metricName="accuracy"
)
evaluatorF1 = MulticlassClassificationEvaluator(
    labelCol="label", predictionCol="prediction"
)
evaluatorWeightedPrecision = MulticlassClassificationEvaluator(
    labelCol="label",
    predictionCol="prediction",
    weightCol="weight",
    metricName="weightedPrecision",
)
evaluatorWeightedRecall = MulticlassClassificationEvaluator(
    labelCol="label",
    predictionCol="prediction",
    weightCol="weight",
    metricName="weightedRecall",
)
evaluators = [
    evaluatorWeightedF,
    evaluatorAccuracy,
    evaluatorF1,
    evaluatorWeightedPrecision,
    evaluatorWeightedRecall,
]

models_list = [model1, model2, model3, model4]
models_grids = [grid1, grid2, grid3, grid4]
best_models = []

# Train models via CV and select the best ones
for model, grid in zip(models_list, models_grids):
    best_models.append(train_model_cv(train, model, grid))

evaluations = []
# Evaluate models and save to hdfs
for i, model in enumerate(best_models, 1):
    print_and_save_model(model, i)
    evaluations.append(evaluate_model(model, test, evaluators))

# Create results comparison table
comparison_list = []
for model, evaluation_result in zip(models_list, evaluations):
    comparison_list.append([str(model)] + evaluation_result)

df_comparison = spark.createDataFrame(
    comparison_list,
    [
        "model",
        "Weighted F-score",
        "Accuracy",
        "F1",
        "Weighted Precision",
        "Weighted Recall",
    ],
)
df_comparison.show(truncate=False)

# Save it to HDFS
df_comparison.coalesce(1).write.mode("overwrite").format("csv").option(
    "sep", ","
).option("header", "true").save("project/output/evaluation.csv")
run_os_command(
    "hdfs dfs -cat project/output/evaluation.csv/*.csv > output/evaluation.csv"
)
