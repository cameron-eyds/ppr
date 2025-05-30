<template>
  <v-container class="pa-0 party-summary flat">
    <BasePartySummary
      :set-headers="securedPartyHeaders"
      :set-items="securedParties"
      :set-options="securedPartyOptions"
      @trigger-no-data-action="goToParties()"
    />
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  reactive,
  computed,
  toRefs
} from 'vue'
import { useStore } from '@/store/store'
import { BasePartySummary } from '@/components/parties/summaries'
import type { AddPartiesIF, PartySummaryOptionsI } from '@/interfaces'
import { useRouter } from 'vue-router'
import { partyTableHeaders } from '@/resources'
import { RegistrationFlowType } from '@/enums'
import { storeToRefs } from 'pinia'
import { useSecuredParty } from '@/composables/parties'

export default defineComponent({
  name: 'SecuredPartySummary',
  components: {
    BasePartySummary
  },
  props: {
    setEnableNoDataAction: {
      type: Boolean,
      default: false
    },
    setHeader: {
      type: String,
      default: ''
    }
  },
  setup (props) {
    const router = useRouter()
    const { setAddSecuredPartiesAndDebtors } = useStore()
    const {
      // Getters
      getAddSecuredPartiesAndDebtors,
      getRegistrationFlowType
    } = storeToRefs(useStore())
    const { isSecuredPartiesRestricted } = useSecuredParty()
    const parties: AddPartiesIF = getAddSecuredPartiesAndDebtors.value

    const localState = reactive({
      securedParties: computed(function () {
        if (getRegistrationFlowType.value === RegistrationFlowType.NEW) {
          if (isSecuredPartiesRestricted.value && parties?.securedParties?.length > 1) {
            return []
          }
        }
        return parties.securedParties
      }),
      securedPartyHeaders: computed(function () {
        return [...partyTableHeaders]
      }),
      securedPartyOptions: {
        header: props.setHeader,
        iconColor: 'darkBlue',
        iconImage: 'mdi-account',
        isDebtorSummary: false,
        enableNoDataAction: props.setEnableNoDataAction,
        isRegisteringParty: false
      } as PartySummaryOptionsI
    })

    const goToParties = (): void => {
      parties.showInvalid = true
      setAddSecuredPartiesAndDebtors(parties)
      router.push({ path: '/new-registration/add-securedparties-debtors' })
    }

    return {
      goToParties,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
