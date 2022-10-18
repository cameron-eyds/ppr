// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import VueRouter from 'vue-router'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'

// local components
import { HomeOwners, MhrInformation } from '@/views'
import { StickyContainer } from '@/components/common'
import mockRouter from './MockRouter'
import { HomeTenancyTypes, RouteNames } from '@/enums'
import { HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'
import { getTestId } from './utils'
import { mockedAddedPerson, mockedRemovedPerson, mockedOrganization, mockedPerson, mockMhrTransferCurrentHomeOwner } from './test-data'
import { MhrRegistrationHomeOwnerGroupIF, MhrRegistrationHomeOwnerIF } from '@/interfaces'
import { nextTick } from '@vue/composition-api'
import { TransferDetails } from '@/components/mhrTransfers'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  localVue.use(VueRouter)
  const router = mockRouter.mock()
  router.push({
    name: RouteNames.MHR_INFORMATION
  })

  document.body.setAttribute('data-app', 'true')
  return mount(MhrInformation, {
    localVue,
    store,
    propsData: {
      appReady: true,
      isMhrTransfer: true
    },
    vuetify,
    router
  })
}

// TODO: Remove after API updates to include the ID for Owners
function addIDsForOwners (ownersGroups): Array<any> {
  // Create an ID to each individual owner for UI Tracking
  ownersGroups.forEach(ownerGroup => {
    for (const [index, owner] of ownerGroup.owners.entries()) {
      owner.id = ownerGroup.groupId + (index + 1)
    }
  })

  return ownersGroups
}

async function setupCurrentHomeOwners (): Promise<void> {
  await store.dispatch('setMhrTransferCurrentHomeOwnerGroups', [mockMhrTransferCurrentHomeOwner])
  // TODO: Remove after API updates to include the ID for Owners
  const homeOwnerWithIdsArray = addIDsForOwners([mockMhrTransferCurrentHomeOwner])
  await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerWithIdsArray)
}

async function setupCurrentMultipleHomeOwnersGroups (): Promise<void> {
  // setup two groups so they can be shown in the table
  const currentHomeOwnersGroups = [
    mockMhrTransferCurrentHomeOwner,
    {
      ...mockMhrTransferCurrentHomeOwner,
      groupId: 2
    }
  ]

  await store.dispatch('setMhrTransferCurrentHomeOwnerGroups', currentHomeOwnersGroups)
  // TODO: Remove after API updates to include the ID for Owners
  const homeOwnerWithIdsArray = addIDsForOwners(currentHomeOwnersGroups)
  await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerWithIdsArray)
}

