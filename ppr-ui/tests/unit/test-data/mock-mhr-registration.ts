import {
  ActionTypes,
  ApiHomeTenancyTypes,
  APIMhrTypes,
  APIRegistrationTypes,
  HomeCertificationOptions,
  HomeLocationTypes,
  HomeOwnerPartyTypes,
  HomeTenancyTypes,
  MhApiStatusTypes
} from '@/enums'
import type {
  AddressIF,
  MhrRegistrationFractionalOwnershipIF,
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnerIF,
  MhrRegistrationIF
} from '@/interfaces'

export const mockedAddress: AddressIF = {
  street: '1234 Fort St.',
  streetAdditional: '2nd floor',
  city: 'Victoria',
  region: 'BC',
  country: 'CA',
  postalCode: 'V8R1L2',
  deliveryInstructions: 'Back Door'
}

export const mockedAddressAlt: AddressIF = {
  street: '1234 Fort St.',
  streetAdditional: '3rd floor',
  city: 'Nanaimo',
  region: 'BC',
  country: 'CA',
  postalCode: 'V6L4K4',
  deliveryInstructions: 'Front Door'
}

export const mockedAddressOutsideBC: AddressIF = {
  city: 'TORONTO',
  country: 'CA',
  postalCode: 'M5E1E5',
  region: 'ON',
  street: '1 YONGE ST, SUITE 100'
}

export const mockedEmptyGroup: MhrRegistrationHomeOwnerGroupIF = {
  groupId: 100,
  owners: [],
  // TODO: Mhr-Submission - UPDATE after the correct type can be determined
  type: Object.keys(HomeTenancyTypes).find(key => HomeTenancyTypes[key] as string === HomeTenancyTypes.SOLE)
}

export const mockedExecutor: MhrRegistrationHomeOwnerIF = {
  ownerId: 10,
  individualName: {
    first: 'John',
    middle: 'A',
    last: 'Smith'
  },
  description: 'Executor of the will of John Smith',
  phoneNumber: '(545) 333-2211',
  phoneExtension: '1234',
  partyType: HomeOwnerPartyTypes.EXECUTOR,
  address: mockedAddress
}

export const mockedOwner: MhrRegistrationHomeOwnerIF = {
  ownerId: 45,
  individualName: {
    first: 'Owner',
    middle: 'A',
    last: 'Smith'
  },
  suffix: 'I am an owner!',
  phoneNumber: '(123) 777-2211',
  phoneExtension: '1234',
  partyType: HomeOwnerPartyTypes.OWNER_IND,
  address: mockedAddress
}

export const mockedAddedExecutor: MhrRegistrationHomeOwnerIF = {
  ownerId: 20,
  individualName: {
    first: 'John',
    middle: 'A',
    last: 'Smith'
  },
  description: 'Sr.',
  phoneNumber: '(545) 333-2211',
  phoneExtension: '1234',
  partyType: HomeOwnerPartyTypes.EXECUTOR,
  action: ActionTypes.ADDED,
  address: mockedAddress
}

export const mockedRemovedExecutor: MhrRegistrationHomeOwnerIF = {
  ownerId: 27,
  individualName: {
    first: 'Roy',
    middle: 'B',
    last: 'Harper'
  },
  description: 'Sr.',
  phoneNumber: '(676) 888-4455',
  phoneExtension: '4321',
  partyType: HomeOwnerPartyTypes.EXECUTOR,
  action: ActionTypes.REMOVED,
  address: mockedAddress
}

export const mockedAdministrator: MhrRegistrationHomeOwnerIF = {
  ownerId: 35,
  individualName: {
    first: 'Admin',
    middle: 'M',
    last: 'Smith'
  },
  description: 'ADMINISTRATOR 123',
  phoneNumber: '(123) 777-6666',
  phoneExtension: '7656',
  partyType: HomeOwnerPartyTypes.ADMINISTRATOR,
  address: mockedAddress
}

export const mockedAddedAdministrator: MhrRegistrationHomeOwnerIF = {
  ownerId: 30,
  individualName: {
    first: 'John',
    middle: 'A',
    last: 'Smith'
  },
  description: 'Sr.',
  phoneNumber: '(545) 333-2211',
  phoneExtension: '1234',
  partyType: HomeOwnerPartyTypes.ADMINISTRATOR,
  action: ActionTypes.ADDED,
  address: mockedAddress
}

export const mockedRemovedAdministrator: MhrRegistrationHomeOwnerIF = {
  ownerId: 37,
  individualName: {
    first: 'John',
    middle: 'A',
    last: 'Smith'
  },
  description: 'Sr.',
  phoneNumber: '(545) 333-2211',
  phoneExtension: '1234',
  partyType: HomeOwnerPartyTypes.ADMINISTRATOR,
  action: ActionTypes.REMOVED,
  address: mockedAddress
}

