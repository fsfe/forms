from celery import Celery

app = Celery()
app.config_from_object('background.celeryconfig')
app.autodiscover_tasks(['background.tasks'])