describe('Mhr Information', () => {
  let wrapper: Wrapper<any>
  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('AUTH_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')

  beforeEach(async () => {
    wrapper = createComponent()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders and displays the Mhr Information View', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.$data.dataLoaded = true
    await Vue.nextTick()

    expect(wrapper.props().isMhrTransfer).toBe(true)
    expect(wrapper.vm.$data.getMhrTransferCurrentHomeOwners.length).toBe(1)
    expect(wrapper.vm.$data.getMhrTransferHomeOwners.length).toBe(1)

    expect(wrapper.findComponent(MhrInformation).exists()).toBe(true)
    expect(wrapper.find('#mhr-information-header').text()).toContain('Manufactured Home Information')

    expect(wrapper.findComponent(HomeOwners).exists()).toBeTruthy()
    const homeOwnersTable = wrapper.findComponent(HomeOwnersTable)
    expect(homeOwnersTable.exists()).toBeTruthy()
    expect(homeOwnersTable.text()).toContain(mockMhrTransferCurrentHomeOwner.owners[0].organizationName)
    expect(homeOwnersTable.text()).toContain(mockMhrTransferCurrentHomeOwner.owners[0].address.city)
  })

  it('renders and displays the correct sub components', async () => {
    // Sticky container w/ Fee Summary
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
  })

  it('should render Added badge after Owner is added to the table', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.$data.dataLoaded = true
    await Vue.nextTick()

    const mhrInformationComponent = wrapper.findComponent(MhrInformation)
    expect(mhrInformationComponent.exists()).toBeTruthy()
    wrapper.vm.$data.dataLoaded = true
    await nextTick()

    expect(mhrInformationComponent.findComponent(HomeOwnersTable).exists()).toBeTruthy()

    const owners = [mockedAddedPerson, mockedRemovedPerson] as MhrRegistrationHomeOwnerIF[] // same IF for Transfer and Registration
    const homeOwnerGroup = [
      mockMhrTransferCurrentHomeOwner,
      { groupId: '2', owners: owners }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)

    const ownersTable = mhrInformationComponent.findComponent(HomeOwners).findComponent(HomeOwnersTable)

    const newlyAddedOwner = ownersTable.find(getTestId(`owner-info-${mockedPerson.id}`))
    expect(newlyAddedOwner.text()).toContain(mockedPerson.individualName.first)
    expect(newlyAddedOwner.text()).toContain(mockedPerson.individualName.last)

    const addedBadge = newlyAddedOwner.find(getTestId('owner-added-badge'))
    expect(addedBadge.isVisible()).toBeTruthy()

    const removedBadge = ownersTable.find(getTestId('owner-removed-badge'))
    expect(removedBadge.isVisible()).toBeTruthy()
  })

  it('should show correct Home Tenancy Type for MHR Transfers', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.$data.dataLoaded = true
    await Vue.nextTick()

    const homeOwnerGroup = [{ groupId: '1', owners: [mockedPerson] }]

    expect(wrapper.findComponent(HomeOwners).vm.$data.getHomeOwners.length).toBe(1)
    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.SOLE)

    // Add a second Owner
    homeOwnerGroup.push({ groupId: '1', owners: [mockedOrganization] })

    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)
    await Vue.nextTick()

    expect(wrapper.findComponent(HomeOwners).vm.$data.getHomeOwners.length).toBe(2)
    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.JOINT)

    // Enable Groups
    wrapper.findComponent(HomeOwners).vm.$data.setShowGroups(true)
    await Vue.nextTick()

    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.COMMON)
  })

  it('should correctly show current and newly added Owner Groups', async () => {
    setupCurrentMultipleHomeOwnersGroups()
    wrapper.vm.$data.dataLoaded = true
    await Vue.nextTick()

    // check current Owners and Groups
    wrapper.findComponent(HomeOwners).vm.$data.setShowGroups(true)
    await Vue.nextTick()

    expect(wrapper.findComponent(HomeOwners).vm.$data.getMhrTransferCurrentHomeOwners.length).toBe(2)
    expect(store.getters.getMhrTransferHomeOwnerGroups.length).toBe(2)

    const homeOwnersTable = wrapper.findComponent(HomeOwners).findComponent(HomeOwnersTable)

    const currentOwnerGroupHeader = homeOwnersTable.find(
      `#mhr-home-edit-owners-group-${mockMhrTransferCurrentHomeOwner.groupId}`
    )
    expect(currentOwnerGroupHeader.text()).toContain(`Group ${mockMhrTransferCurrentHomeOwner.groupId}`)
    expect(currentOwnerGroupHeader.text()).toContain('Owners: 1')

    expect(homeOwnersTable.findAll('.owner-info').length).toBe(2)
    const currentOwnerInfo = homeOwnersTable.findAll('.owner-info').at(0)

    expect(currentOwnerInfo.text()).toContain(mockMhrTransferCurrentHomeOwner.owners[0].organizationName)
    expect(currentOwnerInfo.text()).toContain(mockMhrTransferCurrentHomeOwner.owners[0].address.city)

    // Get current Groups
    const homeOwnerGroups = store.getters.getMhrTransferHomeOwnerGroups as MhrRegistrationHomeOwnerGroupIF[]

    // Add a second Group
    const NEW_GROUP_ID = '3'
    const newHomeOwnerGroup = { groupId: NEW_GROUP_ID, owners: [mockedPerson] } as MhrRegistrationHomeOwnerGroupIF
    homeOwnerGroups.push(newHomeOwnerGroup)
    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroups)
    await Vue.nextTick()

    // Check that new Groups and Owner info are added to the table
    expect(store.getters.getMhrTransferHomeOwnerGroups.length).toBe(3)
    expect(homeOwnersTable.findAll('.owner-info').length).toBe(3)

    const newOwnerGroupHeader = homeOwnersTable.find(`#mhr-home-edit-owners-group-${NEW_GROUP_ID}`)
    expect(newOwnerGroupHeader.text()).toContain(`Group ${NEW_GROUP_ID}`)

    const newOwnerInfo = homeOwnersTable.findAll('.owner-info').at(2)
    expect(newOwnerInfo.text()).toContain(mockedPerson.individualName.first)
    expect(newOwnerInfo.text()).toContain(mockedPerson.address.city)
  })

  // TRANSFER DETAILS COMPONENT TESTS

  it('should render Transfer Details component', async () => {
    const mhrTransferDetailsComponent = wrapper.findComponent(MhrInformation).findComponent(TransferDetails)
    expect(mhrTransferDetailsComponent.exists()).toBeTruthy()

    // Check for component's fields
    expect(mhrTransferDetailsComponent.find(getTestId('declared-value')).exists()).toBeTruthy()
    expect(mhrTransferDetailsComponent.find(getTestId('consideration')).exists()).toBeTruthy()
    expect(mhrTransferDetailsComponent.find(getTestId('transfer-date')).exists()).toBeTruthy()
    expect(mhrTransferDetailsComponent.find(getTestId('lease-own-checkbox')).exists()).toBeTruthy()

    mhrTransferDetailsComponent.find(getTestId('declared-value')).setValue(123)
    mhrTransferDetailsComponent.find(getTestId('declared-value')).trigger('blur')
    await Vue.nextTick()

    // Check that error/warning is shown for Declared Value less than 500
    expect(mhrTransferDetailsComponent.find('.v-messages__message').isVisible()).toBeTruthy()
    await Vue.nextTick()

    // Check that Consideration displayed Declared Value on blur
    expect(mhrTransferDetailsComponent.vm.$data.consideration).toBe('$123.00')
  })
})