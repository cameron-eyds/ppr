# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests to verify the pay-api integration.

Test-Suite to ensure that the client for the pay-api service is working as expected.
"""
import json
import os
from http import HTTPStatus

import pytest

from mhr_api.services.payment.client import SBCPaymentClient, ApiRequestError
from mhr_api.services.payment import TransactionTypes
from mhr_api.services.payment.payment import Payment
from mhr_api.services.payment.exceptions import SBCPaymentException
from mhr_api.services.authz import MHR_ROLE
from tests.unit.services.utils import helper_create_jwt


MOCK_URL_NO_KEY = 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/pay/api/v1/'
MOCK_URL = 'https://bcregistry-bcregistry-mock.apigee.net/pay/api/v1/'
PAY_DETAILS_SEARCH = {
    'label': 'Search by SERIAL_NUMBER',
    'value': '123456789'
}
PAY_DETAILS_REGISTRATION = {
    'label': 'Reg Number',
    'value': '100468B'
}

SELECT_MHR_ONLY = [
    {'mhrNumber': '022911', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
     'homeLocation': 'FORT NELSON', 'includeLienInfo': False, 'serialNumber': '2427',
     'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
     'ownerName': {'first': 'PRITNAM', 'last': 'SANDHU'}}
]
SELECT_COMBO_ONLY = [
    {'mhrNumber': '022911', 'status': 'EXEMPT', 'createDateTime': '1995-11-14T00:00:01+00:00',
     'homeLocation': 'FORT NELSON', 'includeLienInfo': True, 'serialNumber': '2427',
     'baseInformation': {'year': 1968, 'make': 'GLENDALE', 'model': ''},
     'ownerName': {'first': 'PRITNAM', 'last': 'SANDHU'}}
]
SELECT_BOTH = [
    {
        'baseInformation': {
            'make': 'FLASHBACK',
            'model': '',
            'year': 1984
        },
        'createDateTime': '1995-11-14T00:00:01+00:00',
        'homeLocation': 'SICAMOUS',
        'mhrNumber': '074026',
        'includeLienInfo': False,
        'ownerName': {
            'first': 'DAVID',
            'last': 'HAMM',
            'middle': 'ABRAM'
        },
        'serialNumber': '117',
        'status': 'ACTIVE'
    },
    {
        'baseInformation': {
            'make': '3 BEDROOM',
            'model': '',
            'year': 1973
        },
        'createDateTime': '1995-11-14T00:00:01+00:00',
        'homeLocation': 'INVERMERE',
        'mhrNumber': '024289',
        'includeLienInfo': True,
        'ownerName': {
            'first': 'DAVID',
            'last': 'HAMM',
            'middle': 'WAYNE'
        },
        'serialNumber': '68MA0970',
        'status': 'ACTIVE'
    }
]


# testdata pattern is ({filing_type}, {selection}, {staff})
TEST_PAY_TYPE_FILING_TYPE_SEARCH = [
    ('MSRCH', SELECT_MHR_ONLY, False),
    ('CSRCH', SELECT_COMBO_ONLY, False),
    ('MSRCS', SELECT_MHR_ONLY, True),
    ('CSRCS', SELECT_COMBO_ONLY, True)
]
# testdata pattern is ({desc}, {selection}, {trans_id}, {client_id}, {mhr_count}, {combo_count}, {staff})
TEST_PAYMENT_DATA_SEARCH = [
    ('Search MHR', SELECT_MHR_ONLY, '1234', 'UT-00001', 1, 0, False),
    ('Search Combo', SELECT_COMBO_ONLY, '1234', 'UT-00001', 0, 1, False),
    ('Search Both', SELECT_BOTH, '1234', 'UT-00001', 1, 1, False),
    ('Search No Trans ID', SELECT_MHR_ONLY, None, 'UT-00001', 1, 0, False),
    ('Search No Client Ref', SELECT_MHR_ONLY, '1234', None, 1, 0, False),
    ('Search No Trans ID or Client Ref', SELECT_MHR_ONLY, None, None, 1, 0, False),
    ('Search Staff MHR', SELECT_MHR_ONLY, '1234', 'UT-00001', 1, 0, True),
    ('Search Staff Combo', SELECT_COMBO_ONLY, '1234', 'UT-00001', 0, 1, True),
    ('Search Staff Both', SELECT_BOTH, '1234', 'UT-00001', 1, 1, True)
]

# testdata pattern is ({selection}, {pay_trans_type}, {routingSlip}, {bcolNumber}, 'datNUmber', 'waiveFees')
TEST_PAY_STAFF_SEARCH = [
    (SELECT_MHR_ONLY, '12345', None, None, False),
    (SELECT_MHR_ONLY, None, '62345', None, False),
    (SELECT_MHR_ONLY, None, '62345', '72345', False),
    (SELECT_MHR_ONLY, None, None, None, True),
    (SELECT_COMBO_ONLY, '12345', None, None, False),
    (SELECT_COMBO_ONLY, None, '62345', None, False),
    (SELECT_COMBO_ONLY, None, '62345', '72345', False),
    (SELECT_COMBO_ONLY, None, None, None, True)
]
# testdata pattern is ({desc}, {selection}, {pay_url}, {details}, {error})
TEST_PAYMENT_MOCK = [
    ('Valid detail', SELECT_MHR_ONLY, MOCK_URL_NO_KEY, PAY_DETAILS_REGISTRATION, False),
    ('Valid no detail', SELECT_MHR_ONLY, MOCK_URL_NO_KEY, None, False),
    ('Unauthorized', SELECT_MHR_ONLY, MOCK_URL, None, True)
]

@pytest.mark.parametrize('selection,routing_slip,bcol_number,dat_number,waive_fees', TEST_PAY_STAFF_SEARCH)
def test_payment_data_staff_search(client, jwt, selection, routing_slip, bcol_number, dat_number, waive_fees):
    """Assert that the staff payment payment-request body is as expected for a pay transaction type."""
    transaction_info = {
    }
    if routing_slip:
        transaction_info['routingSlipNumber'] = routing_slip
    if bcol_number:
        transaction_info['bcolAccountNumber'] = bcol_number
    if dat_number:
        transaction_info['datNumber'] = dat_number
    if waive_fees:
        transaction_info['waiveFees'] = True
    # test
    data = SBCPaymentClient.create_payment_staff_search_data(selection, transaction_info, 'TEST', 'UT-PAY-0001')
    # check
    assert data
    assert len(data['filingInfo']['filingTypes']) == 1
    if waive_fees:
        assert data['filingInfo']['filingTypes'][0]['waiveFees']
    else:
        assert 'waiveFees' not in data['filingInfo']['filingTypes'][0]

    if not routing_slip and not bcol_number:
        assert 'accountInfo' not in data
    elif routing_slip:
        assert 'accountInfo' in data and data['accountInfo']['routingSlip'] == routing_slip
    elif bcol_number:
        assert 'accountInfo' in data and data['accountInfo']['bcolAccountNumber'] == bcol_number
        if dat_number:
            assert data['accountInfo']['datNumber'] == dat_number


@pytest.mark.parametrize('filing_type,selection,staff', TEST_PAY_TYPE_FILING_TYPE_SEARCH)
def test_payment_filing_type_search(client, jwt, filing_type, selection, staff):
    """Assert that the payment-request body filing type is as expected for a pay transaction type."""
    # setup

    # test
    data = SBCPaymentClient.create_payment_search_data(selection, '200000000', 'UT-PAY-0001', staff)
    # check
    assert data
    assert data['filingInfo']['filingIdentifier'] == '200000000'
    assert data['filingInfo']['folioNumber'] == 'UT-PAY-0001'
    assert len(data['filingInfo']['filingTypes']) == 1
    assert data['filingInfo']['filingTypes'][0]['quantity'] == 1
    assert data['filingInfo']['filingTypes'][0]['filingTypeCode'] == filing_type
    assert data['businessInfo']['corpType'] == 'MHR'


@pytest.mark.parametrize('desc,selection,trans_id,client_id,mhr_count,combo_count,staff', TEST_PAYMENT_DATA_SEARCH)
def test_payment_data_search(client, jwt, desc, selection, trans_id, client_id, mhr_count, combo_count, staff):
    """Assert that the payment-request body filing type is as expected for a search transactions."""
    # setup
    data = None
    # test
    data = SBCPaymentClient.create_payment_search_data(selection, trans_id, client_id, staff)
    # check
    assert data
    if trans_id:
        assert data['filingInfo']['filingIdentifier'] == trans_id
    else:
        assert 'filingIdentifier' not in data['filingInfo']
    if client_id:
        assert data['filingInfo']['folioNumber'] == client_id
    else:
        assert 'folioNumber' not in data['filingInfo']

    assert data['businessInfo']['corpType'] == 'MHR'
    assert len(data['filingInfo']['filingTypes']) == (mhr_count + combo_count)
    if mhr_count > 0:
        assert data['filingInfo']['filingTypes'][0]['quantity'] == mhr_count
    elif combo_count > 0 and mhr_count == 0:
        assert data['filingInfo']['filingTypes'][0]['quantity'] == combo_count
    if combo_count > 0 and mhr_count > 0:
        assert data['filingInfo']['filingTypes'][1]['quantity'] == combo_count

    assert data['filingInfo']['filingTypes'][0]['quantity'] == 1


@pytest.mark.parametrize('selection,routing_slip,bcol_number,dat_number,waive_fees', TEST_PAY_STAFF_SEARCH)
def test_payment_staff_search_mock(session, client, jwt, selection, routing_slip, bcol_number, dat_number, waive_fees):
    """Assert that a pay-api staff search payment request works as expected with the mock service endpoint."""
    # setup
    token = helper_create_jwt(jwt, [MHR_ROLE])
    payment = Payment(jwt=token, account_id='PS12345', details=PAY_DETAILS_SEARCH)
    payment.api_url = MOCK_URL_NO_KEY
    transaction_info = {
    }
    if routing_slip:
        transaction_info['routingSlipNumber'] = routing_slip
    if bcol_number:
        transaction_info['bcolAccountNumber'] = bcol_number
    if dat_number:
        transaction_info['datNumber'] = dat_number
    if waive_fees:
        transaction_info['waiveFees'] = True
 
    # test
    pay_data = payment.create_payment_staff_search(selection, transaction_info, 'TEST-MOCK', 'UT-PAY-SEARCH-01')
    # print(pay_data)
    # check
    assert pay_data
    assert pay_data['invoiceId']
    assert pay_data['receipt']


@pytest.mark.parametrize('desc,selection,pay_url,details,error', TEST_PAYMENT_MOCK)
def test_client_search_mock(session, client, jwt, desc, selection, pay_url, details, error):
    """Assert that a pay-api client works as expected with the mock service endpoint."""
    # setup
    token = helper_create_jwt(jwt, [MHR_ROLE])
    pay_client = SBCPaymentClient(jwt=token, account_id='PS12345', details=details)
    pay_client.api_url = pay_url

    # test
    if error:
        with pytest.raises(ApiRequestError) as request_err:
            pay_data = pay_client.create_payment_search(selection, '200000001', 'UT-PAY-SEARCH-01', False)
    else:
        pay_data = pay_client.create_payment_search(selection, '200000001', 'UT-PAY-SEARCH-01', False)

    # print(pay_data)
    # check
    if error:
        assert request_err
    else:
        assert pay_data
        assert pay_data['invoiceId']
        assert pay_data['receipt']


@pytest.mark.parametrize('desc,selection,pay_url,details,error', TEST_PAYMENT_MOCK)
def test_payment_search_mock(session, client, jwt, desc, selection, pay_url, details, error):
    """Assert that a pay-api search payment request works as expected with the mock service endpoint."""
    # setup
    token = helper_create_jwt(jwt, [MHR_ROLE])
    payment = Payment(jwt=token, account_id='PS12345', details=details)
    payment.api_url = pay_url

    # test
    if error:
        with pytest.raises(SBCPaymentException) as request_err:
            pay_data = payment.create_payment_search(selection, '200000001', 'UT-PAY-SEARCH-01', False)
    else:
        pay_data = payment.create_payment_search(selection, '200000001', 'UT-PAY-SEARCH-01', False)

    # print(pay_data)
    # check
    if error:
        assert request_err
    else:
        assert pay_data
        assert pay_data['invoiceId']
        assert pay_data['receipt']


def test_payment_apikey(session, client, jwt):
    """Assert that a gateway pay-api payment request works as expected."""
    # setup
    apikey = os.getenv('PAYMENT_GATEWAY_APIKEY_TEST')
    if apikey:
        token = helper_create_jwt(jwt, [MHR_ROLE])
        payment = Payment(jwt=token, account_id='PS12345', api_key=apikey)
        payment.api_url = MOCK_URL

        # test
        pay_data = payment.create_payment_search(SELECT_MHR_ONLY, '200000001', 'UT-PAY-SEARCH-01', False)
        # print(pay_data)
        # check
        assert pay_data
        assert pay_data['invoiceId']
        assert pay_data['receipt']


def test_sa_get_token(session, client, jwt):
    """Assert that an OIDC get token request with valid SA credentials works as expected."""
    # setup
    token = helper_create_jwt(jwt, [MHR_ROLE])
    pay_client = SBCPaymentClient(jwt=token, account_id='PS12345')

    # test
    jwt = pay_client.get_sa_token()

    # check
    assert jwt
    assert len(jwt) > 0