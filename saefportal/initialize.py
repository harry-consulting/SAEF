import psycopg2
import pyodbc
import glob
import subprocess
import argparse
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from saefportal.settings import TEST_POSTGRES_DB_NAME, TEST_POSTGRES_USERNAME, TEST_POSTGRES_PASSWORD, TEST_POSTGRES_HOST, TEST_POSTGRES_PORT
from saefportal.settings import TEST_AZURE_DB_NAME, TEST_AZURE_USERNAME, TEST_AZURE_PASSWORD, TEST_AZURE_HOST, TEST_AZURE_PORT
from analyzer.tests.utils import validate_configuration


parser = argparse.ArgumentParser(description='Initialize a clean database')
parser.add_argument('-s', action='store_true', help="Ensures no prompts through the initialize")
parser.add_argument('-r', action='store_true', help="Starts server after initialize without prompt")
parser.add_argument('-t', action='store_true', help="Create test databases")

parser.add_argument('--loaddata', help="Path to data to initialize the database with")
parser.add_argument('--forceclean', action='store_true', help="Forces a clean initialize of the system")
parser.add_argument('-u', help="Username to Postgres")
parser.add_argument('-p', help="Password to Postgres")

parser.add_argument('-su', help="Username to Django")
parser.add_argument('-sp', help="Password to Django")

parser.add_argument('--restart', action='store_true', help="Restarts the Django service")

args = parser.parse_args()

