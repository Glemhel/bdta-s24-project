#!/bin/bash

# clear logs and data
rm -r output/run.log
rm -r output/model*_predictions.csv
rm -r output/evaluation.csv
rm -r models/model1
rm -r models/model2
rm -r models/model3
rm -r models/model4
rm -r data/*.json

# run ML modeling, saving logs to output/run.log
spark-submit --master yarn scripts/stage3_src/stage3.py
