<template>
  <v-container
    id="debtors-component"
    fluid
    class="pa-0 noGutters"
    role="region"
  >
    <v-row no-gutters>
      <v-col cols="auto">
        Include Debtors as <b>either</b> an Individual or a Business. If the debtor is
        operating a business and you want to register both the name of the
        business and the individual associated with the business, enter them as
        separate debtors.<br><br>
        Note: If a Debtor name is entered incorrectly, it could invalidate the
        entire registration.
      </v-col>
    </v-row>
    <v-row
      no-gutters
      class="pb-4 pt-10"
    >
      <v-col>
        <v-btn
          id="btn-add-individual"
          class="mr-4"
          variant="outlined"
          color="primary"
          :disabled="addEditInProgress"
          @click="initAdd(false)"
        >
          <v-icon>mdi-account-plus</v-icon>
          <span>Add an Individual Debtor</span>
        </v-btn>

        <v-btn
          id="btn-add-business"
          variant="outlined"
          color="primary"
          :disabled="addEditInProgress"
          @click="initAdd(true)"
        >
          <v-icon>mdi-domain-plus</v-icon>
          <span>Add a Business Debtor</span>
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <div :class="{ 'invalid-section': invalidSection }">
          <v-expand-transition>
            <v-card
              v-if="showAddDebtor"
              flat
              class="add-debtor-container"
            >
              <EditDebtor
                :active-index="activeIndex"
                :is-business="currentIsBusiness"
                :invalid-section="invalidSection"
                :set-show-error-bar="showErrorBar"
                @reset-event="resetData"
              />
            </v-card>
          </v-expand-transition>
        </div>
      </v-col>
    </v-row>

    <v-row
      no-gutters
      class="pt-4"
    >
      <v-col>
        <v-table
          class="debtor-table debtor-data-table"
          :class="{ 'border-error-left': showErrorDebtors && !getDebtorValidity() }"
        >
          <template #default>
            <!-- Table Headers -->
            <thead>
              <tr>
                <th
                  v-for="header in headers"
                  :key="header.value"
                  :class="header.class"
                  :aria-hidden="!header.text"
                >
                  {{ header.text }}
                </th>
              </tr>
            </thead>

            <!-- Table Body -->
            <tbody v-if="debtors.length > 0">
              <tr
                v-for="(item, index) in debtors"
                :key="`${item}: ${index}`"
                class="debtor-row"
                :class="{ 'disabled-text-not-action': item.action === ActionTypes.REMOVED}"
              >
                <template v-if="showEditDebtor[index]">
                  <!-- Edit Form -->
                  <td
                    colspan="5"
                    class="pa-0"
                    :class="{ 'invalid-section': invalidSection }"
                  >
                    <v-card
                      flat
                      class="edit-debtor-container"
                    >
                      <edit-debtor
                        :active-index="activeIndex"
                        :invalid-section="invalidSection"
                        :set-show-error-bar="showErrorBar"
                        @remove-debtor="removeDebtor"
                        @reset-event="resetData"
                      />
                    </v-card>
                  </td>
                </template>
                <template v-else>
                  <td
                    class="list-item__title title-text generic-label chip-cell"
                    style="padding-left:30px"
                  >
                    <v-row
                      no-gutters
                      :aria-label="`${isBusiness(item) ? 'Business' : 'Person'} ${getName(item)}`"
                    >
                      <v-col
                        cols="auto"
                        aria-hidden="true"
                        :class="{ 'disabled-text': item.action === ActionTypes.REMOVED}"
                      >
                        <div class="icon-div mt-n1 pr-2">
                          <v-icon v-if="isBusiness(item)">
                            mdi-domain
                          </v-icon>
                          <v-icon v-else>
                            mdi-account
                          </v-icon>
                        </div>
                      </v-col>
                      <v-col
                        cols="9"
                        aria-hidden="true"
                      >
                        <span :class="{ 'disabled-text': item.action === ActionTypes.REMOVED}">
                          {{ getName(item) }}
                        </span>
                        <div v-if="item.action && registrationFlowType === RegistrationFlowType.AMENDMENT">
                          <v-chip
                            v-if="item.action === ActionTypes.REMOVED"
                            x-small
                            variant="elevated"
                            color="greyLighten"
                          >
                            {{ item.action }}
                          </v-chip>
                          <v-chip
                            v-else
                            x-small
                            variant="elevated"
                            color="#1669BB"
                          >
                            {{ item.action }}
                          </v-chip>
                        </div>
                      </v-col>
                    </v-row>
                  </td>
                  <td>
                    <BaseAddress
                      :editing="false"
                      :schema="addressSchema"
                      :value="item.address"
                    />
                  </td>
                  <td>{{ getFormattedBirthdate(item) }}</td>
                  <!-- Action Btns -->
                  <td class="actions-width actions-cell pr-5">
                    <div class="actions-up">
                      <span
                        v-if="registrationFlowType !== RegistrationFlowType.AMENDMENT
                          || (registrationFlowType === RegistrationFlowType.AMENDMENT &&
                            (item.action === ActionTypes.ADDED) || !item.action)"
                        class="edit-button"
                      >
                        <v-btn
                          :id="'class-' + index + '-change-added-btn'"
                          variant="plain"
                          color="primary"
                          class="smaller-button edit-btn"
                          :disabled="addEditInProgress"
                          @click="initEdit(index)"
                        >
                          <v-icon size="small">mdi-pencil</v-icon>
                          <span
                            v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                              && item.action !== ActionTypes.ADDED"
                          >
                            Amend
                          </span>
                          <span v-else>Edit</span>
                        </v-btn>
                      </span>
                      <span
                        v-if="registrationFlowType !== RegistrationFlowType.AMENDMENT
                          || (registrationFlowType === RegistrationFlowType.AMENDMENT && (!item.action ||
                            item.action === ActionTypes.ADDED))"
                        class="actions-border actions__more pr-1"
                      >
                        <v-menu
                          location="bottom right"
                        >
                          <template #activator="{ props }">
                            <v-btn
                              variant="plain"
                              size="small"
                              color="primary"
                              class="smaller-actions actions__more-actions__btn"
                              :disabled="addEditInProgress"
                              v-bind="props"
                            >
                              <v-icon>mdi-menu-down</v-icon>
                            </v-btn>
                          </template>
                          <v-list class="actions__more-actions">
                            <v-list-item @click="removeDebtor(index)">
                              <v-list-item-subtitle>
                                <v-icon size="small">mdi-delete</v-icon>
                                <span
                                  v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                                    && item.action !== ActionTypes.ADDED"
                                >
                                  Delete
                                </span>
                                <span
                                  v-else
                                  class="ml-1"
                                >Remove</span>
                              </v-list-item-subtitle>
                            </v-list-item>
                          </v-list>
                        </v-menu>
                      </span>
                      <span
                        v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                          && ((item.action === ActionTypes.REMOVED) || (item.action === ActionTypes.EDITED))"
                        class="undo-button"
                      >
                        <v-btn
                          :id="'class-' + index + '-undo-btn'"
                          variant="plain"
                          color="primary"
                          class="smaller-button edit-btn"
                          :disabled="addEditInProgress"
                          @click="undo(index)"
                        >
                          <v-icon size="small">mdi-undo</v-icon>
                          <span>Undo</span>
                        </v-btn>
                      </span>

                      <span
                        v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                          && item.action === ActionTypes.EDITED"
                        class="actions-border actions__more"
                      >
                        <v-menu
                          location="bottom left"
                        >
                          <template #activator="{ props }">
                            <v-btn
                              variant="plain"
                              size="small"
                              color="primary"
                              class="smaller-actions actions__more-actions__btn"
                              :disabled="addEditInProgress"
                              v-bind="props"
                            >
                              <v-icon>mdi-menu-down</v-icon>
                            </v-btn>
                          </template>
                          <v-list class="actions__more-actions">
                            <v-list-item @click="initEdit(index)">
                              <v-list-item-subtitle>
                                <v-icon size="small">mdi-pencil</v-icon>
                                <span class="ml-1">Amend</span>
                              </v-list-item-subtitle>
                            </v-list-item>
                            <v-list-item @click="removeDebtor(index)">
                              <v-list-item-subtitle>
                                <v-icon size="small">mdi-delete</v-icon>
                                <span
                                  v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                                    && item.action !== ActionTypes.ADDED"
                                >
                                  Delete
                                </span>
                                <span
                                  v-else
                                  class="ml-1"
                                >Remove</span>
                              </v-list-item-subtitle>
                            </v-list-item>
                          </v-list>
                        </v-menu>
                      </span>
                    </div>
                  </td>
                </template>
              </tr>
            </tbody>
            <!-- No Data Message -->
            <tbody v-else>
              <tr>
                <td
                  class="text-center"
                  :colspan="headers.length"
                >
                  No debtors added yet
                </td>
              </tr>
            </tbody>
          </template>
        </v-table>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  computed,
  watch
} from 'vue'
import { useStore } from '@/store/store'
import type { AddPartiesIF } from '@/interfaces'
import EditDebtor from './EditDebtor.vue'
import { useParty } from '@/composables/useParty'
import { BaseAddress } from '@/composables/address'

