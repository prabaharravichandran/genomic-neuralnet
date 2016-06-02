import joblib

TRAIN_SIZE = 0.9
# Limit the number of markers required to participate in analysis.
REQUIRED_MARKERS_PROPORTION = 0.0
# Set the number of cores to use for processing. 
CPU_CORES = joblib.cpu_count()
# The number of folds to use for cross-validation.
NUM_FOLDS = 10

# Neuralnet Settings
MAX_EPOCHS = 1000 # If TRY_CONVERGENCE is False, this is also the minimum # epochs.
CONTINUE_EPOCHS = 25 # Ignored if TRY_CONVERGENCE is False
TRY_CONVERGENCE = True 
USE_ARAC = True # If arac library is installed, we can train networks faster.

# Pick a processing backend for the modeling.
CELERY_BACKEND = 'celery'
JOBLIB_BACKEND = 'joblib'
SINGLE_CORE_BACKEND = 'single-core'

INIT_CELERY = False # Must be True to use celery backend.
