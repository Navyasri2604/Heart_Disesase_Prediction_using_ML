# Dataset

The training script downloads the Cleveland subset of the UCI Heart Disease dataset from:
https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data

The original target values 1-4 are mapped to the positive class; target 0 is the negative class. Rows with missing values are removed. The source contains 303 records and is intended for research and educational use, not clinical deployment. Categorical values remain in the source encoding: chest pain (`cp`) 1-4, ST slope 1-3, major vessels (`ca`) 0-3, and thalassemia (`thal`) 3, 6, or 7.