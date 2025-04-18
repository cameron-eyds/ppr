<template>
  <div
    id="mhr-describe-your-home"
    class="increment-sections"
  >
    <section
      id="mhr-make-model"
      class="mt-10"
    >
      <h2>Manufacturer, Make, and Model</h2>
      <p
        :class="['mt-2', isMhrManufacturerRegistration ? 'mb-3' : 'mb-6']"
        data-test-id="make-model-prompt"
      >
        <span v-html="manufacturerMakeModelPrompt" />
      </p>

      <ContactUsToggle
        v-if="isMhrManufacturerRegistration"
        help-text="If you require assistance with changes to your manufacturer information please contact us."
      />

      <ManufacturerMakeModel
        :validate="validateMakeModel"
        :class="{'border-error-left': validateMakeModel}"
      />
    </section>

    <section
      id="mhr-home-sections"
      class="mt-10"
    >
      <h2>Home Sections</h2>
      <p class="mt-2">
        Add the Serial Number and dimensions for each section of the home. You can include up to four
        sections in a home.
      </p>

      <HomeSections
        :validate="validateSections"
      />
    </section>

    <section
      id="mhr-home-certification"
      class="mt-10"
    >
      <h2>Home Certification</h2>
      <p
        class="mt-2"
        data-test-id="home-certification-prompt"
      >
        {{ homeCertificationPrompt }}
      </p>

      <HomeCertification
        :validate="validateCertification"
        :class="{'border-error-left': validateCertification}"
      />
    </section>


    <template v-if="!isMhrManufacturerRegistration">
      <section
        id="mhr-rebuilt-status"
        class="mt-10"
      >
        <h2>Rebuilt Status</h2>
        <p class="mt-2">
          If the home was rebuilt, include the description of the changes to the home
          (normally accompanied by a statutory declaration).
        </p>

        <RebuiltStatus
          class="mt-6"
          :validate="validateRebuilt"
          :class="{'border-error-left': validateRebuilt}"
        />
      </section>

      <section
        id="mhr-other-information"
        class="mt-10"
      >
        <h2>Other Information</h2>
        <p class="mt-2">
          Include any other relevant information about the home.
        </p>

        <OtherInformation
          class="mt-6"
          :validate="validateOther"
          :class="{'border-error-left': validateOther}"
        />
      </section>
    </template>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from 'vue'
import { useStore } from '@/store/store'
import {
  HomeCertification,
  HomeSections,
  ManufacturerMakeModel,
  RebuiltStatus,
  OtherInformation
} from '@/components/mhrRegistration/YourHome'
import { ContactUsToggle } from '@/components/common'
import { useMhrValidations } from '@/composables/mhrRegistration/useMhrValidations'
import { storeToRefs } from 'pinia'
import { ManufacturerMakeModelPrompt, HomeCertificationPrompt } from '@/resources/mhr-registration'

export default defineComponent({
  name: 'YourHome',
  components: {
    HomeCertification,
    HomeSections,
    ManufacturerMakeModel,
    RebuiltStatus,
    OtherInformation,
    ContactUsToggle
  },
  props: {},
  setup () {
    const {
      getMhrRegistrationValidationModel,
      isMhrManufacturerRegistration,
      isRoleManufacturer
    } = storeToRefs(useStore())

    const {
      MhrCompVal,
      MhrSectVal,
      getSectionValidation,
      scrollToInvalid
    } = useMhrValidations(toRefs(getMhrRegistrationValidationModel.value))

    const localState = reactive({
      validateMakeModel: computed(() => {
        return getSectionValidation(MhrSectVal.YOUR_HOME_VALID, MhrCompVal.MAKE_MODEL_VALID)
      }),
      validateSections: computed(() => {
        return getSectionValidation(MhrSectVal.YOUR_HOME_VALID, MhrCompVal.HOME_SECTION_VALID)
      }),
      validateCertification: computed(() => {
        return getSectionValidation(MhrSectVal.YOUR_HOME_VALID, MhrCompVal.HOME_CERTIFICATION_VALID)
      }),
      validateRebuilt: computed(() => {
        return getSectionValidation(MhrSectVal.YOUR_HOME_VALID, MhrCompVal.REBUILT_STATUS_VALID)
      }),
      validateOther: computed(() => {
        return getSectionValidation(MhrSectVal.YOUR_HOME_VALID, MhrCompVal.OTHER_VALID)
      }),
      manufacturerMakeModelPrompt: computed(() : string => {
        return isRoleManufacturer.value
          ? ManufacturerMakeModelPrompt.manufacturer
          : ManufacturerMakeModelPrompt.staff
      }),
      homeCertificationPrompt: computed(() : string => {
        return isRoleManufacturer.value
          ? HomeCertificationPrompt.manufacturer
          : HomeCertificationPrompt.staff
      })
    })

    const scrollOnValidationUpdates = () => {
      scrollToInvalid(MhrSectVal.YOUR_HOME_VALID, 'mhr-describe-your-home')
    }

    watch(() => localState, () => {
      setTimeout(scrollOnValidationUpdates, 300)
    }, { deep: true })

    return {
      MhrCompVal,
      MhrSectVal,
      getSectionValidation,
      isMhrManufacturerRegistration,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme';
</style>
