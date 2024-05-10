"""
General file for modelling part of the project.
Includes various functions for data loading, transformations, processing.
Also includes models definitions and training functions.
Intended to be run as-is, transforming dataset and training everything at once.
"""

# from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

from data_preparation import load_dataset, preprocess_dataset # pylint: disable=import-error
from modeling import ( # pylint: disable=import-error
    make_model1,
    make_model2,
    make_model3,
    make_model4,
    train_model_cv,
    evaluate_model,
    print_and_save_model,
)
from data_utils import run_os_command, save_dataset, custom_log # pylint: disable=import-error

# SparkContext.setSystemProperty('spark.executor.memory', '5g')
custom_log("Stage 3. Python script started")

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
    .config("spark.executor.instances", 4)\
    .enableHiveSupport()
    .getOrCreate()
)

spark.sparkContext.addPyFile("scripts/stage3_src/data_utils.py")
spark.sparkContext.addPyFile("scripts/stage3_src/modeling.py")
spark.sparkContext.addPyFile("scripts/stage3_src/data_preparation.py")

custom_log("Stage 3. Initialized spark.")

spark.sql("USE team2_projectdb;")

# load dataset from the hdfs
custom_log("Stage 3. Loading dataset.")
initial_dataset = load_dataset(spark)
# perform dataset processing: data cleaning, feature selection
# and feature engineering
custom_log("Stage 3. Preprocessing dataset.")
processed_dataset = preprocess_dataset(initial_dataset)

# train and test split
train = processed_dataset.sampleBy(
    "label", fractions={1: 0.8, 2: 0.8, 3: 0.8, 4: 0.8}, seed=42
)
test = processed_dataset.subtract(train)

custom_log("Stage 3. Saving train and test to disk.")
# save dataset
save_dataset(train, "train")
save_dataset(test, "test")


# create models
custom_log("Stage 3. Creating models.")
# Model1: PCA + logistic regression
model1, grid1 = make_model1(197)

# Model2: PCA + decision tree
model2, grid2 = make_model2(197)

# Model3: PCA + random forest
model3, grid3 = make_model3(197)

# Model4: PCA + LogReg + OvR
model4, grid4 = make_model4(197)

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
model_descriptions = [
    "PCA+LogReg",
    "PCA+DecisionTrees",
    "PCA+RandomForest",
    "PCA+LogReg+OvR",
]
models_grids = [grid1, grid2, grid3, grid4]
best_models = []

# Train models via CV and select the best ones
for model, desc, grid in zip(models_list, model_descriptions, models_grids):
    custom_log(f"Stage 3. Running model: {desc}.")
    best_models.append(train_model_cv(train, model, grid, evaluatorWeightedF))

custom_log("Stage 3. Running evaluation.")
evaluations = []
# Evaluate models and save to hdfs
for i, model in enumerate(best_models, 1):
    print_and_save_model(model, i)
    evaluations.append(evaluate_model(model, i, test, evaluators))

custom_log("Stage 3. Saving comparison results.")

# Create results comparison table
comparison_list = []
for model, desc, evaluation_result in zip(models_list, model_descriptions, evaluations):
    comparison_list.append([desc] + evaluation_result)

df_comparison = spark.createDataFrame(
    comparison_list,
    [
        "model",
        "Weighted_F_score",
        "Accuracy",
        "F1",
        "Weighted_Precision",
        "Weighted_Recall",
    ],
)
df_comparison.show(truncate=False)

# Save it to HDFS
df_comparison.coalesce(1).write.mode("overwrite").format("csv") \
    .option("sep", ",").option("header", "true") \
    .save("project/output/evaluation")

# create external table for ML results
spark.sql("""CREATE EXTERNAL TABLE IF NOT EXISTS evaluation_results (
    model STRING,
    Weighted_F_score DOUBLE,
    Accuracy DOUBLE,
    F1 DOUBLE,
    Weighted_Precision DOUBLE,
    Weighted_Recall DOUBLE
)
STORED AS TEXTFILE
LOCATION 'project/hive/warehouse/evaluation_results'
""")

# save comparison dataframe to the table
df_comparison.coalesce(1).write.mode("overwrite").saveAsTable("team2_projectdb.evaluation_results")

run_os_command(
    "hdfs dfs -cat project/output/evaluation.csv/*.csv > output/evaluation.csv"
)
