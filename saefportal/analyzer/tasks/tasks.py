from __future__ import absolute_import, unicode_literals

from analyzer.celery_conf import app
from analyzer.tasks.task_analyze_dataset import task_analyze_dataset
from analyzer.tasks.task_compute_application_session_meta_data import task_compute_application_session_meta_data
from analyzer.tasks.task_compute_job_session_meta_data import task_compute_job_session_meta_data


@app.task
def analyze_dataset(dataset_session_pk):
    return task_analyze_dataset(dataset_session_pk)


@app.task
def compute_application_session_meta_data(application_session_start_pk):
    return task_compute_application_session_meta_data(application_session_start_pk)


@app.task
def compute_job_session_meta_data(application_session_start_pk):
    return task_compute_job_session_meta_data(application_session_start_pk)


@app.task(name='celery.ping')
def ping():
    return 'pong'
