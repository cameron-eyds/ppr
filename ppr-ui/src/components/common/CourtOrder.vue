<template>
  <v-container
    v-if="renewalView && isSummary"
    id="court-order-component"
    class="pa-0"
  >
    <h2 class="pt-2 pb-5">
      Court Order
    </h2>
    <v-container
      class="bg-white"
      style="padding: 40px 30px;"
    >
      <v-row
        no-gutters
        class="pb-7"
      >
        <v-col
          cols="3"
          class="generic-label"
        >
          Court Name
        </v-col>
        <v-col
          id="court-name-display"
          cols="9"
        >
          {{ courtName }}
        </v-col>
      </v-row>
      <v-row
        no-gutters
        class="pb-7"
      >
        <v-col
          cols="3"
          class="generic-label"
        >
          Court Registry
        </v-col>
        <v-col
          id="court-registry-display"
          cols="9"
        >
          {{ courtRegistry }}
        </v-col>
      </v-row>
      <v-row
        no-gutters
        class="pb-7"
      >
        <v-col
          cols="3"
          class="generic-label"
        >
          Court File Number
        </v-col>
        <v-col
          id="file-number-display"
          cols="9"
        >
          {{ fileNumber }}
        </v-col>
      </v-row>
      <v-row
        no-gutters
        class="pb-7"
      >
        <v-col
          cols="3"
          class="generic-label"
        >
          Date of Order
        </v-col>
        <v-col
          id="date-display"
          cols="9"
        >
          {{ computedDateFormatted }}
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col
          cols="3"
          class="generic-label"
        >
          Effect of Order
        </v-col>
        <v-col
          id="effect-display"
          cols="9"
        >
          <span style="white-space: pre-wrap">{{ effectOfOrder }}</span>
        </v-col>
      </v-row>
    </v-container>
  </v-container>
  <v-container v-else-if="isSummary">
    <v-row
      no-gutters
      class="py-2"
    >
      <v-col
        cols="auto"
        class="generic-label"
      >
        <label>
          <strong>Court Order</strong>
        </label>
      </v-col>
    </v-row>
    <v-row
      no-gutters
      style="padding: 15px 30px;"
    >
      <v-col class="generic-label">
        Court Name
      </v-col>
      <v-col
        id="court-name-display"
        cols="9"
      >
        {{ courtName }}
      </v-col>
    </v-row>
    <v-row
      no-gutters
      style="padding: 15px 30px;"
    >
      <v-col class="generic-label">
        Court Registry
      </v-col>
      <v-col
        id="court-registry-display"
        cols="9"
      >
        {{ courtRegistry }}
      </v-col>
    </v-row>
    <v-row
      no-gutters
      style="padding: 15px 30px;"
    >
      <v-col class="generic-label">
        Court File Number
      </v-col>
      <v-col
        id="file-number-display"
        cols="9"
      >
        {{ fileNumber }}
      </v-col>
    </v-row>
    <v-row
      no-gutters
      style="padding: 15px 30px;"
    >
      <v-col class="generic-label">
        Date of Order
      </v-col>
      <v-col
        id="date-display"
        cols="9"
      >
        {{ computedDateFormatted }}
      </v-col>
    </v-row>
    <v-row
      no-gutters
      style="padding: 15px 30px;"
    >
      <v-col class="generic-label">
        Effect of Order
      </v-col>
      <v-col
        id="effect-display"
        cols="9"
      >
        <span style="white-space: pre-wrap">{{ effectOfOrder }}</span>
      </v-col>
    </v-row>
  </v-container>
  <v-container
    v-else
    fluid
    class="pb-6  px-0 rounded noGutters"
  >
    <v-card
      id="court-order"
      class="rounded"
      :class="showErrors && !valid ? 'border-error-left' : ''"
      flat
    >
      <v-row
        no-gutters
        class="summary-header pa-2 mb-8"
      >
        <v-col
          cols="auto"
          class="py-2 px-4"
        >
          <v-icon color="darkBlue">
            mdi-gavel
          </v-icon>
          <label class="pl-3">
            <strong>Court Order</strong>
          </label>
        </v-col>
      </v-row>
      <v-row
        no-gutters
        class="summary-text"
        style="padding: 0 30px;"
      >
        <v-col v-if="requireCourtOrder && registrationType === APIRegistrationTypes.REPAIRERS_LIEN">
          A court order is required to renew a Repairer's Lien. Enter the court
          order information below. A default Effect of Order is provided; you can
          modify this default text if you wish.
        </v-col>
        <v-col v-else>
          If this registration is pursuant to a court order, enter the court order
          information below, otherwise leave the Court Order information empty.
        </v-col>
      </v-row>
      <v-form
        v-model="valid"
        class="px-6"
      >
        <v-row
          no-gutters
        >
          <v-col
            cols="3"
            class="generic-label pt-10"
          >
            Court Name
          </v-col>
          <v-col
            cols="9"
            class="pt-8"
          >
            <v-text-field
              id="txt-court-name"
              v-model.trim="courtName"
              variant="filled"
              color="primary"
              label="Court Name"
              hint="For example: Supreme Court of British Columbia"
              persistent-hint
              :error-messages="
                errors.courtName.message ? errors.courtName.message : courtNameMessage
              "
            />
          </v-col>
        </v-row>
        <v-row
          no-gutters
        >
          <v-col
            cols="3"
            class="generic-label pt-6"
          >
            Court Registry
          </v-col>
          <v-col
            cols="9"
            class="pt-4"
          >
            <v-text-field
              id="txt-court-registry"
              v-model.trim="courtRegistry"
              variant="filled"
              color="primary"
              label="Court Registry"
              hint="The location (city) of the court. For example: Richmond"
              persistent-hint
              :error-messages="
                errors.courtRegistry.message ? errors.courtRegistry.message : courtRegistryMessage
              "
            />
          </v-col>
        </v-row>
        <v-row
          no-gutters
        >
          <v-col
            cols="3"
            class="generic-label pt-6"
          >
            Court File Number
          </v-col>
          <v-col
            cols="9"
            class="pt-4"
          >
            <v-text-field
              id="txt-court-file-number"
              v-model.trim="fileNumber"
              variant="filled"
              color="primary"
              label="Court File Number"
              persistent-hint
              :error-messages="
                errors.fileNumber.message ? errors.fileNumber.message : fileNumberMessage
              "
            />
          </v-col>
        </v-row>
        <v-row
          no-gutters
        >
          <v-col
            cols="3"
            class="generic-label pt-6"
          >
            Date of Order
          </v-col>
          <v-col
            cols="9"
            class="pt-4"
          >
            <InputFieldDatePicker
              id="court-date-text-field"
              ref="datePickerRef"
              :key="datePickerKey"
              class="court-date-text-input"
              nudge-right="40"
              title="Date of Order"
              :error-msg="errors.orderDate.message ? errors.orderDate.message : ''"
              :initial-value="orderDate"
              :min-date="minCourtDate"
              :max-date="maxCourtDate"
              :persistent-hint="true"
              @emit-date="orderDate = $event"
              @emit-cancel="orderDate = ''"
            />
          </v-col>
        </v-row>
        <v-row
          no-gutters
        >
          <v-col
            cols="3"
            class="generic-label pt-6"
          >
            Effect of Order
          </v-col>
          <v-col
            cols="9"
            class="pt-4"
          >
            <v-textarea
              id="effect-of-order"
              v-model.trim="effectOfOrder"
              auto-grow
              counter="512"
              variant="filled"
              color="primary"
              label="Effect of Order"
              class="bg-white pt-2 text-input-field"
              :error-messages="
                errors.effectOfOrder.message ? errors.effectOfOrder.message : effectOfOrderMessage
              "
            />
          </v-col>
        </v-row>
      </v-form>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import { isEqual } from 'lodash'
