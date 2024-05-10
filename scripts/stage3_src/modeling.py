from pyspark.ml.feature import VectorAssembler, RobustScaler, PCA, StandardScaler
from pyspark.ml.classification import LogisticRegression, DecisionTreeClassifier, RandomForestClassifier, GBTClassifier, MultilayerPerceptronClassifier, OneVsRest
from pyspark.ml import Pipeline

from pyspark.ml.tuning import ParamGridBuilder, CrossValidator 
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

import numpy as np
from utils import run_os_command
from pprint import pprint


def make_model1(total_features=199):
    pca = PCA(k=50, inputCol="features", outputCol="pcaFeatures")
    lr = LogisticRegression(featuresCol="pcaFeatures", outputCol="label")

    model = Pipeline(stages=[pca, lr])

    grid = ParamGridBuilder()
    grid = grid.addGrid(pca.k, [50, 100, total_features]) \
                .addGrid(lr.aggregationDepth, [2, 3, 4]) \
                .addGrid(lr.regParam, [0, 0.001, 0.1, 1]) \
                .build()

    return model, grid

def make_model2(total_features=199):
    pca = PCA(k=50, inputCol="features", outputCol="pcaFeatures")
    dtc = DecisionTreeClassifier(featuresCol="pcaFeatures", labelCol="label")

    model = Pipeline(stages=[pca, dtc])

    grid = ParamGridBuilder()
    grid = grid.addGrid(pca.k, [50, 100, total_features]) \
                .addGrid(dtc.maxDepth, [5, 10]) \
                .addGrid(dtc.impurity, ["gini", "entropy"]) \
                .build()
    
    return model, grid

def make_model3(total_features=199):
    pca = PCA(k=50, inputCol="features", outputCol="pcaFeatures")
    rf = RandomForestClassifier(featuresCol="features", labelCol="label")

    model = Pipeline(stages=[pca, rf])

    grid = ParamGridBuilder()
    grid = grid.addGrid(pca.k, [50, 100, total_features]) \
                .addGrid(rf.maxDepth, [5, 10]) \
                .addGrid(rf.numTrees, [5, 10]) \
                .addGrid(rf.impurity, ["gini", "entropy"]) \
                .build()
    
    return model, grid

def make_model4(total_features=199):
    pca = PCA(k=50, inputCol="features", outputCol="pcaFeatures")
    gbt = GBTClassifier(featuresCol="pcaFeatures", labelCol="label")
    ovr = OneVsRest(classifier=gbt)

    model = Pipeline(stages=[pca, ovr])

    grid = ParamGridBuilder()
    grid = grid.addGrid(pca.k, [50, 100, total_features]) \
                .addGrid(gbt.maxDepth, [3, 5]) \
                .build()
    
    return model, grid

def train_model_cv(train_data, model, grid, evaluator, parallelism=5, numFolds=3):
    cv = CrossValidator(estimator = model, 
                        estimatorParamMaps = grid, 
                        evaluator = evaluator,
                        parallelism = parallelism,
                        numFolds=numFolds)

    cvModel = cv.fit(train_data)
    bestModel = cvModel.bestModel
    
    return bestModel

def print_and_save_model(model, model_id):
    pprint(model.extractParamMap())

    model.write().overwrite().save(f"project/models/model{model_id}")
    run_os_command(f"hdfs dfs -get project/models/model1 models/model{model_id}")

def evaluate_model(model, test_data, evaluators):
    predictions = model.transform(test_data)
    results = []
    for evaluator in evaluators:
        results.append(evaluator.evaluate(predictions))

    return results
