import { AddressIF, MhrRegistrationHomeOwnerGroupIF, MhrRegistrationHomeOwnerIF } from "@/interfaces";

export const mockMhrTransferCurrentHomeOwner = {
  groupId: 1,
  interestNumerator: 1,
  interestDenominator: 1,
  owners: [
    {
      address: {
        city: 'KELOWNA',
        country: 'CA',
        postalCode: 'V1X7T1',
        region: 'BC',
        street: '3075 SEXSMITH ROAD'
      } as AddressIF,
      organizationName: 'CHAPARRAL INDUSTRIES (86) INC.',
      phoneNumber: '2507652985',
      phoneExtension: '1234',
      type: 'SOLE'
    } as MhrRegistrationHomeOwnerIF
  ],
  status: 'PREVIOUS',
  tenancySpecified: true,
  type: 'SOLE'
} as MhrRegistrationHomeOwnerGroupIF
