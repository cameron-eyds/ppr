<template>
  <v-card
    id="general-collateral"
    :class="{ 'border-error-left': showErrorComponent }"
    class="pa-4"
    flat
  >
    <v-row
      no-gutters
      class="py-6"
    >
      <v-col
        cols="3"
        class="generic-label pl-2"
      >
        General Collateral
      </v-col>
      <v-col
        cols="9"
      >
        <WysiwygEditor
          place-holder-text="Description of General Collateral"
          :editor-content="newDesc"
          @emit-editor-content="newDesc = $event"
        />

        <p class="summary-text mt-8">
          Note: If you are pasting text,
          <strong>we recommend pasting plain text</strong>
          to avoid formatting and font issues with PDF and printed
          registrations. If you have pasted text other than plain text, verify
          that your documents are correct. If they are not correct, they will
          need to be amended.
        </p>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  toRefs,
  watch,
  onMounted,
  computed
} from 'vue'
import { useStore } from '@/store/store'
// local
import { APIRegistrationTypes, RegistrationFlowType } from '@/enums'
import type { GeneralCollateralIF } from '@/interfaces'
import { storeToRefs } from 'pinia'

import { WysiwygEditor } from '@/components/common'

export default defineComponent({
  name: 'GenColEdit',
  components: {
    WysiwygEditor
  },
  props: {
    showInvalid: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const { setGeneralCollateral } = useStore()
    const {
      getRegistrationType,
      getGeneralCollateral,
      getRegistrationFlowType,
    } = storeToRefs(useStore())

    const generalCollateralDefaultValue = (): string => {
      switch (getRegistrationType.value.registrationTypeAPI) {
        case APIRegistrationTypes.CARBON_TAX:
        case APIRegistrationTypes.EXCISE_TAX:
        case APIRegistrationTypes.INCOME_TAX:
        case APIRegistrationTypes.INSURANCE_PREMIUM_TAX:
        case APIRegistrationTypes.LOGGING_TAX:
        case APIRegistrationTypes.MOTOR_FUEL_TAX:
        case APIRegistrationTypes.PROVINCIAL_SALES_TAX:
        case APIRegistrationTypes.TOBACCO_TAX:
        case APIRegistrationTypes.SPECULATION_VACANCY_TAX:
            return 'All the debtor’s present and after acquired personal property, including but not restricted to machinery, equipment, furniture, fixtures and receivables.' // eslint-disable-line
        case APIRegistrationTypes.LIEN_UNPAID_WAGES:
          return 'All the personal property of the debtor, including money due or accruing due'
      }
    }

    const localState = reactive({
      newDesc: getGeneralCollateral.value[0]?.description || generalCollateralDefaultValue() || '',
      generalCollateral: computed((): GeneralCollateralIF[] => {
        return (getGeneralCollateral.value as GeneralCollateralIF[]) || []
      }),
      showErrorComponent: computed((): boolean => {
        return props.showInvalid
      })
    })

    onMounted(() => {
      if (getRegistrationFlowType.value === RegistrationFlowType.NEW) {
        if (localState.generalCollateral.length > 0) {
          localState.newDesc = localState.generalCollateral[0].description
        }
      }
    })

    watch(
      () => localState.newDesc,
      (val: string) => {
        if (getRegistrationFlowType.value === RegistrationFlowType.NEW) {
          if (val) {
            setGeneralCollateral([{ description: val }])
          } else {
            setGeneralCollateral([])
          }
        }
      }, { immediate: true }
    )

    watch(
      () => localState.generalCollateral,
      (val: GeneralCollateralIF[]) => {
        if (getRegistrationFlowType.value === RegistrationFlowType.NEW) {
          if (val.length > 0 && val[0].description !== localState.newDesc) {
            localState.newDesc = val[0].description
          }
        }
      }
    )

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
