import copy
from datetime import datetime
from unittest.mock import call

import pytest
from flask import url_for
from freezegun import freeze_time

import app
from app.main.views.providers import add_monthly_traffic
from tests.conftest import normalize_spaces

stub_providers = {
    'provider_details': [
        {
            'id': '6005e192-4738-4962-beec-ebd982d0b03f',
            'active': True,
            'priority': 1,
            'display_name': 'Domestic SMS Provider',
            'identifier': 'first_sms_domestic',
            'notification_type': 'sms',
            'updated_at': datetime(2017, 1, 16, 15, 20, 40).isoformat(),
            'version': 1,
            'created_by_name': 'Test User',
            'supports_international': False,
            'current_month_billable_sms': 5020,
        },
        {
            'id': '0bd529cd-a0fd-43e5-80ee-b95ef6b0d51f',
            'active': True,
            'priority': 2,
            'display_name': 'Second Domestic SMS Provider',
            'identifier': 'second_sms_domestic',
            'notification_type': 'sms',
            'updated_at': None,
            'version': 1,
            'created_by': None,
            'supports_international': False,
            'current_month_billable_sms': 6891,
        },
        {
            'id': '6005e192-4738-4962-beec-ebd982d0b03a',
            'active': True,
            'priority': 1,
            'display_name': 'first_email_provider',
            'identifier': 'first_email',
            'notification_type': 'email',
            'updated_at': None,
            'version': 1,
            'created_by': None,
            'supports_international': False,
            'current_month_billable_sms': 0,
        },
        {
            'active': True,
            'priority': 2,
            'display_name': 'second_email_provider',
            'identifier': 'second_email',
            'id': '0bd529cd-a0fd-43e5-80ee-b95ef6b0d51b',
            'notification_type': 'email',
            'updated_at': None,
            'version': 1,
            'created_by': None,
            'supports_international': False,
            'current_month_billable_sms': 0,
        },
        {
            'id': '67c770f5-918e-4afa-a5ff-880b9beb161d',
            'active': False,
            'priority': 10,
            'display_name': 'First International SMS Provider',
            'identifier': 'first_sms_international',
            'notification_type': 'sms',
            'updated_at': None,
            'version': 1,
            'created_by': None,
            'supports_international': True,
            'current_month_billable_sms': 0,
        },
        {
            'id': '67c770f5-918e-4afa-a5ff-880b9beb161d',
            'active': False,
            'priority': 10,
            'display_name': 'Second International SMS Provider',
            'identifier': 'second_sms_international',
            'notification_type': 'sms',
            'updated_at': None,
            'version': 1,
            'created_by': None,
            'supports_international': True,
            'current_month_billable_sms': 0,
        }
    ]
}

stub_provider = {
    'provider_details':
        {
            'id': '6005e192-4738-4962-beec-ebd982d0b03f',
            'active': True,
            'priority': 1,
            'display_name': 'Domestic SMS Provider',
            'identifier': 'first_sms_domestic',
            'notification_type': 'sms',
            'updated_at': None,
            'version': 1,
            'created_by': None,
            'supports_international': False
        }
}

stub_provider_history = {
    'data': [
        {
            'id': 'f9af1ec7-58ef-4f7d-a6f4-5fe7e48644cb',
            'active': True,
            'priority': 20,
            'display_name': 'Foo',
            'identifier': 'foo',
            'notification_type': 'sms',
            'updated_at': None,
            'version': 2,
            'created_by': {
                'email_address': 'test@foo.bar',
                'name': 'Test User',
                'id': '7cc1dddb-bcbc-4739-8fc1-61bedde3332a'
            },
            'supports_international': False
        },
        {
            'id': 'f9af1ec7-58ef-4f7d-a6f4-5fe7e48644cb',
            'active': True,
            'priority': 10,
            'display_name': 'Bar',
            'identifier': 'bar',
            'notification_type': 'sms',
            'updated_at': None,
            'version': 1,
            'created_by': None,
            'supports_international': False
        }
    ]
}


