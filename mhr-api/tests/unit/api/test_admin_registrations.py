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

"""Tests to verify the endpoints for maintaining MH staff admin registrations.

Test-Suite to ensure that the /admin-registrations endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app

from mhr_api.models import MhrRegistrationReport, MhrDocument, MhrRegistration, utils as model_utils
from mhr_api.models.type_tables import MhrDocumentTypes, MhrRegistrationStatusTypes
from mhr_api.resources.v1.admin_registrations import get_transaction_type
from mhr_api.services.authz import BCOL_HELP_ROLE, MHR_ROLE, STAFF_ROLE, COLIN_ROLE, TRANSFER_DEATH_JT, \
                                   TRANSFER_SALE_BENEFICIARY, REQUEST_TRANSPORT_PERMIT
from mhr_api.services.payment import TransactionTypes
from tests.unit.services.utils import create_header, create_header_account


ADMIN_REGISTRATION = {
  'clientReferenceId': 'EX-TP001234',
  'attentionReference': 'JOHN SMITH',
  'documentType': 'NRED',
  'documentId': '62133670',
  'submittingParty': {
    'businessName': 'BOB PATERSON HOMES INC.',
    'address': {
      'street': '1200 S. MACKENZIE AVE.',
      'city': 'WILLIAMS LAKE',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V2G 3Y1'
    },
    'phoneNumber': '6044620279'
  },
  'note': {
    'documentType': 'NRED',
    'documentId': '62133670',
    'remarks': 'REMARKS',
    'givingNoticeParty': {
      'personName': {
        'first': 'JOHNNY',
        'middle': 'B',
        'last': 'SMITH'
      },
      'address': {
        'street': '222 SUMMER STREET',
        'city': 'VICTORIA',
        'region': 'BC',
        'country': 'CA',
        'postalCode': 'V8W 2V8'
      },
      'phoneNumber': '2504930122'
    }
  }
}
STAT_REGISTRATION = {
  'clientReferenceId': 'EX-TP001234',
  'attentionReference': 'JOHN SMITH',
  'documentType': 'STAT',
  'documentId': '80058756',
  'submittingParty': {
    'businessName': 'BOB PATERSON HOMES INC.',
    'address': {
      'street': '1200 S. MACKENZIE AVE.',
      'city': 'WILLIAMS LAKE',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V2G 3Y1'
    },
    'phoneNumber': '6044620279'
  },
  'location': {
    'locationType': 'MH_PARK',
    'address': {
      'street': '1117 GLENDALE AVENUE',
      'city': 'SALMO',
      'region': 'BC',
      'country': 'CA',
      'postalCode': ''
    },
    'leaveProvince': False,
    'parkName': 'GLENDALE TRAILER PARK',
    'pad': '2',
    'taxCertificate': True,
    'taxExpiryDate': '2035-01-31T08:00:00+00:00'
  }
}
REGC_PUBA_REGISTRATION = {
  'clientReferenceId': 'EX-TP001234',
  'attentionReference': 'JOHN SMITH',
  'documentType': 'REGC_STAFF',
  'documentId': '80058756',
  'submittingParty': {
    'businessName': 'BOB PATERSON HOMES INC.',
    'address': {
      'street': '1200 S. MACKENZIE AVE.',
      'city': 'WILLIAMS LAKE',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V2G 3Y1'
    },
    'phoneNumber': '6044620279'
  },
  'location': {
    'locationType': 'MH_PARK',
    'address': {
      'street': '1117 GLENDALE AVENUE',
      'city': 'SALMO',
      'region': 'BC',
      'country': 'CA',
      'postalCode': ''
    },
    'leaveProvince': False,
    'parkName': 'GLENDALE TRAILER PARK',
    'pad': '2',
    'taxCertificate': True,
    'taxExpiryDate': '2035-01-31T08:00:00+00:00'
  },
  'note': {
    'documentType': 'REGC_STAFF',
    'documentId': '80058756',
    'remarks': 'REMARKS'
  }
}
LOCATION_VALID = {
    'locationType': 'MH_PARK',
    'address': {
      'street': '1117 GLENDALE AVENUE',
      'city': 'SALMO',
      'region': 'BC',
      'country': 'CA',
      'postalCode': ''
    },
    'leaveProvince': False,
    'parkName': 'GLENDALE TRAILER PARK',
    'pad': '2',
    'taxCertificate': True,
    'taxExpiryDate': '2035-01-31T08:00:00+00:00'
}
LOCATION_PARK_MINIMAL= {
    'locationType': 'MH_PARK',
    'address': {
      'city': 'SALMO',
      'region': 'BC',
      'country': 'CA'
    },
    'leaveProvince': False,
    'parkName': 'GLENDALE TRAILER PARK',
    'pad': '2',
    'taxCertificate': True,
    'taxExpiryDate': '2035-01-31T08:00:00+00:00'
}
DESCRIPTION_VALID = {
  'manufacturer': 'STARLINE',
  'baseInformation': {
    'year': 2018,
    'make': 'WATSON IND. (ALTA)',
    'model': 'DUCHESS'
  },
  'sectionCount': 2,
  'sections': [
    {
      'serialNumber': '52D70556-A',
      'lengthFeet': 52,
      'lengthInches': 0,
      'widthFeet': 12,
      'widthInches': 0
    },
    {
      'serialNumber': '52D70556-B',
      'lengthFeet': 52,
      'lengthInches': 0,
      'widthFeet': 12,
      'widthInches': 0
    }
  ],
  'csaNumber': '786356',
  'csaStandard': 'Z240',
  'engineerDate': '2024-10-22T07:59:00+00:00',
  'engineerName': ' Dave Smith ENG. LTD.'
}
ADD_OG_VALID = [
    {
      'groupId': 2,
      'owners': [
        {
          'individualName': {
            'first': 'James',
            'last': 'Smith'
          },
          'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
          },
          'phoneNumber': '6041234567',
          'ownerId': 2
        }
      ],
      'type': 'SOLE'
    }
]
DELETE_OG_VALID = [
    {
        'groupId': 1,
        'owners': [
        {
            'individualName': {
            'first': 'Jane',
            'last': 'Smith'
            },
            'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': ' ',
            'country': 'CA'
            },
            'phoneNumber': '6041234567',
            'ownerId': 1
        }
        ],
        'type': 'SOLE'
    }
]
DELETE_OG_EXRE = [
    {
        'groupId': 1,
        'owners': [
        {
            'organizationName': 'TEST EXNR ACTIVE',
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': ' ',
                'country': 'CA'
            },
            'ownerId': 1
        }
        ],
        'type': 'SOLE'
    }
]
MOCK_AUTH_URL = 'https://test.api.connect.gov.bc.ca/mockTarget/auth/api/v1/'
MOCK_PAY_URL = 'https://test.api.connect.gov.bc.ca/mockTarget/pay/api/v1/'
QUALIFIED_USER_ROLES = [MHR_ROLE,TRANSFER_SALE_BENEFICIARY,TRANSFER_DEATH_JT,REQUEST_TRANSPORT_PERMIT]

# testdata pattern is ({description}, {mhr_num}, {roles}, {status}, {account})
TEST_CREATE_DATA = [
    ('Invalid schema validation missing submitting', '000900', [MHR_ROLE, STAFF_ROLE],
     HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Staff missing account', '000900', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, None),
    ('Invalid role product', '000900', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Invalid BCOL helpdesk role', '000900', [MHR_ROLE, BCOL_HELP_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Invalid non-staff role', '000900', [MHR_ROLE, TRANSFER_DEATH_JT], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Valid staff NCAN', '000915', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'PS12345'),
    ('Invalid mhr num', '300655', [MHR_ROLE, STAFF_ROLE], HTTPStatus.NOT_FOUND, 'PS12345'),
    ('Invalid exempt', '000912', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Invalid historical', '000913', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Invalid missing note party', '000900', [MHR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Valid staff NRED', '000914', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'PS12345'),
    ('Valid staff STAT', '000931', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'PS12345'),
    ('Valid staff location minimal', '000931', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'PS12345'),
    ('Valid staff CANCEL_PERMIT', '000931', [MHR_ROLE, STAFF_ROLE], HTTPStatus.CREATED, 'PS12345'),
    ('Valid QS CANCEL_PERMIT', '000931', QUALIFIED_USER_ROLES, HTTPStatus.CREATED, 'PS12345')
  ]
# testdata pattern is ({description}, {mhr_num}, {account}, {doc_type}, {mh_status}, {region}, {ownland})
TEST_AMEND_CORRECT_STATUS_DATA = [
    ('Valid correct ACTIVE AB', '000912', 'PS12345', 'REGC_STAFF', MhrRegistrationStatusTypes.ACTIVE.value, 'AB',
     False),
    ('Valid correct client ACTIVE', '000912', 'PS12345', 'REGC_CLIENT', MhrRegistrationStatusTypes.ACTIVE.value, 
     None, True),
    ('Valid amend ACTIVE AB', '000912', 'PS12345', 'PUBA', MhrRegistrationStatusTypes.ACTIVE.value, 'AB', False),
    ('Valid correct EXEMPT', '000931', 'PS12345', 'REGC_CLIENT', MhrRegistrationStatusTypes.EXEMPT.value, 'BC', True),
    ('Valid amend EXEMPT', '000931', 'PS12345', 'PUBA', MhrRegistrationStatusTypes.EXEMPT.value, 'AB', True)
]
# testdata pattern is ({doc_type}, {pay_trans_type})
TEST_TRANS_TYPE_DATA = [
    (MhrDocumentTypes.EXRE, TransactionTypes.REGISTRATION.value),
    (MhrDocumentTypes.NRED, TransactionTypes.UNIT_NOTE.value),
    (MhrDocumentTypes.NCAN, TransactionTypes.UNIT_NOTE.value),
    (MhrDocumentTypes.STAT, TransactionTypes.ADMIN_RLCHG.value),
    (MhrDocumentTypes.REGC_CLIENT, TransactionTypes.CORRECTION.value),
    (MhrDocumentTypes.REGC_STAFF, TransactionTypes.CORRECTION.value),
    (MhrDocumentTypes.PUBA, TransactionTypes.AMENDMENT.value),
    (MhrDocumentTypes.CANCEL_PERMIT, TransactionTypes.CANCEL_PERMIT.value)
]
# testdata pattern is ({mhr_num}, {account_id}, {has_loc}, {has_desc}, {has_owners})
TEST_CREATE_DATA_EXRE= [
    ('000928', 'PS12345', False, True, False),
    ('000928', 'PS12345', False, False, True),
    ('000928', 'PS12345', True, True, True),
    ('000928', 'PS12345', True, False, False)
]
# testdata pattern is ({mhr_num}, {account_id}, {has_loc}, {has_desc}, {has_owners}, {doc_type})
TEST_CREATE_DATA_REGC_PUBA= [
    ('000931', 'PS12345', True, True, True, 'REGC_STAFF'),
    ('000931', 'PS12345', False, True, False, 'REGC_CLIENT'),
    ('000931', 'PS12345', False, False, True, 'REGC_CLIENT'),
    ('000931', 'PS12345', True, False, False, 'REGC_STAFF'),
    ('000931', 'PS12345', False, True, False, 'PUBA'),
    ('000919', 'PS12345', False, False, True, 'PUBA'),
    ('000931', 'PS12345', True, False, False, 'PUBA')
]


@pytest.mark.parametrize('mhr_num,account,has_loc,has_desc,has_owners,doc_type', TEST_CREATE_DATA_REGC_PUBA)
def test_create_regc_puba(session, client, jwt, mhr_num, account, has_loc, has_desc, has_owners, doc_type):
    """Assert that a post MH REGC_STAFF/REGC_CLIENT/PUBA registration works as expected."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    json_data = copy.deepcopy(REGC_PUBA_REGISTRATION)
    json_data['mhrNumber'] = mhr_num
    json_data['documentType'] = doc_type
    json_data['documentId'] = '80058756'
    del json_data['note']
    if not has_loc:
        del json_data['location']
    if has_desc:
        json_data['description'] = DESCRIPTION_VALID
    if has_owners:
        json_data['addOwnerGroups'] = ADD_OG_VALID
        json_data['deleteOwnerGroups'] = DELETE_OG_VALID

    headers = create_header_account(jwt, [MHR_ROLE, STAFF_ROLE], 'UT-TEST', account)
    # test
    response = client.post('/api/v1/admin-registrations/' + mhr_num,
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    # current_app.logger.debug(response.json)
    assert response.status_code == HTTPStatus.CREATED
    reg_json = response.json
    assert reg_json.get('documentId')
    assert reg_json.get('mhrNumber')
    assert reg_json.get('createDateTime')
    assert reg_json.get('registrationType')
    assert reg_json.get('clientReferenceId')
    assert reg_json.get('submittingParty')
    assert reg_json.get('documentType') == doc_type
    assert reg_json.get('status')
    doc: MhrDocument = MhrDocument.find_by_document_id(reg_json.get('documentId'))
    assert doc
    reg_report: MhrRegistrationReport = MhrRegistrationReport.find_by_registration_id(doc.registration_id)
    assert reg_report
    assert reg_report.report_data
    report_json = reg_report.report_data
    assert report_json.get('status')
    if has_loc:
        assert reg_json.get('location')
        assert report_json.get('location')
    else:
        assert not reg_json.get('location')
        assert not report_json.get('location')
    if has_desc:
        assert reg_json.get('description')
        assert report_json.get('description')
    else:
        assert not reg_json.get('description')
        assert not report_json.get('description')
    if has_owners:
        assert reg_json.get('addOwnerGroups')
        assert reg_json.get('deleteOwnerGroups')
        assert len(reg_json.get('addOwnerGroups')) == 1
        assert report_json.get('ownerGroups')
        assert len(report_json.get('ownerGroups')) == 1
    else:
        assert not reg_json.get('addOwnerGroups')
        assert not reg_json.get('deleteOwnerGroups')
        assert not report_json.get('ownerGroups')


@pytest.mark.parametrize('mhr_num,account,has_loc,has_desc,has_owners', TEST_CREATE_DATA_EXRE)
def test_create_exre(session, client, jwt, mhr_num, account, has_loc, has_desc, has_owners):
    """Assert that a post MH EXRE registration works as expected."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    json_data = copy.deepcopy(REGC_PUBA_REGISTRATION)
    json_data['mhrNumber'] = mhr_num
    json_data['documentType'] = MhrDocumentTypes.EXRE
    json_data['documentId'] = '80058756'
    del json_data['note']
    if not has_loc:
        del json_data['location']
    if has_desc:
        json_data['description'] = DESCRIPTION_VALID
    if has_owners:
        json_data['addOwnerGroups'] = ADD_OG_VALID
        json_data['deleteOwnerGroups'] = DELETE_OG_EXRE

    headers = create_header_account(jwt, [MHR_ROLE, STAFF_ROLE], 'UT-TEST', account)
    # test
    response = client.post('/api/v1/admin-registrations/' + mhr_num,
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    # current_app.logger.debug(response.json)
    assert response.status_code == HTTPStatus.CREATED
    reg_json = response.json
    assert reg_json.get('documentId')
    assert reg_json.get('mhrNumber')
    assert reg_json.get('createDateTime')
    assert reg_json.get('registrationType')
    assert reg_json.get('clientReferenceId')
    assert reg_json.get('submittingParty')
    assert reg_json.get('documentType') == MhrDocumentTypes.EXRE
    assert reg_json.get('status') == MhrRegistrationStatusTypes.ACTIVE
    if has_loc:
        assert reg_json.get('location')
    else:
        assert not reg_json.get('location')
    if has_desc:
        assert reg_json.get('description')
    else:
        assert not reg_json.get('description')
    if has_owners:
        assert reg_json.get('addOwnerGroups')
        assert reg_json.get('deleteOwnerGroups')
        assert len(reg_json.get('addOwnerGroups')) == 1
    else:
        assert not reg_json.get('addOwnerGroups')
        assert not reg_json.get('deleteOwnerGroups')
    doc: MhrDocument = MhrDocument.find_by_document_id(reg_json.get('documentId'))
    assert doc
    reg_report: MhrRegistrationReport = MhrRegistrationReport.find_by_registration_id(doc.registration_id)
    assert reg_report
    assert reg_report.report_data
    report_json = reg_report.report_data
    assert report_json.get('status') == MhrRegistrationStatusTypes.ACTIVE
    assert report_json.get('location')
    assert report_json.get('description')
    assert report_json.get('ownerGroups')
    assert len(report_json.get('ownerGroups')) == 1


@pytest.mark.parametrize('desc,mhr_num,roles,status,account', TEST_CREATE_DATA)
def test_create(session, client, jwt, desc, mhr_num, roles, status, account):
    """Assert that a post MH registration works as expected."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    json_data = copy.deepcopy(ADMIN_REGISTRATION)
    if desc == 'Valid staff STAT':
        json_data = copy.deepcopy(STAT_REGISTRATION)
        json_data['mhrNumber'] = mhr_num
    elif desc == 'Valid staff location minimal':
        json_data = copy.deepcopy(REGC_PUBA_REGISTRATION)
        json_data['mhrNumber'] = mhr_num
        json_data['location'] = copy.deepcopy(LOCATION_PARK_MINIMAL)
        json_data['documentType'] = MhrDocumentTypes.REGC_STAFF
        del json_data['note']
    elif desc in ('Valid staff CANCEL_PERMIT', 'Valid QS CANCEL_PERMIT'):
        json_data['mhrNumber'] = mhr_num
        json_data['documentType'] = MhrDocumentTypes.CANCEL_PERMIT
        if json_data.get('location'):
          del json_data['location']
    else:
        json_data['mhrNumber'] = mhr_num
        json_data['documentType'] = MhrDocumentTypes.NRED
        json_data['note']['documentType'] = MhrDocumentTypes.NRED
    if desc == 'Invalid schema validation missing submitting':
        del json_data['submittingParty']
    elif desc == 'Invalid missing note party':
        del json_data['note']['givingNoticeParty']
    elif status == HTTPStatus.CREATED:
        json_data['documentId'] = '80058756'
        if json_data.get('note'):
            json_data['note']['documentId'] = '80058756'
    if mhr_num == '000914':
        json_data['updateDocumentId'] = 'UT000020'
    elif mhr_num == '000915':
        json_data['updateDocumentId'] = 'UT000022'
        json_data['documentType'] = MhrDocumentTypes.NCAN
        json_data['note']['documentType'] = MhrDocumentTypes.NCAN
    if account:
        headers = create_header_account(jwt, roles, 'UT-TEST', account)
    else:
        headers = create_header(jwt, roles)
    # test
    response = client.post('/api/v1/admin-registrations/' + mhr_num,
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    # current_app.logger.debug(response.json)
    assert response.status_code == status
    if response.status_code == HTTPStatus.CREATED:
        reg_json = response.json
        doc_id = reg_json.get('documentId')
        if not doc_id:
            doc_id = reg_json['note']['documentId']
        doc: MhrDocument = MhrDocument.find_by_document_id(doc_id)
        assert doc
        assert reg_json.get('mhrNumber')
        assert reg_json.get('createDateTime')
        assert reg_json.get('registrationType')
        assert reg_json.get('clientReferenceId')
        assert reg_json.get('submittingParty')
        if desc not in ('Valid staff STAT', 'Valid staff CANCEL_PERMIT', 'Valid QS CANCEL_PERMIT') and \
              json_data.get('documentType') not in (MhrDocumentTypes.REGC_STAFF,
                                                    MhrDocumentTypes.REGC_CLIENT,
                                                    MhrDocumentTypes.PUBA, MhrDocumentTypes.EXRE):
            assert reg_json.get('note')
            note_json = reg_json.get('note')
            assert note_json.get('documentType')
            assert note_json.get('documentId')
            assert note_json.get('createDateTime')
            assert note_json.get('remarks') is not None
            if note_json.get('documentType') in (MhrDocumentTypes.CAU, MhrDocumentTypes.CAUC,
                                                 MhrDocumentTypes.CAUE, MhrDocumentTypes.REG_102, MhrDocumentTypes.NPUB,
                                                 MhrDocumentTypes.NCON, MhrDocumentTypes.TAXN):
                assert note_json.get('givingNoticeParty')
                notice_json = note_json.get('givingNoticeParty')
                assert notice_json.get('personName')
                assert notice_json['personName'].get('first')
                assert notice_json['personName'].get('last')
                assert notice_json.get('phoneNumber')
                assert notice_json.get('address')
                assert notice_json['address']['street']
                assert notice_json['address']['city']
                assert notice_json['address']['region']
                assert notice_json['address']['country']
                assert notice_json['address']['postalCode'] is not None
            else:
                assert 'givingNoticeParty' not in note_json
            assert reg_json.get('documentType')
            assert reg_json.get('documentDescription')
        if json_data['documentType'] == MhrDocumentTypes.CANCEL_PERMIT:
            assert reg_json.get('location')
            assert reg_json.get('previousLocation')
            assert reg_json.get('note')
            assert reg_json['note'].get('cancelledDocumentRegistrationNumber')
            assert reg_json['note'].get('cancelledDateTime')
        elif json_data['documentType'] in (MhrDocumentTypes.STAT,
                                           MhrDocumentTypes.PUBA,
                                           MhrDocumentTypes.EXRE,
                                           MhrDocumentTypes.REGC_STAFF,
                                           MhrDocumentTypes.REGC_CLIENT):
            if json_data.get('location'):
                assert reg_json.get('location')
            else:
                assert not reg_json.get('location')
            if json_data.get('description'):
                assert reg_json.get('description')
            else:
                assert not reg_json.get('description')
            if json_data.get('addOwnerGroups'):
                assert reg_json.get('addOwnerGroups')
                assert reg_json.get('deleteOwnerGroups')
            else:
                assert not reg_json.get('addOwnerGroups')
                assert not reg_json.get('deleteOwnerGroups')
            if doc:
                assert doc.document_type == json_data['documentType']
                reg_report: MhrRegistrationReport = MhrRegistrationReport.find_by_registration_id(doc.registration_id)
                assert reg_report
                assert reg_report.batch_registration_data
        if json_data['documentType'] == MhrDocumentTypes.EXRE:
            assert reg_json.get('status') == MhrRegistrationStatusTypes.ACTIVE


@pytest.mark.parametrize('desc,mhr_num,account,doc_type,mh_status,region,ownland', TEST_AMEND_CORRECT_STATUS_DATA)
def test_amend_correct_status(session, client, jwt, desc, mhr_num, account, doc_type, mh_status, region, ownland):
    """Assert that a post MH amendment/correction status change registration works as expected."""
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = create_header_account(jwt, [MHR_ROLE, STAFF_ROLE], 'UT-TEST', account)
    json_data = copy.deepcopy(REGC_PUBA_REGISTRATION)
    json_data['mhrNumber'] = mhr_num
    json_data['documentType'] = doc_type
    json_data['status'] = mh_status
    json_data['ownLand'] = ownland
    del json_data['note']
    if not region:
          del json_data['location']
    else:
          json_data['location']['address']['region'] = region
    # test
    response = client.post('/api/v1/admin-registrations/' + mhr_num,
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    # current_app.logger.debug(response.json)
    assert response.status_code == HTTPStatus.CREATED
    reg_json = response.json
    assert reg_json.get('documentType') == doc_type
    assert reg_json.get('status') == mh_status
    doc_id = reg_json.get('documentId')
    doc: MhrDocument = MhrDocument.find_by_document_id(doc_id)
    assert doc.document_type == json_data['documentType']
    reg_report: MhrRegistrationReport = MhrRegistrationReport.find_by_registration_id(doc.registration_id)
    assert reg_report
    assert reg_report.batch_registration_data
    registration: MhrRegistration = MhrRegistration.find_all_by_mhr_number(response.json['mhrNumber'], account)
    assert registration
    registration.current_view = True
    curr_json = registration.new_registration_json
    assert curr_json['ownLand'] == json_data['ownLand'] 


@pytest.mark.parametrize('doc_type,pay_trans_type', TEST_TRANS_TYPE_DATA)
def test_transaction_type(session, client, jwt, doc_type, pay_trans_type):
    """Assert that mapping document type to payment transaction type works as expected."""
    json_data = {
        'documentType': doc_type
    }
    trans_type: str = get_transaction_type(json_data)
    assert trans_type == pay_trans_type