export const mockedPerson: MhrRegistrationHomeOwnerIF = {
  ownerId: 10,
  groupId: 1,
  individualName: {
    first: 'John',
    middle: 'A',
    last: 'Smith'
  },
  suffix: 'Sr.',
  phoneNumber: '(545) 333-2211',
  phoneExtension: '1234',
  partyType: HomeOwnerPartyTypes.OWNER_IND,
  address: mockedAddress
}

export const mockedPerson2: MhrRegistrationHomeOwnerIF = {
  ownerId: 11,
  individualName: {
    first: 'John',
    middle: 'A',
    last: 'Smith'
  },
  suffix: 'Sr.',
  phoneNumber: '(545) 333-2211',
  phoneExtension: '1234',
  partyType: HomeOwnerPartyTypes.OWNER_IND,
  address: mockedAddress
}

export const mockedAddedPerson: MhrRegistrationHomeOwnerIF = {
  ownerId: 10,
  individualName: {
    first: 'John',
    middle: 'A',
    last: 'Smith'
  },
  suffix: 'Sr.',
  phoneNumber: '(545) 333-2211',
  phoneExtension: '1234',
  partyType: HomeOwnerPartyTypes.OWNER_IND,
  address: mockedAddress,
  action: ActionTypes.ADDED
}

export const mockedRemovedPerson: MhrRegistrationHomeOwnerIF = {
  ownerId: 10,
  individualName: {
    first: 'John',
    middle: 'A',
    last: 'Smith'
  },
  suffix: 'Sr.',
  phoneNumber: '(545) 333-2211',
  phoneExtension: '1234',
  address: mockedAddress,
  partyType: HomeOwnerPartyTypes.OWNER_IND,
  action: ActionTypes.REMOVED
}

export const mockedOrganization: MhrRegistrationHomeOwnerIF = {
  ownerId: 20,
  groupId: 1,
  organizationName: 'Smart Track',
  suffix: 'Inc.',
  phoneNumber: '(999) 888-7766',
  phoneExtension: '4321',
  partyType: HomeOwnerPartyTypes.OWNER_BUS,
  address: mockedAddressAlt
}

export const mockedAddedOrganization: MhrRegistrationHomeOwnerIF = {
  ownerId: 20,
  organizationName: 'Smart Track',
  suffix: 'Inc.',
  phoneNumber: '(999) 888-7766',
  phoneExtension: '4321',
  partyType: HomeOwnerPartyTypes.OWNER_BUS,
  address: mockedAddressAlt,
  action: ActionTypes.ADDED
}

export const mockedRemovedOrganization: MhrRegistrationHomeOwnerIF = {
  ownerId: 20,
  organizationName: 'Smart Track',
  suffix: 'Inc.',
  phoneNumber: '(999) 888-7766',
  phoneExtension: '4321',
  partyType: HomeOwnerPartyTypes.OWNER_BUS,
  address: mockedAddressAlt,
  action: ActionTypes.REMOVED
}

export const mockedFractionalOwnership: MhrRegistrationFractionalOwnershipIF = {
  interest: 'Undivided',
  interestNumerator: 1,
  interestDenominator: 4
}