def test_should_show_all_providers(
    client_request,
    platform_admin_user,
    mocker,
):
    mocker.patch('app.provider_client.get_all_providers', return_value=copy.deepcopy(stub_providers))

    client_request.login(platform_admin_user)
    page = client_request.get('main.view_providers')

    h1 = [header.text.strip() for header in page.find_all('h1')]

    assert 'Providers' in h1

    h2 = [header.text.strip() for header in page.find_all('h2')]

    assert 'Email' in h2
    assert 'SMS' in h2

    tables = page.find_all('table')
    assert len(tables) == 3

    domestic_sms_table = tables[0]
    domestic_email_table = tables[1]
    international_sms_table = tables[2]

    domestic_sms_first_row = domestic_sms_table.tbody.find_all('tr')[0]
    table_data = domestic_sms_first_row.find_all('td')

    assert not table_data[0].find_all("a")
    assert table_data[0].text.strip() == "Domestic SMS Provider"
    assert table_data[1].text.strip() == "1"
    assert table_data[2].text.strip() == "42"
    assert table_data[3].text.strip() == "True"
    assert table_data[4].text.strip() == "16 January at 3:20pm"
    assert table_data[5].text.strip() == "Test User"

    domestic_sms_second_row = domestic_sms_table.tbody.find_all('tr')[1]
    table_data = domestic_sms_second_row.find_all('td')

    assert not table_data[0].find_all("a")
    assert table_data[0].text.strip() == "Second Domestic SMS Provider"
    assert table_data[1].text.strip() == "2"
    assert table_data[2].text.strip() == "58"
    assert table_data[3].text.strip() == "True"
    assert table_data[4].text.strip() == "None"
    assert table_data[5].text.strip() == "None"

    domestic_email_first_row = domestic_email_table.tbody.find_all('tr')[0]
    domestic_email_table_data = domestic_email_first_row.find_all('td')

    assert domestic_email_table_data[0].find_all("a")[0]['href'] == '/provider/6005e192-4738-4962-beec-ebd982d0b03a'
    assert domestic_email_table_data[0].text.strip() == "first_email_provider"
    assert domestic_email_table_data[1].text.strip() == "1"
    assert domestic_email_table_data[2].text.strip() == "True"
    assert domestic_email_table_data[3].text.strip() == "None"
    assert domestic_email_table_data[4].text.strip() == "None"
    assert domestic_email_table_data[5].find_all("a")[0]['href'] \
        == '/provider/6005e192-4738-4962-beec-ebd982d0b03a/edit'

    domestic_email_second_row = domestic_email_table.tbody.find_all('tr')[1]
    domestic_email_table_data = domestic_email_second_row.find_all('td')

    assert domestic_email_table_data[0].find_all("a")[0]['href'] == '/provider/0bd529cd-a0fd-43e5-80ee-b95ef6b0d51b'
    assert domestic_email_table_data[0].text.strip() == "second_email_provider"
    assert domestic_email_table_data[1].text.strip() == "2"
    assert domestic_email_table_data[2].text.strip() == "True"
    assert domestic_email_table_data[3].text.strip() == "None"
    assert domestic_email_table_data[4].text.strip() == "None"
    assert domestic_email_table_data[5].find_all("a")[0]['href'] \
        == '/provider/0bd529cd-a0fd-43e5-80ee-b95ef6b0d51b/edit'

    international_sms_first_row = international_sms_table.tbody.find_all('tr')[0]
    table_data = international_sms_first_row.find_all('td')

    assert table_data[0].find_all("a")[0]['href'] == '/provider/67c770f5-918e-4afa-a5ff-880b9beb161d'
    assert table_data[0].text.strip() == "First International SMS Provider"
    assert table_data[1].text.strip() == "10"
    assert table_data[2].text.strip() == "False"
    assert table_data[3].text.strip() == "None"
    assert table_data[4].text.strip() == "None"


def test_add_monthly_traffic():
    domestic_sms_providers = [{
        'identifier': 'mmg',
        'current_month_billable_sms': 27,
    }, {
        'identifier': 'firetext',
        'current_month_billable_sms': 5,
    }, {
        'identifier': 'loadtesting',
        'current_month_billable_sms': 0,
    }]

    add_monthly_traffic(domestic_sms_providers)

    assert domestic_sms_providers == [{
        'identifier': 'mmg',
        'current_month_billable_sms': 27,
        'monthly_traffic': 84
    }, {
        'identifier': 'firetext',
        'current_month_billable_sms': 5,
        'monthly_traffic': 16
    }, {
        'identifier': 'loadtesting',
        'current_month_billable_sms': 0,
        'monthly_traffic': 0
    }]


