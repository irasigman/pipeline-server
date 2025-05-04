from celery import Celery
import logfire
from celery.signals import worker_init

# log = logfire.configure()

@worker_init.connect()
def init_worker(*args, **kwargs):
    logfire.configure(service_name="worker")
    logfire.instrument_celery()


app = Celery('hello', broker='redis://raspberrypi.local:6379/0', backend='redis://raspberrypi.local:6379/0', include=['demos.jobs'])

@app.task
def hello():
    return 'hello world'
