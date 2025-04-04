<template>
  <div id="service-agreement">
    <!-- download service agreement button -->
    <v-btn
      variant="outlined"
      color="primary"
      class="mt-8"
      :ripple="false"
      data-test-id="download-agreement-btn"
      @click="downloadServiceAgreement"
    >
      <img
        alt=""
        src="@/assets/svgs/pdf-icon-blue.svg"
      >
      <span class="pl-1">Download Qualified Suppliers' Agreement</span>
    </v-btn>

    <!-- service agreement preview container -->
    <v-card
      v-if="serviceAgreementUrl"
      flat
      class="mt-10 scroll-container"
    >
      <VuePdfEmbed :source="serviceAgreementUrl" />
    </v-card>
    <div
      v-else
      class="loading-spinner"
    >
      <v-progress-circular
        color="primary"
        size="30"
        indeterminate
      />
    </div>

    <!-- service agreement confirmation -->
    <v-card
      flat
      class="mt-5 pa-8"
      :class="{'border-error-left': showQsSaConfirmError}"
    >
      <v-checkbox
        v-model="serviceAgreementConfirm"
        class="pa-0"
        color="primary"
        hide-details
      >
        <template #label>
          <span
            :class="{ 'error-text': showQsSaConfirmError }"
            class="mt-2"
          >
            I have read, understood and agree to the terms and conditions of the Qualified Suppliers’ Agreement
            for the Manufactured Home Registry.
          </span>
        </template>
      </v-checkbox>
    </v-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, reactive, toRefs, watch } from 'vue'
import { useUserAccess } from '@/composables'
import { getQsServiceAgreements } from '@/utils/mhr-api-helper'
import { useStore } from '@/store/store'
import VuePdfEmbed from 'vue-pdf-embed'
import { storeToRefs } from 'pinia'

export default defineComponent({
  name: 'ServiceAgreement',
  components: { VuePdfEmbed },
  props: { validate: { type: Boolean, default: false } },
  setup (props) {
    const { setMhrQsValidation } = useStore()
    const { getMhrUserAccessValidation } = storeToRefs(useStore())
    const { downloadServiceAgreement } = useUserAccess()

    const localState = reactive({
      showQsSaConfirmError: false,
      serviceAgreementUrl: '',
      serviceAgreementConfirm: getMhrUserAccessValidation.value?.qsSaConfirmValid
    })

    onMounted(async () => {
      // Get the service agreement pdf url for preview
      const serviceAgreementBlob = await getQsServiceAgreements()
      localState.serviceAgreementUrl = URL.createObjectURL(serviceAgreementBlob)
    })

    watch(() => localState.serviceAgreementConfirm, (val: boolean) => {
      localState.showQsSaConfirmError = props.validate && !val
      setMhrQsValidation({ key: 'qsSaConfirmValid', value: val })
    })

    watch(() => props.validate, (val: boolean) => {
      localState.showQsSaConfirmError = val && !getMhrUserAccessValidation.value?.qsSaConfirmValid
    })

    return {
      downloadServiceAgreement,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.loading-spinner {
  display: flex;
  justify-content: center;
  align-items: center;
}

:deep(.vue-pdf-embed) {
  background-color: $gray1 !important;

  .annotationLayer {
    margin-top: 8px !important;
  }
}

:deep(.v-checkbox .v-selection-control) {
  display: flex;
  align-items: flex-start;
  word-break: break-word;
}
</style>