def test_should_show_edit_provider_form(
    client_request,
    platform_admin_user,
    mocker,
    fake_uuid,
):
    mocker.patch('app.provider_client.get_provider_by_id', return_value=copy.deepcopy(stub_provider))

    client_request.login(platform_admin_user)
    page = client_request.get('main.edit_provider', provider_id=fake_uuid)

    h1 = [header.text.strip() for header in page.find_all('h1')]

    assert 'Domestic SMS Provider' in h1

    form = [form for form in page.find_all('form')]

    form_elements = [element for element in form[0].find_all('input')]
    assert form_elements[0]['value'] == '1'
    assert form_elements[0]['name'] == 'priority'


def test_should_show_error_on_bad_provider_priority(
    client_request,
    platform_admin_user,
    mocker,
):
    mocker.patch('app.provider_client.get_provider_by_id', return_value=copy.deepcopy(stub_provider))

    client_request.login(platform_admin_user)
    page = client_request.post(
        'main.edit_provider',
        provider_id=stub_provider['provider_details']['id'],
        _data={'priority': "not valid"},
        _expected_status=200,
    )

    assert normalize_spaces(
        page.select_one('.govuk-error-message').text
    ) == "Error: Not a valid integer value."


def test_should_show_error_on_negative_provider_priority(
    client_request,
    platform_admin_user,
    mocker,
):
    mocker.patch('app.provider_client.get_provider_by_id', return_value=copy.deepcopy(stub_provider))

    client_request.login(platform_admin_user)
    page = client_request.post(
        'main.edit_provider',
        provider_id=stub_provider['provider_details']['id'],
        _data={'priority': -1},
        _expected_status=200,
    )

    assert normalize_spaces(
        page.select_one('.govuk-error-message').text
    ) == "Error: Must be between 1 and 100"


def test_should_show_error_on_too_big_provider_priority(
    client_request,
    platform_admin_user,
    mocker,
):
    mocker.patch('app.provider_client.get_provider_by_id', return_value=copy.deepcopy(stub_provider))

    client_request.login(platform_admin_user)
    page = client_request.post(
        'main.edit_provider',
        provider_id=stub_provider['provider_details']['id'],
        _data={'priority': 101},
        _expected_status=200,
    )

    assert normalize_spaces(
        page.select_one('.govuk-error-message').text
    ) == "Error: Must be between 1 and 100"


def test_should_show_error_on_too_little_provider_priority(
    client_request,
    platform_admin_user,
    mocker,
):
    mocker.patch('app.provider_client.get_provider_by_id', return_value=copy.deepcopy(stub_provider))

    client_request.login(platform_admin_user)
    page = client_request.post(
        'main.edit_provider',
        provider_id=stub_provider['provider_details']['id'],
        _data={'priority': 0},
        _expected_status=200,
    )

    assert normalize_spaces(
        page.select_one('.govuk-error-message').text
    ) == "Error: Must be between 1 and 100"


def test_should_update_provider_priority(
    client_request,
    platform_admin_user,
    mocker,
):
    mocker.patch('app.provider_client.get_provider_by_id', return_value=copy.deepcopy(stub_provider))
    mocker.patch('app.provider_client.update_provider', return_value=copy.deepcopy(stub_provider))

    client_request.login(platform_admin_user)
    client_request.post(
        'main.edit_provider',
        provider_id=stub_provider['provider_details']['id'],
        _data={'priority': 2},
        _expected_redirect='http://localhost/providers',
    )

    app.provider_client.update_provider.assert_called_with(stub_provider['provider_details']['id'], 2)


def test_should_show_provider_version_history(
    client_request,
    platform_admin_user,
    mocker
):
    mocker.patch('app.provider_client.get_provider_versions', return_value=copy.deepcopy(stub_provider_history))

    client_request.login(platform_admin_user)
    page = client_request.get(
        'main.view_provider', provider_id=stub_provider_history['data'][0]['id']
    )

    table = page.find('table')
    table_rows = table.find_all('tr')
    table_headings = table_rows[0].find_all('th')
    first_row = table_rows[1].find_all('td')
    second_row = table_rows[2].find_all('td')

    assert page.find_all('h1')[0].text.strip() == stub_provider_history['data'][0]["display_name"]
    assert len(table_rows) == 3

    assert table_headings[0].text.strip() == "Version"
    assert table_headings[1].text.strip() == "Last Updated"
    assert table_headings[2].text.strip() == "Updated By"
    assert table_headings[3].text.strip() == "Priority"
    assert table_headings[4].text.strip() == "Active"

    assert first_row[0].text.strip() == "2"
    assert first_row[1].text.strip() == "None"
    assert first_row[2].text.strip() == "Test User"
    assert first_row[3].text.strip() == "20"
    assert first_row[4].text.strip() == "True"

    assert second_row[0].text.strip() == "1"
    assert second_row[1].text.strip() == "None"
    assert second_row[2].text.strip() == "None"
    assert second_row[3].text.strip() == "10"
    assert second_row[4].text.strip() == "True"