import { debtorTableHeaders, editTableHeaders } from '@/resources'
import { PartyAddressSchema } from '@/schemas'
import { ActionTypes, RegistrationFlowType } from '@/enums'
import { cloneDeep } from 'lodash'
import { storeToRefs } from 'pinia'

export default defineComponent({
  components: {
    EditDebtor,
    BaseAddress
  },
  props: {
    isSummary: {
      type: Boolean,
      default: false
    },
    setShowInvalid: {
      type: Boolean,
      default: false
    },
    setShowErrorBar: {
      type: Boolean,
      default: false
    }
  },
  emits: ['setDebtorValid', 'debtorOpen'],
  setup (props, { emit }) {
    const { setAddSecuredPartiesAndDebtors } = useStore()
    const {
      // Getters
      getAddSecuredPartiesAndDebtors,
      getRegistrationFlowType,
      getRegistrationType,
      getOriginalAddSecuredPartiesAndDebtors
    } = storeToRefs(useStore())

    const registrationFlowType = getRegistrationFlowType.value
    const addressSchema = PartyAddressSchema
    const {
      getName,
      getFormattedBirthdate,
      isPartiesValid,
      isBusiness
    } = useParty()

    const localState = reactive({
      summaryView: props.isSummary,
      showAddDebtor: false,
      currentIsBusiness: true,
      addEditInProgress: false,
      invalidSection: false,
      activeIndex: -1,
      showEditDebtor: [false],
      debtors: getAddSecuredPartiesAndDebtors.value.debtors,
      showErrorSummary: computed((): boolean => {
        return !getAddSecuredPartiesAndDebtors.value.valid
      }),
      showErrorDebtors: getAddSecuredPartiesAndDebtors.value.showInvalid,
      parties: computed((): AddPartiesIF => {
        return getAddSecuredPartiesAndDebtors.value
      }),
      showErrorBar: computed((): boolean => {
        return props.setShowErrorBar
      }),
      headers: [...debtorTableHeaders, ...editTableHeaders]
    })

    const removeDebtor = (index: number): void => {
      let currentParties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
      const currentDebtor = currentParties.debtors[index]
      if ((registrationFlowType === RegistrationFlowType.AMENDMENT) && (currentDebtor.action !== ActionTypes.ADDED)) {
        currentDebtor.action = ActionTypes.REMOVED
        localState.debtors.splice(index, 1, currentDebtor)
        setAddSecuredPartiesAndDebtors(currentParties)
      } else {
        localState.debtors.splice(index, 1)
        currentParties.debtors = localState.debtors
        currentParties.valid = isPartiesValid(currentParties, getRegistrationType.value?.registrationTypeAPI)
        setAddSecuredPartiesAndDebtors(currentParties)
      }
      const isValid = getDebtorValidity()
      emitDebtorValidity(isValid)
    }

    const initEdit = (index: number) => {
      localState.activeIndex = index
      localState.addEditInProgress = true
      localState.showEditDebtor[index] = true
      emit('debtorOpen', true)
    }

    const initAdd = (currentIsBusiness: boolean) => {
      localState.currentIsBusiness = currentIsBusiness
      localState.addEditInProgress = true
      localState.showAddDebtor = true
      emit('debtorOpen', true)
    }

    const resetData = () => {
      localState.activeIndex = -1
      localState.addEditInProgress = false
      localState.showAddDebtor = false
      localState.showEditDebtor = [false]
      let currentParties = getAddSecuredPartiesAndDebtors.value // eslint-disable-line
      currentParties.valid = isPartiesValid(currentParties, getRegistrationType.value?.registrationTypeAPI)
      setAddSecuredPartiesAndDebtors(currentParties)
      const isValid = getDebtorValidity()
      emitDebtorValidity(isValid)
      emit('debtorOpen', false)
    }

    const undo = (index: number): void => {
      const originalParties = getOriginalAddSecuredPartiesAndDebtors.value
      localState.debtors.splice(index, 1, cloneDeep(originalParties.debtors[index]))
      const isValid = getDebtorValidity()
      emitDebtorValidity(isValid)
    }

    const getDebtorValidity = (): boolean => {
      let validity = false
      if (registrationFlowType === RegistrationFlowType.AMENDMENT) {
        for (let i = 0; i < localState.debtors.length; i++) {
          // is valid if there is at least one debtor
          if (localState.debtors[i].action !== ActionTypes.REMOVED) {
            validity = true
          }
        }
      } else {
        if (localState.debtors.length > 0) {
          validity = true
        }
      }
      return validity
    }

    const emitDebtorValidity = (validity: boolean): void => {
      emit('setDebtorValid', validity)
    }

    watch(() => props.setShowInvalid, (val) => {
      localState.showErrorDebtors = val
    })

    return {
      removeDebtor,
      getDebtorValidity,
      getName,
      getFormattedBirthdate,
      initEdit,
      initAdd,
      resetData,
      undo,
      isBusiness,
      addressSchema,
      registrationFlowType,
      RegistrationFlowType,
      ActionTypes,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

td {
  word-wrap: break-word;
}

.undo-button {
  padding-right: 0px;
}

</style>
