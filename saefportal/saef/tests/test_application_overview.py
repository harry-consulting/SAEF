import pytz
from datetime import datetime, timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from mock import Mock
from saef.models import ApplicationSessionMetaData

from utils.test_utils import load_test_database, load_test_db


class ApplicationOverviewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_test_database('users.user')
        load_test_database('saef.connectiontype')
        load_test_database('saef.connection')
        load_test_database('saef.postgresconnection')
        load_test_database('saef.applicationtoken')
        load_test_database('saef.application')
        load_test_database('saef.applicationsession')
        load_test_db('saef', 'test_application_overview')

    def setUp(self):
        self.client.login(email='t@test.com', password='test')

    def test_application_overview_view_get(self):
        response = self.client.get(reverse('application_session'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'application_overview/application_overview.html')

        expected = ApplicationSessionMetaData.objects.filter().count()
        self.assertEqual(len(response.context['application_sessions_metadata']), expected)

    def test_application_overview_filter_status_all(self):
        response = self.client.get(reverse('application_session') + '?status_option=All+status')
        self.assertEqual(response.status_code, 200)

        expected = ApplicationSessionMetaData.objects.filter().count()
        self.assertEqual(len(response.context['application_sessions_metadata']), expected)
        
    def test_application_overview_filter_status_succeeded(self):
        response = self.client.get(reverse('application_session') + '?status_option=Succeeded')
        self.assertEqual(response.status_code, 200)

        expected = ApplicationSessionMetaData.objects.filter(status_type='SUCCEEDED').count()
        self.assertEqual(len(response.context['application_sessions_metadata']), expected)
        
        for application in response.context['application_sessions_metadata']:
            self.assertEqual(application.status_type, 'SUCCEEDED')

    def test_application_overview_filter_status_succeeded_with_issue(self):
        response = self.client.get(reverse('application_session') + '?status_option=Succeeded+with+issue')
        self.assertEqual(response.status_code, 200)

        expected = ApplicationSessionMetaData.objects.filter(status_type='SUCCEEDED_ISSUE').count()
        self.assertEqual(len(response.context['application_sessions_metadata']), expected)
        
        for application in response.context['application_sessions_metadata']:
            self.assertEqual(application.status_type, 'SUCCEEDED_ISSUE')

    def test_application_overview_filter_status_failed(self):
        response = self.client.get(reverse('application_session') + '?status_option=Failed')
        self.assertEqual(response.status_code, 200)

        expected = ApplicationSessionMetaData.objects.filter(status_type='FAILED').count()
        self.assertEqual(len(response.context['application_sessions_metadata']), expected)
        
        for application in response.context['application_sessions_metadata']:
            self.assertEqual(application.status_type, 'FAILED')     
               
    def test_application_overview_filter_date_all(self):
        response = self.client.get(reverse('application_session') + '?date_option=All')
        self.assertEqual(response.status_code, 200)
        expected = ApplicationSessionMetaData.objects.filter().count()
        self.assertEqual(len(response.context['application_sessions_metadata']), expected)
        
    def test_application_overview_filter_date_last_7_days(self):
        date_now_mock = datetime(2020, 8, 12, 15, 37, 26, 179787, tzinfo=pytz.utc)
        timezone.now = Mock(return_value=date_now_mock)
        response = self.client.get(reverse('application_session') + '?date_option=7+days')
        self.assertEqual(response.status_code, 200)

        past_7 = date_now_mock + timedelta(days=-7)
        expected = ApplicationSessionMetaData.objects.filter(application_session__create_timestamp__gte=past_7).count()
        self.assertEqual(len(response.context['application_sessions_metadata']), expected)
        
        for application in response.context['application_sessions_metadata']:
            self.assertGreaterEqual(application.application_session.create_timestamp, past_7)  
            
    def test_application_overview_filter_date_last_31_days(self):
        date_now_mock = datetime(2020, 8, 12, 15, 37, 26, 179787, tzinfo=pytz.utc)
        timezone.now = Mock(return_value=date_now_mock)
        response = self.client.get(reverse('application_session') + '?date_option=1+month')
        self.assertEqual(response.status_code, 200)

        past_31 = date_now_mock + timedelta(days=-31)
        expected = ApplicationSessionMetaData.objects.filter(application_session__create_timestamp__gte=past_31).count()
        self.assertEqual(len(response.context['application_sessions_metadata']), expected)

        for application in response.context['application_sessions_metadata']:
            self.assertGreaterEqual(application.application_session.create_timestamp, past_31)  
            
    def test_application_overview_filter_multiple_arguments_daterange31_statustype(self):
        date_now_mock = datetime(2020, 8, 12, 15, 37, 26, 179787, tzinfo=pytz.utc)
        timezone.now = Mock(return_value=date_now_mock)
        response = self.client.get(reverse('application_session') + '?date_option=1+month&status_option=Succeeded')
        self.assertEqual(response.status_code, 200)

        past_31 = date_now_mock + timedelta(days=-31)
        expected = ApplicationSessionMetaData.objects.filter(application_session__create_timestamp__gte=past_31, 
                                                             status_type='SUCCEEDED').count()
        self.assertEqual(len(response.context['application_sessions_metadata']), expected)
            
    def test_application_overview_filter_orderby(self):
        response = self.client.get(reverse('application_session') + '?order_by=-status_type')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['application_sessions_metadata'][0].status_type, 'SUCCEEDED_ISSUE')
        self.assertEqual(response.context['application_sessions_metadata'][1].status_type, 'SUCCEEDED')
        self.assertEqual(response.context['application_sessions_metadata'][2].status_type, 'FAILED')
        
        response = self.client.get(reverse('application_session') + '?order_by=status_type')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['application_sessions_metadata'][0].status_type, 'FAILED')
        self.assertEqual(response.context['application_sessions_metadata'][1].status_type, 'SUCCEEDED')
        self.assertEqual(response.context['application_sessions_metadata'][2].status_type, 'SUCCEEDED_ISSUE')

        response = self.client.get(reverse('application_session') + '?order_by=-execution_time')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['application_sessions_metadata'][0].actual_execution_time, timedelta(days=12, 
                                                                                                               seconds=74809, 
                                                                                                               microseconds=75498))
        self.assertEqual(response.context['application_sessions_metadata'][1].actual_execution_time, timedelta(seconds=19, 
                                                                                                               microseconds=945057))
        self.assertEqual(response.context['application_sessions_metadata'][2].actual_execution_time, timedelta(seconds=12, 
                                                                                                               microseconds=136567))

        response = self.client.get(reverse('application_session') + '?order_by=execution_time')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['application_sessions_metadata'][0].actual_execution_time, timedelta(seconds=12, 
                                                                                                               microseconds=136567))
        self.assertEqual(response.context['application_sessions_metadata'][1].actual_execution_time, timedelta(seconds=19,
                                                                                                                microseconds=945057))
        self.assertEqual(response.context['application_sessions_metadata'][2].actual_execution_time, timedelta(days=12, 
                                                                                                               seconds=74809, 
                                                                                                               microseconds=75498))
