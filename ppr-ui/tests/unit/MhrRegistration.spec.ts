// Libraries
import { useStore } from '../../src/store/store'

// local components
import { MhrRegistration } from '@/pages'
import { ButtonFooter , Stepper, StickyContainer } from '@/components/common'
import { MhrCorrectionStaff, MhrReRegistrationType, MhrRegistrationType } from '@/resources'
import { defaultFlagSet } from '@/utils'
import { AuthRoles, HomeTenancyTypes, MhApiStatusTypes, RouteNames } from '@/enums'
import { mockMhrReRegistration, mockedManufacturerAuthRoles, mockedMhrRegistration, mockedPerson } from './test-data'
import { createComponent, getTestId } from './utils'
import { useMhrReRegistration, useNewMhrRegistration } from '@/composables'
import { nextTick } from 'vue'
import CautionBox from '@/components/common/CautionBox.vue'
import HomeOwnersTable from '@/components/mhrRegistration/HomeOwners/HomeOwnersTable.vue'
import SubmittingParty from '@/pages/newMhrRegistration/SubmittingParty.vue'
import HomeLocation from '@/pages/newMhrRegistration/HomeLocation.vue'
import HomeOwners from '@/pages/newMhrRegistration/HomeOwners.vue'
import type { MhrRegistrationHomeOwnerGroupIF } from '@/interfaces'
import { PreviousHomeOwners } from '@/components/mhrRegistration'

const store = useStore()

describe.skip('Mhr Registration', () => {
  let wrapper: any

  beforeEach(async () => {
    // Staff with MHR enabled
    defaultFlagSet['mhr-registration-enabled'] = true
    await store.setRegistrationType(MhrRegistrationType)
    wrapper = await createComponent(MhrRegistration, { appReady: true }, RouteNames.YOUR_HOME)
  })

  it('renders and displays the Mhr Registration View', async () => {
    expect(wrapper.findComponent(MhrRegistration).exists()).toBe(true)
    expect(wrapper.find('#registration-header').text()).toBe('Manufactured Home Registration')
  })

  it('renders and displays the correct sub components', async () => {
    // Stepper
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    // Action button footers
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    // Sticky container w/ Fee Summary
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
  })
})

describe.skip('Mhr Manufacturer Registration', () => {
  let wrapper: any

  beforeEach(async () => {
    defaultFlagSet['mhr-registration-enabled'] = true
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    await store.setRegistrationType(MhrRegistrationType)

    wrapper = await createComponent(MhrRegistration, { appReady: true }, RouteNames.YOUR_HOME)
  })

  it('renders and displays the Mhr Registration View', async () => {
    expect(wrapper.findComponent(MhrRegistration).exists()).toBe(true)
    expect(wrapper.find('#registration-header').text()).toBe('Manufactured Home Registration')
  })

  it('renders and displays the correct sub components', async () => {
    // Stepper
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    // Action button footers
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    // Sticky container w/ Fee Summary
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
  })
})

describe.skip('Mhr Correction', () => {
  let wrapper: any
  const { initDraftOrCurrentMhr } = useNewMhrRegistration()

  beforeEach(async () => {
    // Staff with MHR enabled
    defaultFlagSet['mhr-registration-enabled'] = true
    await store.setRegistrationType(MhrCorrectionStaff)
    await initDraftOrCurrentMhr(mockedMhrRegistration)
    wrapper = await createComponent(MhrRegistration, { appReady: true }, RouteNames.SUBMITTING_PARTY)
  })

  it('renders and displays the Mhr Registration View', async () => {
    expect(wrapper.findComponent(MhrRegistration).exists()).toBe(true)
    expect(wrapper.find('#registration-correction-header').text()).toBe('Registry Correction - Staff Error or Omission')
  })

  it('renders and displays the correct sub components', async () => {
    // Stepper
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    // Action button footers
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    // Sticky container w/ Fee Summary
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
  })
})

describe.skip('Mhr Re-Registration', () => {
  let wrapper: any

  beforeEach(async () => {
    // Staff with MHR enabled
    await store.setAuthRoles([AuthRoles.PPR_STAFF])
    defaultFlagSet['mhr-registration-enabled'] = true
    store.setRegistrationType(MhrReRegistrationType)
    store.setMhrStatusType(MhApiStatusTypes.EXEMPT)

    await store.setMhrInformation({
      permitDateTime: mockMhrReRegistration.permitDateTime,
      permitExpiryDateTime: mockMhrReRegistration.permitExpiryDateTime,
      permitRegistrationNumber: mockMhrReRegistration.permitRegistrationNumber,
      permitStatus: mockMhrReRegistration.permitStatus
    })
    await nextTick()

    const homeOwnerGroup = [{ groupId: 1, owners: [mockedPerson] }] as MhrRegistrationHomeOwnerGroupIF[]
    useMhrReRegistration().setupPreviousOwners(homeOwnerGroup)
    useNewMhrRegistration().initDraftOrCurrentMhr(mockMhrReRegistration as any, false)
    await nextTick()

    wrapper = await createComponent(MhrRegistration, { appReady: true }, RouteNames.SUBMITTING_PARTY)
  })

  it('renders and displays the Mhr Re-Registration View', async () => {
    expect(wrapper.findComponent(MhrRegistration).exists()).toBe(true)
    expect(wrapper.find('#re-registration-header h1').text()).toBe(MhrReRegistrationType.registrationTypeUI)
    expect(wrapper.vm.$route.name).toBe(RouteNames.SUBMITTING_PARTY)

    expect(wrapper.findComponent(SubmittingParty).findComponent(CautionBox).exists()).toBe(false)

    // Go to Home Owners step
    wrapper.findComponent(Stepper).findAll('.step').at(2).trigger('click')
    await nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.HOME_OWNERS)
    const homeOwnersTable = wrapper.findComponent(HomeOwnersTable)
    expect(homeOwnersTable.find(getTestId('no-data-msg')).exists()).toBe(true) // should not have owners for Re-Reg
    expect(wrapper.findComponent(HomeOwners).findComponent(CautionBox).exists()).toBe(false)

    // Previous Home Owners
    const prevOwnersCard = wrapper.findComponent(PreviousHomeOwners)
    expect(prevOwnersCard.exists()).toBe(true)
    expect(prevOwnersCard.find(getTestId('card-header-label')).text()).toBe('Previous Home Owners')
    expect(prevOwnersCard.find(getTestId('card-toggle-label')).text()).toBe('Hide Previous Owners')
    expect(prevOwnersCard.find(getTestId('home-owner-tenancy-type')).text()).toContain(HomeTenancyTypes.SOLE)
    expect(prevOwnersCard.findComponent(HomeOwnersTable).exists()).toBe(true)

    const homeOwnersTableText = prevOwnersCard.findComponent(HomeOwnersTable).text()
    expect(homeOwnersTableText).toContain(mockedPerson.individualName.first)
    expect(homeOwnersTableText).toContain(mockedPerson.phoneNumber)
    expect(homeOwnersTableText).toContain(mockedPerson.address.street)

    // Go to Home Location step
    wrapper.findComponent(Stepper).findAll('.step').at(3).trigger('click')
    await nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.HOME_LOCATION)

    const homeLocationStepWrapper = wrapper.findComponent(HomeLocation)
    expect(homeLocationStepWrapper.findComponent(CautionBox).exists()).toBe(true)
  })
})
