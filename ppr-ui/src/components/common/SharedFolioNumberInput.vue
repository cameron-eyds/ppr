<template>
  <v-form id="folio-number-form" ref="folioForm" v-model="folioFormValid">
    <v-text-field
      filled
      id="folio-number-textfield"
      label="Folio Number (Optional)"
      :value="folioNumber"
      :rules="folioNumberRules"
      :disabled="disabled"
      @input="emitFolioNumber($event)"
      @focus="emitFocus($event)"
      autocomplete="chrome-off"
      :name="Math.random()"
    />
  </v-form>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, ref, watch } from '@vue/composition-api'
// eslint-disable-next-line no-unused-vars
import { FormIF } from '@/interfaces'

export default defineComponent({
  name: 'SharedFolioNumberInput',
  emits: ['valid', 'focus', 'emitFolioNumber'],
  props: {
    validate: {
      type: Boolean,
      default: false
    },
    folioNumber: {
      type: String,
      default: null
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const folioForm = ref(null)

    const localState = reactive({
      folioFormValid: false,
      folioNumberRules: computed((): Array<Function> => {
        return [
          v => (!v || !props.validate || v.length <= 50) || 'Cannot exceed 50 characters' // maximum character count
        ]
      })
    })

    /**
     * Public method that can be used through $refs from a parent
     * component to reset the folio form.
     */
    const resetFolioNumber = (): void => {
      (context.refs.folioForm as FormIF).reset()
    }

    /**
     * Public method that can be used through $refs from a parent
     * component to reset folio number validation.
     */
    const resetFolioNumberValidation = (): void => {
      (context.refs.folioForm as FormIF).resetValidation()
    }

    /**
     * Public method that can be used through $refs from a parent
     * component to trigger folio number validation.
     * @returns True if form is valid and False if not
     */
    const validateFolioNumber = (): boolean => {
      return (context.refs.folioForm as FormIF).validate()
    }

    /** Emits an event indicating whether or not this component is valid. */
    const emitValid = (): void => {
      context.emit('valid', localState.folioFormValid)
    }

    /** Emits an event indicating whether or not this component is focused. */
    const emitFocus = (val: boolean): void => {
      context.emit('focus', val)
    }

    /** Emits an event to update the Folio Number. */
    const emitFolioNumber = (val: string): void => {
      context.emit('emitFolioNumber', val)
    }

    /** Prompt the field validations. */
    watch(() => [localState.folioFormValid, props.validate], (): void => {
      if (props.validate) {
        validateFolioNumber()
        emitValid()
      }
    })

    return {
      folioForm,
      emitValid,
      emitFocus,
      emitFolioNumber,
      resetFolioNumber,
      resetFolioNumberValidation,
      validateFolioNumber,
      ...toRefs(localState)
    }
  }
})
</script>
