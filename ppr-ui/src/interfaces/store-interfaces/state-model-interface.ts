import { RegistrationFlowType } from '@/enums'
import {
  AccountInformationIF, AuthorizationIF, CertifyIF, RegistrationTypeIF, SearchResponseIF,
  SearchTypeIF, RegTableDataI, UserInfoIF
} from '@/interfaces'
import { AccountProductSubscriptionIF } from '../account-interfaces'
import { CourtOrderIF, DebtorNameIF, DraftIF, IndividualNameIF, ManufacturedHomeSearchResponseIF, ManufacturedHomeSearchResultIF } from '../ppr-api-interfaces'
import { AddPartiesIF, AddCollateralIF, LengthTrustIF } from '../registration-interfaces'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'

// State model example
export interface StateModelIF {
  accountInformation: AccountInformationIF
  accountProductSubscriptions: AccountProductSubscriptionIF
  authorization: AuthorizationIF
  certifyInformation: CertifyIF
  folioOrReferenceNumber: string
  // for amendments only
  originalRegistration: {
    collateral: AddCollateralIF
    lengthTrust: LengthTrustIF
    parties: AddPartiesIF
  }
  registration: {
    amendmentDescription: string // amendments only
    collateral: AddCollateralIF
    confirmDebtorName: DebtorNameIF // Required for actions on existing registrations.
    courtOrderInformation: CourtOrderIF
    creationDate: string
    draft: DraftIF
    expiryDate: string
    registrationFlowType: RegistrationFlowType
    lengthTrust: LengthTrustIF
    parties: AddPartiesIF
    registrationNumber: string
    registrationType: RegistrationTypeIF
    registrationTypeOtherDesc: string
    showStepErrors: boolean
  }
  registrationTable: RegTableDataI
  search: {
    searchDebtorName: IndividualNameIF
    searchHistory: Array<SearchResponseIF>
    searchHistoryLength: Number
    searchResults: SearchResponseIF
    manufacturedHomeSearchResults: ManufacturedHomeSearchResponseIF
    searchedType: SearchTypeIF
    searchedValue: string
    searching: boolean
    searchCertified: boolean
  }
  selectedManufacturedHomes: ManufacturedHomeSearchResultIF[]
  staffPayment: StaffPaymentIF
  unsavedChanges: Boolean // used for cancel flows
  userInfo: UserInfoIF
}