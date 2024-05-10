"""
Models definition and function for model training and evaluation.
"""

import pprint

from pyspark.ml.feature import PCA
from pyspark.ml.classification import (
    LogisticRegression,
    DecisionTreeClassifier,
    RandomForestClassifier,
    OneVsRest,
)
from pyspark.ml import Pipeline
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator

from data_utils import run_os_command, custom_log # pylint: disable=import-error

def make_model1(total_features=197):
    """
    Creates a machine learning pipeline with PCA and Logistic Regression.

    Parameters:
    - total_features (int): The total number of features in the dataset. Default is 197.

    Returns:
    - Tuple: A tuple containing the model and the parameter grid.
    """
    pca = PCA(k=50, inputCol="features", outputCol="pcaFeatures")
    log_reg = LogisticRegression(featuresCol="pcaFeatures", labelCol="label", maxIter=10)

    model = Pipeline(stages=[pca, log_reg])

    grid = ParamGridBuilder()
    grid = (
        grid.addGrid(pca.k, [total_features])
    #    .addGrid(log_reg.aggregationDepth, [2, 3, 4])
    #    .addGrid(log_reg.regParam, [0, 0.001, 0.1, 1])
       .build()
    )

    return model, grid


def make_model2(total_features=197):
    """
    Creates a machine learning pipeline with PCA and Decision Tree Classifier.

    Parameters:
    - total_features (int): The total number of features in the dataset. Default is 197.

    Returns:
    - Tuple: A tuple containing the model and the parameter grid.
    """
    pca = PCA(k=50, inputCol="features", outputCol="pcaFeatures")
    dtc = DecisionTreeClassifier(featuresCol="pcaFeatures", labelCol="label")

    model = Pipeline(stages=[pca, dtc])

    grid = ParamGridBuilder()
    grid = (
        grid.addGrid(pca.k, [total_features])
    #   .addGrid(dtc.maxDepth, [5, 10])
    #   .addGrid(dtc.impurity, ["gini", "entropy"])
      .build()
    )

    return model, grid


def make_model3(total_features=197):
    """
    Creates a machine learning pipeline with PCA and Random Forest Classifier.

    Parameters:
    - total_features (int): The total number of features in the dataset. Default is 197.

    Returns:
    - Tuple: A tuple containing the model and the parameter grid.
    """
    pca = PCA(k=50, inputCol="features", outputCol="pcaFeatures")
    rfc = RandomForestClassifier(featuresCol="features", labelCol="label")

    model = Pipeline(stages=[pca, rfc])

    grid = ParamGridBuilder()
    grid = (
        grid.addGrid(pca.k, [total_features])
        # .addGrid(rfc.maxDepth, [5, 10])
        # .addGrid(rfc.numTrees, [5, 10])
        # .addGrid(rfc.impurity, ["gini", "entropy"])
        .build()
    )

    return model, grid


def make_model4(total_features=197):
    """
    Creates a machine learning pipeline with PCA and Logistic Regression using OneVsRest.

    Parameters:
    - total_features (int): The total number of features in the dataset. Default is 197.

    Returns:
    - Tuple: A tuple containing the model and the parameter grid.
    """
    pca = PCA(k=50, inputCol="features", outputCol="pcaFeatures")
    log_reg = LogisticRegression(featuresCol="pcaFeatures", labelCol="label", maxIter=10)
    ovr = OneVsRest(classifier=log_reg)

    model = Pipeline(stages=[pca, ovr])

    grid = ParamGridBuilder()
    grid = (
        grid.addGrid(pca.k, [total_features])
    #    .addGrid(log_reg.aggregationDepth, [2, 3, 4])
    #    .addGrid(log_reg.regParam, [0, 0.001, 0.1, 1])
        .build()
    )

    return model, grid


def train_model_cv(train_data, model, grid, evaluator, num_folds=3):
    """
    Trains a model using cross-validation.

    Parameters:
    - train_data (DataFrame): The training data.
    - model (Pipeline): The machine learning model to be trained.
    - grid (ParamGrid): The parameter grid for hyperparameter tuning.
    - evaluator (Evaluator): The evaluator to be used for model evaluation.
    - numFolds (int): The number of folds for cross-validation. Default is 3.

    Returns:
    - Model: The best model found during cross-validation.
    """
    cross_validaton_trainer = CrossValidator(
        estimator=model,
        estimatorParamMaps=grid,
        evaluator=evaluator,
        parallelism=5,
        numFolds=num_folds,
    )

    cv_model = cross_validaton_trainer.fit(train_data)
    best_model = cv_model.bestModel

    return best_model


def print_and_save_model(model, model_id):
    """
    Prints the parameters of a model and saves it to HDFS and disk.

    Parameters:
    - model (Model): The Spark ML model to be printed and saved.
    - model_id (str): The identifier for the model file name.
    """
    custom_log(pprint.pformat(model.stages))

    model.write().overwrite().save(f"project/models/model{model_id}")
    run_os_command(f"hdfs dfs -get project/models/model{model_id} models/model{model_id}")


def evaluate_model(model, model_id, test_data, evaluators):
    """
    Evaluates a model on test data using a list of evaluators.
    Saves model prediction to HDFS and disk.

    Parameters:
    - model (Model): The Spark ML model to be evaluated.
    - test_data (DataFrame): The test data to evaluate the model on.
    - evaluators (List[Evaluator]): A list of evaluators to use for evaluation.

    Returns:
    - List: A list of evaluation results.
    """
    predictions = model.transform(test_data)

    predictions.select("label", "prediction")\
        .coalesce(1)\
        .write\
        .mode("overwrite")\
        .format("csv")\
        .option("sep", ",")\
        .option("header","true")\
        .save(f"project/output/model{model_id}_predictions.csv")

    # Run it from root directory of the repository
    run_os_command(f"hdfs dfs -cat project/output/model{model_id}_predictions.csv/*.csv " +
        f"> output/model{model_id}_predictions.csv")
    results = []
    for evaluator in evaluators:
        results.append(evaluator.evaluate(predictions))

    return results