class Initialize():
    def __init__(self):
        self.username = 'postgres'
        self.password = 'test'
        self.default_db = 'saefportal'
        self.cursor = self.connect_to_database()

    def prompt_verify_dropping_database(self):
        print('ARE YOU SURE YOU WANNA INITIALIZE THE SYSTEM?')
        print('THE DATABASE WILL BE DROPPED AND CAN NOT BE UNDONE')
        print('START PROCESS? WRITE YES')
        inp = input()
        if inp.lower() != 'yes':
            exit()
            
    def connect_to_database(self):
        print (f'Initializing system using PostgresDB')
        print (f'-----------------------------------------')
        print (f'CONNECTING TO DATABASE')
        if args.u:
            self.username = args.u
        if args.p:
            self.password = args.p
        connection = psycopg2.connect(host='localhost', dbname="postgres", user=self.username, password=self.password)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return connection.cursor()

    def terminate_connections(self):
        print (f'-----------------------------------------')
        print (f'TERMINATING ALL CURRENT CONNECTIONS')
        self.cursor.execute(f"SELECT pg_terminate_backend (pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{self.default_db}'")
        
    def drop_database(self, database):
        try:
            self.cursor.execute(f"DROP DATABASE {database}")
        except Exception:
            pass # Already deleted

    def create_database_super_user(self):
        try:
            print (f'-----------------------------------------')
            print('CREATING SUPERUSER SAEFUSER')
            self.cursor.execute("create user saefuser with encrypted password 'saefpassword'")
        except Exception as e:
            pass # Already exists
        
        try:
            self.cursor.execute("ALTER role saefuser with superuser createdb")
        except Exception as e:
            pass # Already exists
        
    def create_database(self, database):
        try:
            print (f'-----------------------------------------')
            print(f'CREATING {database} DATABASE')
            self.cursor.execute(f"CREATE DATABASE {database}")
        except Exception:
            pass # Already exists
        
    def setup_test_database(self):
        print (f'-----------------------------------------')
        print(f'CREATING TEST DATABASES')
        
        try:
            # Postgres test database
            print(f'CREATING POSTGRES TEST DATABASE')
            
            configration = {'TEST_POSTGRES_DB_NAME': TEST_POSTGRES_DB_NAME,
                            'TEST_POSTGRES_USERNAME': TEST_POSTGRES_USERNAME,
                            'TEST_POSTGRES_PASSWORD': TEST_POSTGRES_PASSWORD,
                            'TEST_POSTGRES_HOST': TEST_POSTGRES_HOST,
                            'TEST_POSTGRES_PORT': TEST_POSTGRES_PORT}

            validate_configuration(configration)

            connection = psycopg2.connect(host=TEST_POSTGRES_HOST, dbname=TEST_POSTGRES_DB_NAME, user=TEST_POSTGRES_USERNAME, password=TEST_POSTGRES_PASSWORD, port=TEST_POSTGRES_PORT)
            connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = connection.cursor()
            cursor.execute(f"ALTER DATABASE {TEST_POSTGRES_DB_NAME} SET timezone TO 'Europe/Copenhagen'")
            cursor.execute("""
                            CREATE TABLE saef_job 
                            (id INTEGER PRIMARY KEY, 
                            name VARCHAR(255), 
                            description VARCHAR(255),
                            create_timestamp TIMESTAMPTZ, 
                            application_id INTEGER)""")

            cursor.execute("""
                        INSERT INTO saef_job
                        VALUES
                            ( 1, 'LoadDimCustomer', 'Customer dimension from source tables', '2020-04-23T21:13:59.440Z+02', 2 ),
                            ( 2, 'LoadProduct', 'Loads Production dimension', '2020-04-24T19:01:07.145Z+02', 2 ),
                            ( 3, 'LoadSales', 'The job that loads Sales Fact', '2020-04-24T19:01:33.280Z+02', 2 ),
                            ( 4, 'test2', 'descr for test 2', '2020-05-30T12:51:55.485Z+02', 20 )
                        """)
        except Exception as e:
            print(e)
       
        try:
            # AzureSQL test database
            print(f'CREATING AZURE TEST DATABASE')
            
            configration = {'TEST_AZURE_DB_NAME': TEST_AZURE_DB_NAME,
                'TEST_AZURE_USERNAME': TEST_AZURE_USERNAME,
                'TEST_AZURE_PASSWORD': TEST_AZURE_PASSWORD,
                'TEST_AZURE_HOST': TEST_AZURE_HOST,
                'TEST_AZURE_PORT': TEST_AZURE_PORT}

            validate_configuration(configration)

            drivers = [item for item in pyodbc.drivers()]
            connection_string = f'DRIVER={drivers[-1]};SERVER={TEST_AZURE_HOST};PORT={TEST_AZURE_PORT};DATABASE={TEST_AZURE_DB_NAME};UID={TEST_AZURE_USERNAME};PWD={TEST_AZURE_PASSWORD}'

            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            cursor.execute("""
                    CREATE TABLE saef_job 
                    (id INTEGER PRIMARY KEY, 
                    name VARCHAR(255), 
                    description VARCHAR(255),
                    create_timestamp datetime, 
                    application_id INTEGER)""")

            cursor.execute("""
                        INSERT INTO saef_job
                        VALUES
                            ( 1, 'LoadDimCustomer', 'Customer dimension from source tables', '2020-04-23T21:13:59.440', 2 ),
                            ( 2, 'LoadProduct', 'Loads Production dimension', '2020-04-24T19:01:07.145', 2 ),
                            ( 3, 'LoadSales', 'The job that loads Sales Fact', '2020-04-24T19:01:33.280', 2 ),
                            ( 4, 'test2', 'descr for test 2', '2020-05-30T12:51:55.485', 20 )
                        """)
        except Exception as e:
            print(e)


            
    def prompt_start_server(self):
        print (f'-----------------------------------------')
        print('SYSTEM IS NOW READY TO RUN')
        if args.r:
            self.start_server()
        else:
            print('START SERVER? Y/N')
            inp = input()
            if inp.lower() == 'y':
                self.start_server()

    def start_server(self):
        subprocess.run(["python", "manage.py", "runserver"])
                    
    def restart_celery(self):
        subprocess.run(["systemctl", "restart ", "celery"])

    def create_super_user(self):
        print (f'-----------------------------------------')
        try:
            import os
            os.environ['DJANGO_SETTINGS_MODULE'] = 'saefportal.settings'
            import django
            django.setup()
            from users.models import User

            email = 't@test.com'
            password = 'test'

            if args.su:
                email = args.su
            if args.sp:
                password = args.sp
                
            print(f'CREATING SUPER USER - {email} {password}')
                
            User.objects.create_superuser(email, password)
        except Exception:
            print('An superuser with that email already exists')

    def load_sample_data(self):
        print (f'-----------------------------------------')
        print('IMPORTING SAMPLE DATA INTO THE DATABASE')
        if args.loaddata:
            subprocess.run(["python", "manage.py", "loaddata", args.loaddata])
        else:
            files = glob.glob("../database/data/development/*.json")
            run_command = ["python", "manage.py", "loaddata"]
            run_command.extend(files)
            subprocess.run(run_command)
            
    def migrate(self):
        print (f'-----------------------------------------')
        print('MIGRATE')
        subprocess.run(["python", "manage.py", "migrate"])

    def make_migrations(self):
        print (f'-----------------------------------------')
        print('MAKING MIGRATIONS')
        subprocess.run(["python", "manage.py", "makemigrations"])

    def initialize(self):
        if args.forceclean:
            if not args.s:
                self.prompt_verify_dropping_database()
                
            self.terminate_connections()
            self.drop_database(self.default_db)
            self.create_database_super_user()
            self.create_database(self.default_db)
            
        if args.t:
            self.setup_test_database()

        self.make_migrations()
        self.migrate()
        self.create_super_user()
        self.load_sample_data()
        if args.restart:
            self.restart_celery()
        if args.r or not args.s:
            self.prompt_start_server()


if __name__ == "__main__":
    i = Initialize()
    i.initialize()