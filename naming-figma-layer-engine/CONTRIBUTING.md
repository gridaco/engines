- `data/`: This folder contains all the data-related files. It is further divided into three sub-folders:

  - `raw/`: Stores raw, unprocessed data files.
  - `processed/`: Stores processed data that is ready for training and evaluation.
  - `models/`: Stores trained models and model checkpoints.

- `src/`: Contains the source code for the project, including datasets, models, utilities, and scripts for training and evaluation.

  - `datasets/`: Contains the custom dataset classes and data processing functions.
  - `models/`: Contains the neural network model definitions.
  - `utils/`: Contains utility functions and any other helper code.
  - `config.py`: Contains project configurations, such as hyperparameters and other settings.
  - `train.py`: Script for training the model.
  - `evaluate.py`: Script for evaluating the model on a validation or test set.
  - `notebooks/`: Contains Jupyter notebooks for exploratory data analysis, visualization, or any other interactive tasks.

- `tests/`: Contains unit tests for different components of the project, such as dataset processing, model implementation, and utility functions.
