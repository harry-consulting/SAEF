import os
import glob
import json
from pathlib import Path
from django.core.management import call_command

CURRENT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


def load_test_json(name):
    with open(os.path.join(CURRENT_DIR.parent, name, 'tests', f'testdata_{name}.json')) as json_data_file:
        return json.load(json_data_file)


def load_test_database(data):
    call_command('loaddata', os.path.join(CURRENT_DIR.parent.parent, 'database', 'data', 'test', f'{data}.json'),
                 verbosity=0)


def load_test_db(app, test):
    path = os.path.join(CURRENT_DIR.parent.parent, 'database', 'data', 'test', app, test, '*.json')
    files = glob.glob(path)
    call_command('loaddata', *files, verbosity=0)


# Loads all data that is required to load a dataset
def load_test_dataset():
    load_test_database('saef.connectiontype')
    load_test_database('saef.connection')
    load_test_database('saef.postgresconnection')
    load_test_database('saef.applicationtoken')
    load_test_database('saef.application')
    load_test_database('saef.job')
    load_test_database('saef.dataset')
