import pytest

from django.core.management import call_command

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'crm.json')


@pytest.fixture
def management_user(db):
    return ("00000001", 'test')


@pytest.fixture
def general_user(db):
    return ("00000002", 'test')


@pytest.fixture
def sales_user(db):
    return ("00000003", 'test')
