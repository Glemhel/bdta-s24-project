# US Road Accidents Analysis
BDTA S24 project. Author: Mikhail Rudakov.

The project is done for NHTSA agency, USA, which is responsible for ensuring and law-enforcing road safety. This project covers:
- ✍Formulating clear business assessment & goals
- 🔍 Conduct Exploratory Data Analysis to identify accidents reasons and common patterns
- ⚙Develop ML pipeline for accidnet severity prediction
- 🔁Automate the proof-of-concept ML pipeline, from data loading to metrics output to dashboard, all in one ./main.sh!

You can access project dashboard in Apache Superset to get started!

# Technical details
A fully-automated ML pipeline is implemented with the use of Hive, Hadoop, PySpark. All stages are independent and reproducible.
To run the results, execute `./main.sh` within the hadoop cluster available. Output results are located in HDFS `project` folder, and in local `output`.

Structure of the project:
- `data/` contains the dataset files in both plain csv and sparse json format.
- `models/` contains the trained Spark ML models from the training pipeline.
- `output/` represents the output directory for storing the results of the project. It contains `csv` files, text files, images related to the project.
- `scripts/` stores main pipeline stages in `.sh` files. Additional subfolder are created where needed.
- `sql/` is a folder for SQL and HQL queries.
- `requirements.txt` lists the Python packages needed for running your Python scripts. 

`main.sh` is the main script that will run all scripts of the pipeline stages which will execute the full pipeline and store the results in `output/` folder. During checking your project repo, the grader will run only the main script and check the results in `output/` folder.