export const mockedMhrRegistration: MhrRegistrationIF = {
  attentionReference: '',
  clientReferenceId: '',
  draftNumber: '',
  declaredValue: '123',
  isManualLocationInfo: false,
  description: {
    baseInformation: {
      circa: false,
      make: 'make',
      model: 'model',
      year: 2002
    },
    csaNumber: 'asd',
    csaStandard: 'A277',
    certificationOption: HomeCertificationOptions.CSA, // does not come from API
    hasNoCertification: false, // does not come from API
    engineerName: '',
    engineerDate: '',
    manufacturer: 'adsasd',
    otherRemarks: '',
    rebuiltRemarks: '',
    sectionCount: 1,
    sections: [
      {
        lengthFeet: 12,
        lengthInches: 0,
        serialNumber: '123',
        widthFeet: 12,
        widthInches: 0
      }
    ]
  },
  documentId: '83000323',
  location: {
    address: {
      city: 'NORTH YORK',
      country: 'CA',
      postalCode: 'M6B 1W8',
      region: 'ON',
      street: '123-160 TYCOS DR',
      streetAdditional: ''
    },
    dealerName: 'adasdasd',
    leaveProvince: false,
    locationType: HomeLocationTypes.LOT,
    taxCertificate: false
  },
  ownLand: false,
  ownerGroups: [
    {
      groupId: 4,
      interest: 'UNDIVIDED',
      interestDenominator: 3,
      interestNumerator: 1,
      owners: [
        {
          address: {
            city: 'NORTH SAANICH',
            country: 'CA',
            postalCode: 'V8L 5V4',
            region: 'BC',
            street: '123-1640 ELECTRA BLVD'
          },
          individualName: {
            first: 'MockFirstName',
            middle: 'mockMiddleName',
            last: 'MockLastName'
          },
          ownerId: 1,
          partyType: HomeOwnerPartyTypes.OWNER_IND,
          phoneNumber: '1250516825',
          type: ApiHomeTenancyTypes.COMMON
        }
      ],
      tenancySpecified: true,
      type: ApiHomeTenancyTypes.COMMON
    },
    {
      groupId: 5,
      interest: 'UNDIVIDED',
      interestDenominator: 3,
      interestNumerator: 1,
      owners: [
        {
          address: {
            city: 'NORTH SAANICH',
            country: 'CA',
            postalCode: 'V8L 5V4',
            region: 'BC',
            street: '123-1640 ELECTRA BLVD'
          },
          individualName: {
            first: 'MockFirstName',
            middle: 'mockMiddleName',
            last: 'MockLastName'
          },
          ownerId: 1,
          partyType: HomeOwnerPartyTypes.OWNER_IND,
          phoneNumber: '1250516825',
          type: ApiHomeTenancyTypes.JOINT
        },
        {
          address: {
            city: 'NORTH SAANICH',
            country: 'CA',
            postalCode: 'V8L 5V4',
            region: 'BC',
            street: '123-1640 ELECTRA BLVD'
          },
          individualName: {
            first: 'MockFirstName',
            middle: 'mockMiddleName',
            last: 'MockLastName'
          },
          ownerId: 1,
          partyType: HomeOwnerPartyTypes.OWNER_IND,
          phoneNumber: '1250516825',
          type: ApiHomeTenancyTypes.JOINT
        }
      ],
      tenancySpecified: true,
      type: ApiHomeTenancyTypes.COMMON
    },
  ],
  registrationType: APIRegistrationTypes.MANUFACTURED_HOME_REGISTRATION,
  submittingParty: {
    address: {
      city: 'LANGLEY',
      country: 'CA',
      postalCode: 'V2Z 3C1',
      region: 'BC',
      street: '#200 - 4769 - 222ND STREET'
    },
    emailAddress: '',
    phoneNumber: '',
    businessName: 'CAMPBELL, BURTON & MCMULLAN, LLP'
  }
}

export const mockMhrReRegistration = {
  ownerNames: '',
  path: '',
  username: '',
  documentId: '',
  draftNumber: '',
  registrationDescription: '',
  submittingParty: null,
  attentionReference: '',
  isManualLocationInfo: false,
  clientReferenceId: '',
  createDateTime: '2024-04-04T21:49:12+00:00',
  declaredValue: '120000',
  description: {
    baseInformation: {
      circa: false,
      make: 'asdasd',
      model: 'asdasd',
      year: 2002
    },
    csaNumber: 'asdasd',
    csaStandard: 'A277',
    engineerName: '',
    engineerDate: '',
    manufacturer: 'MODULINE INDUSTRIES',
    otherRemarks: 'asdasd',
    rebuiltRemarks: 'asdasd',
    sectionCount: 1,
    sections: [
      {
        lengthFeet: 1,
        lengthInches: 0,
        serialNumber: '123123',
        widthFeet: 1,
        widthInches: 0
      }
    ]
  },
  location: {
    address: {
      city: 'FORT ST. JOHN',
      country: 'CA',
      postalCode: '',
      region: 'BC',
      street: '8312 GALLAGHER LK FRONTAGE RD'
    },
    landDistrict: 'PEACE RIVER',
    leaveProvince: false,
    locationType: HomeLocationTypes.OTHER_LAND,
    lot: '1224',
    permitWithinSamePark: false,
    plan: '12',
    taxCertificate: false
  },
  mhrNumber: '108000',
  ownLand: true,
  ownerGroups: [],
  permitDateTime: '2024-05-21T22:19:11+00:00',
  permitExpiryDateTime: '2024-06-21T06:59:59+00:00',
  permitLandStatusConfirmation: true,
  permitRegistrationNumber: '00550790',
  permitStatus: MhApiStatusTypes.ACTIVE,
  previousLocation: {
    address: {
      city: 'NORTH SAANICH',
      country: 'CA',
      postalCode: 'V8L 5V4',
      region: 'BC',
      street: '123-1640 ELECTRA BLVD'
    },
    dealerName: 'asdasd',
    leaveProvince: false,
    locationId: 200876,
    locationType: 'MANUFACTURER',
    status: 'HISTORICAL',
    taxCertificate: false
  },
  registrationType: APIMhrTypes.MANUFACTURED_HOME_REGISTRATION,
  statusType: MhApiStatusTypes.EXEMPT,
}

