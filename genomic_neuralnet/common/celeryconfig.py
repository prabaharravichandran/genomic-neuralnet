
# Wait up to 15 minutes for each iteration.
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 60*60} # 60*60 Seconds = 1 hour.
# Do not pre-fetch work.
CELERYD_PREFETCH_MULTIPLIER = 1 
# Do not ack messages until work is completed.
CELERY_ACKS_LATE = True
# Stop warning me about PICKLE.
CELERY_ACCEPT_CONTENT = ['pickle']
# Clear out finished results after 30 minutes.
CELERY_TASK_RESULT_EXPIRES = 60*30