@freeze_time('2022-2-22 15:00')
def test_should_show_version_history_for_first_two_sms_providers(
    client_request,
    platform_admin_user,
    mocker
):
    mocker.patch(
        'app.provider_client.get_all_providers',
        return_value=copy.deepcopy(stub_providers)
    )
    # second_sms_international will be the primary provider because it’s
    # the first in the list when reverse sorting the SMS providers
    second_sms_international = stub_providers['provider_details'][5]
    mocker.patch(
        'app.provider_client.get_provider_versions',
        return_value={'data': [
            {
                'id': id,
                'priority': priority,
                'display_name': second_sms_international['display_name'],
                'identifier': second_sms_international['identifier'],
                'updated_at': updated_at,
                'created_by': {
                    'email_address': 'test@foo.bar',
                    'name': 'Test User',
                    'id': '7cc1dddb-bcbc-4739-8fc1-61bedde3332a'
                },
                'supports_international': False,
            }
            for updated_at, priority in [
                (datetime(2022, 2, 22, 14).isoformat(), 100),
                (datetime(2020, 1, 1, 5).isoformat(), 80),
                (datetime(2020, 1, 1, 3).isoformat(), 10),
                # Anything older than 11am on 29 November 2019
                # should be ignored because the priority numbers
                # didn’t mean the same thing before then
                (datetime(2019, 11, 29, 10, 59).isoformat(), 123),
                (datetime(2000, 1, 1, 0).isoformat(), 1999),
                (None, 30),
            ]
        ]}
    )

    client_request.login(platform_admin_user)
    page = client_request.get('main.edit_sms_provider_ratio')

    assert [
        radio['value']
        for radio in page.select('input[name=ratio]')
    ] == [
        '100', '90', '80', '70', '60', '50', '40', '30', '20', '10', '0',
    ]

    assert [
        radio['value']
        for radio in page.select('input[checked]')
    ] == [
        str(second_sms_international['priority'])
    ]

    assert [
        normalize_spaces(heading.text)
        for heading in page.select('main h2')
    ] == [
        'Now',
        'Today',
        '1 January 2020',
    ]

    assert [
        normalize_spaces(version.text)
        for version in page.select('li.history-list-item')
    ] == [
        (
            'Test User 2:00pm '
            'Second International SMS Provider 100% '
            'Second Domestic SMS Provider 0%'
        ),
        (
            'Test User 5:00am '
            'Second International SMS Provider 80% '
            'Second Domestic SMS Provider 20%'
        ),
        (
            'Test User 3:00am '
            'Second International SMS Provider 10% '
            'Second Domestic SMS Provider 90%'
        ),
    ]


@pytest.mark.parametrize('posted_number, expected_calls', [
    (
        '10',
        [
            call(stub_providers['provider_details'][5]['id'], 10),
            call(stub_providers['provider_details'][1]['id'], 90),
        ],
    ),
    (
        '80',
        [
            call(stub_providers['provider_details'][5]['id'], 80),
            call(stub_providers['provider_details'][1]['id'], 20),
        ],
    ),
])
def test_should_update_priority_of_first_two_sms_providers(
    client_request,
    platform_admin_user,
    mocker,
    posted_number,
    expected_calls,
):
    mocker.patch(
        'app.provider_client.get_all_providers',
        return_value=copy.deepcopy(stub_providers)
    )
    mocker.patch(
        'app.provider_client.get_provider_versions',
        return_value={'data': []}
    )
    mock_update_provider = mocker.patch(
        'app.provider_client.update_provider'
    )

    client_request.login(platform_admin_user)
    client_request.post(
        '.edit_sms_provider_ratio',
        _data={
            'ratio': posted_number,
        },
        _expected_redirect=url_for(
            '.edit_sms_provider_ratio',
            _external=True,
        ),
    )

    assert mock_update_provider.call_args_list == expected_calls