import InputFieldDatePicker from '@/components/common/InputFieldDatePicker.vue'
import { APIRegistrationTypes } from '@/enums'
import type { CourtOrderIF } from '@/interfaces'
import { convertDate, localTodayDate } from '@/utils'
import { useCourtOrderValidation } from './composables'
import { storeToRefs } from 'pinia'

export default defineComponent({
  components: {
    InputFieldDatePicker
  },
  props: {
    setShowErrors: {
      type: Boolean,
      default: false
    },
    setRequireCourtOrder: {
      type: Boolean,
      default: false
    },
    setSummary: {
      type: Boolean,
      default: false
    },
    isRenewal: {
      type: Boolean,
      default: false
    }
  },
  emits: ['setCourtOrderValid'],
  setup (props, { emit }) {
    const {
      // Actions
      setCourtOrderInformation,
      setUnsavedChanges
    } = useStore()
    const {
      // Getters
      getCourtOrderInformation,
      getRegistrationType,
      getRegistrationCreationDate,
      hasUnsavedChanges
    } = storeToRefs(useStore())
    const {
      errors,
      valid,
      validateCourtOrderForm,
      isValidCourtOrderForm,
      resetErrors
    } = useCourtOrderValidation()
    const modal = false
    const registrationType = getRegistrationType.value?.registrationTypeAPI
    const localState = reactive({
      renewalView: props.isRenewal,
      courtName: '',
      courtRegistry: '',
      fileNumber: '',
      orderDate: '',
      effectOfOrder: '',
      datePickerKey: Math.random(),
      courtOrderInfo: computed(
        (): CourtOrderIF => {
          return getCourtOrderInformation.value as CourtOrderIF
        }
      ),
      computedDateFormatted: computed((): string => {
        if (getCourtOrderInformation.value === null) {
          return ''
        }
        return getCourtOrderInformation.value?.orderDate !== ''
          ? convertDate(
            new Date(getCourtOrderInformation.value.orderDate + 'T09:00:00Z'),
            false,
            false
          )
          : ''
      }),
      requireCourtOrder: computed((): boolean => {
        return props.setRequireCourtOrder
      }),
      isSummary: computed((): boolean => {
        return props.setSummary
      }),
      showErrors: computed((): boolean => {
        if ((props.setShowErrors === true) && (shouldValidate())) {
          validateCourtOrderForm(localState.courtOrderInfo)
        }
        return props.setShowErrors
      }),
      minCourtDate: computed((): string => {
        if (registrationType === APIRegistrationTypes.REPAIRERS_LIEN) {
          return new Date(getRegistrationCreationDate.value).toString()
        } else {
          return ''
        }
      }),
      maxCourtDate: computed((): string => {
        return new Date().toString()
      }),
      fileNumberMessage: computed((): string => {
        if (localState.fileNumber.length > 20) {
          return 'Maximum 20 characters'
        }
        return ''
      }),
      courtNameMessage: computed((): string => {
        if (localState.courtName.length > 256) {
          return 'Maximum 256 characters'
        }
        return ''
      }),
      courtRegistryMessage: computed((): string => {
        if (localState.courtRegistry.length > 64) {
          return 'Maximum 64 characters'
        }
        return ''
      }),
      effectOfOrderMessage: computed((): string => {
        if (localState.effectOfOrder.length > 512) {
          return 'Maximum 512 characters'
        }
        return ''
      })
    })

    const emitValid = async () => {
      if (!shouldValidate()) {
        resetErrors()
        emit('setCourtOrderValid', valid.value)
      } else {
        await isValidCourtOrderForm(localState.courtOrderInfo)
        emit('setCourtOrderValid', valid.value)
      }
    }

    const shouldValidate = () => {
      return !!((localState.courtName) || (localState.courtRegistry) ||
        (localState.fileNumber) || (localState.orderDate) || (localState.effectOfOrder) ||
        (localState.requireCourtOrder))
    }

    watch(
      () => localState.courtName,
      (val: string) => {
        const newCourtOrderInfo = localState.courtOrderInfo
        newCourtOrderInfo.courtName = val
        setCourtOrderInformation(newCourtOrderInfo)
        emitValid()
      }
    )

    watch(
      () => localState.fileNumber,
      (val: string) => {
        const newCourtOrderInfo = localState.courtOrderInfo
        newCourtOrderInfo.fileNumber = val
        setCourtOrderInformation(newCourtOrderInfo)
        emitValid()
      }
    )

    watch(
      () => localState.courtRegistry,
      (val: string) => {
        const newCourtOrderInfo = localState.courtOrderInfo
        newCourtOrderInfo.courtRegistry = val
        setCourtOrderInformation(newCourtOrderInfo)
        emitValid()
      }
    )

    watch(
      () => localState.orderDate,
      (val: string) => {
        const newCourtOrderInfo = localState.courtOrderInfo
        newCourtOrderInfo.orderDate = val
        // date cannot be in the future

        setCourtOrderInformation(newCourtOrderInfo)
        emitValid()
      }
    )

    watch(
      () => localState.effectOfOrder,
      (val: string) => {
        const newCourtOrderInfo = localState.courtOrderInfo
        newCourtOrderInfo.effectOfOrder = val
        setCourtOrderInformation(newCourtOrderInfo)
        emitValid()
      }
    )

    onMounted(() => {
      const blankCourtOrder: CourtOrderIF = {
        courtName: '',
        courtRegistry: '',
        effectOfOrder: '',
        fileNumber: '',
        orderDate: ''
      }
      if (isEqual(localState.courtOrderInfo, blankCourtOrder)) {
        if (localState.requireCourtOrder && registrationType === APIRegistrationTypes.REPAIRERS_LIEN) {
          localState.effectOfOrder = 'Order directs the effective period of the Repairer\'s Lien be extended' +
            ' an additional 180 days.'
        }
      } else {
        // get unsavedChanges to reset it after court order setup
        const unsavedChanges = hasUnsavedChanges.value as boolean
        if (localState.courtOrderInfo.orderDate?.length > 10) {
          // convert back to local iso date string
          const orderDate = new Date(localState.courtOrderInfo.orderDate)
          localState.orderDate = localTodayDate(orderDate)
        } else {
          localState.orderDate = localState.courtOrderInfo.orderDate
        }
        localState.effectOfOrder = localState.courtOrderInfo.effectOfOrder
        localState.courtName = localState.courtOrderInfo.courtName
        localState.courtRegistry = localState.courtOrderInfo.courtRegistry
        localState.fileNumber = localState.courtOrderInfo.fileNumber
        // rerender date-picker
        localState.datePickerKey = Math.random()
        // reset unsaved changes to what it was before setting up court order
        setTimeout(() => {
          setUnsavedChanges(unsavedChanges)
        }, 100)
      }
    })

    return {
      modal,
      errors,
      valid,
      registrationType,
      APIRegistrationTypes,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
