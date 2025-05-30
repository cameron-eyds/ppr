<template>
  <div>
    <section
      id="mhr-unit-note-doc-id"
      class="mt-10"
    >
      <DocumentId
        :document-id="unitNoteDocumentId"
        :section-number="1"
        :content="{
          title: 'Document ID',
          description: 'Enter the 8-digit Document ID number.',
          sideLabel: 'Document ID'
        }"
        :validate="validate"
        @set-store-property="handleStoreUpdate('documentId', $event)"
        @is-valid="handleComponentValid(MhrCompVal.DOC_ID_VALID, $event)"
      />
    </section>

    <section
      id="mhr-unit-note-remarks"
      class="mt-10"
    >
      <Remarks
        :unit-note-remarks="unitNoteRemarks"
        :additional-remarks="additionalRemarks"
        :show-additional-remarks-checkbox="isNoticeOfTaxSale"
        :section-number="2"
        :content="remarksContent"
        :is-required="isRemarksRequired"
        :validate="validate"
        @set-store-property="handleStoreUpdate($event.key, $event.value)"
        @is-valid="handleComponentValid(MhrCompVal.REMARKS_VALID, $event)"
      />
    </section>

    <section
      id="mhr-unit-note-person-giving-notice"
      class="mt-10"
    >
      <ContactInformation
        :contact-info="unitNoteGivingNoticeParty"
        :section-number="3"
        :content="contactInfoContent"
        :validate="validate"
        :is-hidden="hasNoPersonGivingNotice"
        enable-combined-name-validation
        hide-party-search
        hide-delivery-address
        @set-store-property="handleStoreUpdate('givingNoticeParty', $event)"
        @is-valid="handleComponentValid(MhrCompVal.PERSON_GIVING_NOTICE_VALID, $event)"
      >
        <template
          v-if="isPersonGivingNoticeOptional()"
          #preForm
        >
          <v-checkbox
            id="no-person-giving-notice-checkbox"
            v-model="hasNoPersonGivingNotice"
            class="no-person-giving-notice-checkbox mb-8"
            :label="hasNoPersonGivingNoticeText"
            hide-details
            density="compact"
            :ripple="false"
          />
        </template>
      </ContactInformation>
    </section>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch, onMounted } from 'vue'
import { UnitNotesInfo } from '@/resources/unitNotes'
import { UnitNoteDocTypes } from '@/enums'
import { useStore } from '@/store/store'
import { storeToRefs } from 'pinia'
import type { ContactInformationContentIF, UnitNoteIF } from '@/interfaces'
import { useMhrUnitNote, useMhrValidations } from '@/composables'
import { MhrCompVal, MhrSectVal } from '@/composables/mhrRegistration/enums'
import { DocumentId, Remarks, ContactInformation } from '@/components/common'
import {
  personGivingNoticeContent, collectorInformationContent, remarksContent,
  hasNoPersonGivingNoticeText
} from '@/resources'

export default defineComponent({
  name: 'UnitNoteAdd',
  components: {
    DocumentId,
    Remarks,
    ContactInformation
  },
  props: {
    validate: {
      type: Boolean,
      default: false
    },
    docType: {
      type: String as () => UnitNoteDocTypes,
      default: UnitNoteDocTypes.NOTICE_OF_CAUTION
    }
  },
  emits: ['isValid'],
  setup (props, { emit }) {
    const {
      setMhrUnitNoteProp
    } = useStore()

    const {
      getMhrUnitNote,
      getMhrUnitNoteValidation
    } = storeToRefs(useStore())

    const {
      getValidation,
      setValidation
    } = useMhrValidations(toRefs(getMhrUnitNoteValidation.value))

    const {
      isPersonGivingNoticeOptional,
      isCancelUnitNote
    } = useMhrUnitNote()

    const localState = reactive({
      unitNoteInfo: UnitNotesInfo[props.docType],
      isUnitNoteValid: computed((): boolean =>
        getValidation(MhrSectVal.UNIT_NOTE_VALID, MhrCompVal.DOC_ID_VALID) &&
        getValidation(MhrSectVal.UNIT_NOTE_VALID, MhrCompVal.REMARKS_VALID) &&
        getValidation(MhrSectVal.UNIT_NOTE_VALID, MhrCompVal.PERSON_GIVING_NOTICE_VALID)
      ),
      contactInfoContent: computed((): ContactInformationContentIF =>
        [UnitNoteDocTypes.NOTICE_OF_TAX_SALE, UnitNoteDocTypes.NOTICE_OF_REDEMPTION].includes(props.docType)
          ? collectorInformationContent
          : personGivingNoticeContent
      ),
      isNoticeOfTaxSale: computed((): boolean => props.docType === UnitNoteDocTypes.NOTICE_OF_TAX_SALE),
      hasNoPersonGivingNotice: props.docType === UnitNoteDocTypes.DECAL_REPLACEMENT ||
        (getMhrUnitNote.value as UnitNoteIF).hasNoPersonGivingNotice || false,

      // Remarks
      unitNoteRemarks: (getMhrUnitNote.value as UnitNoteIF).remarks || '',
      additionalRemarks: (getMhrUnitNote.value as UnitNoteIF).additionalRemarks,
      remarksContent: computed(() => {
        // update the side label for Cancel Note only
        if (isCancelUnitNote.value) {
          remarksContent.sideLabel = remarksContent.sideLabelCancelNote
        }
        return remarksContent
      }),
      isRemarksRequired: computed((): boolean => props.docType === UnitNoteDocTypes.PUBLIC_NOTE),

      // Document Id
      unitNoteDocumentId: computed(() => (getMhrUnitNote.value as UnitNoteIF).documentId || ''),

      // Person Giving Notice
      unitNoteGivingNoticeParty: (getMhrUnitNote.value as UnitNoteIF).givingNoticeParty || {}
    })

    const handleComponentValid = (component: MhrCompVal, isValid: boolean) => {
      setValidation(MhrSectVal.UNIT_NOTE_VALID, component, isValid)
    }

    const handleStoreUpdate = (key: string, val) => {
      setMhrUnitNoteProp({ key, value: val })
    }

    watch(() => localState.hasNoPersonGivingNotice, (val) => {
      setValidation(MhrSectVal.UNIT_NOTE_VALID, MhrCompVal.PERSON_GIVING_NOTICE_VALID, val)
      handleStoreUpdate('hasNoPersonGivingNotice', val)
    })

    watch(() => [localState.isUnitNoteValid, props.validate], () => {
      emit('isValid', localState.isUnitNoteValid)
    })

    onMounted(() => {
      if(props.docType === UnitNoteDocTypes.DECAL_REPLACEMENT) {
        setValidation(
          MhrSectVal.UNIT_NOTE_VALID, MhrCompVal.PERSON_GIVING_NOTICE_VALID,
          localState.hasNoPersonGivingNotice
        )
        handleStoreUpdate('hasNoPersonGivingNotice', localState.hasNoPersonGivingNotice)
      }
    })

    return {
      personGivingNoticeContent,
      MhrCompVal,
      handleStoreUpdate,
      handleComponentValid,
      isPersonGivingNoticeOptional,
      hasNoPersonGivingNoticeText,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>

:deep(.no-person-giving-notice-checkbox) {

  .v-label {
    margin-left: 7px;
  }

}
</style>
