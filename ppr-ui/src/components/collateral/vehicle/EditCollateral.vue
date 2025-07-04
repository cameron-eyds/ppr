<template>
  <div
    id="edit-vehicle"
    class="bg-white py-8"
    :class="{ 'border-error-left': showErrorBar && activeIndex === -1 }"
  >
    <v-expand-transition>
      <v-row no-gutters>
        <v-col cols="3">
          <label
            class="add-vehicle-header generic-label pl-2"
            :class="{ 'error-text': invalidSection }"
          >
            <span
              v-if="activeIndex === -1"
              :class="registrationFlowType === RegistrationFlowType.AMENDMENT ? '' : 'pl-4'"
            >
              Add Vehicle
            </span>
            <span
              v-else
              class="ml-n3"
            >
              <span
                v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                  && (!currentVehicle.action || currentVehicle.action !== ActionTypes.ADDED)"
              >
                Amend
              </span>
              <span v-else>Edit</span>
              Vehicle</span>
          </label>
        </v-col>
        <v-col
          cols="9"
          :class="registrationFlowType === RegistrationFlowType.AMENDMENT ? '' : 'pr-6'"
        >
          <v-form
            ref="vehicleForm"
            class="vehicle-form"
          >
            <v-row no-gutters class="pb-[5px]">
              <v-col v-if="mustHaveManufacturedHomeCollateral()">
                <v-text-field
                  id="txt-type"
                  variant="filled"
                  color="primary"
                  label="Vehicle Type"
                  model-value="Manufactured Home (MH)"
                  readonly
                  persistent-hint
                />
              </v-col>
              <v-col v-else-if="excludesManufacturedHomeCollateral() && !isRlTransition">
                <v-select
                  id="txt-type-drop"
                  v-model="currentVehicle.type"
                  class="vehicle-type-select"
                  :items="vehicleTypesNoMH"
                  item-title="text"
                  variant="filled"
                  color="primary"
                  label="Vehicle Type"
                  :error-messages="
                    errors.type.message ? errors.type.message : ''
                  "
                  @update:model-value="resetSerialError()"
                />
              </v-col>
              <v-col v-else>
                <v-select
                  id="txt-type-drop"
                  v-model="currentVehicle.type"
                  class="vehicle-type-select"
                  :items="vehicleTypes"
                  item-title="text"
                  variant="filled"
                  color="primary"
                  label="Vehicle Type"
                  :error-messages="
                    errors.type.message ? errors.type.message : ''
                  "
                  @update:model-value="resetSerialError()"
                />
              </v-col>
            </v-row>
            <v-row
              v-if="currentVehicle.type === 'MH'"
              no-gutters
              class="py-[5px]"
            >
              <v-col>
                <v-text-field
                  id="txt-man"
                  v-model="currentVehicle.manufacturedHomeRegistrationNumber"
                  class="mh-num-input"
                  variant="filled"
                  color="primary"
                  label="Manufactured Home Registration Number"
                  :error-messages="
                    errors.manufacturedHomeRegistrationNumber.message
                      ? errors.manufacturedHomeRegistrationNumber.message
                      : ''
                  "
                  persistent-hint
                  @keyup="onBlur('manufacturedHomeRegistrationNumber')"
                />
              </v-col>
            </v-row>
            <v-row
              no-gutters
              class="py-[5px]"
            >
              <v-col>
                <v-text-field
                  id="txt-serial"
                  v-model="currentVehicle.serialNumber"
                  class="serial-number"
                  variant="filled"
                  color="primary"
                  :label="getSerialLabel"
                  :disabled="getSerialDisabled"
                  :error-messages="
                    errors.serialNumber.message
                      ? errors.serialNumber.message
                      : ''
                  "
                  persistent-hint
                  @keyup="onBlur('serialNumber')"
                />
              </v-col>
            </v-row>
            <v-row
              no-gutters
              class="py-[5px]"
            >
              <v-col cols="4">
                <v-text-field
                  id="txt-years"
                  v-model="currentVehicle.year"
                  variant="filled"
                  color="primary"
                  label="Year (Optional)"
                  hint="YYYY"
                  persistent-hint
                  :error-messages="
                    errors.year.message ? errors.year.message : ''
                  "
                  @blur="onBlur('year')"
                />
              </v-col>
            </v-row>
            <v-row
              no-gutters
              class="py-[5px]"
            >
              <v-col>
                <v-text-field
                  id="txt-make"
                  v-model="currentVehicle.make"
                  variant="filled"
                  color="primary"
                  label="Make"
                  persistent-hint
                  :error-messages="
                    errors.make.message ? errors.make.message : ''
                  "
                  @keyup="onBlur('make')"
                />
              </v-col>
            </v-row>
            <v-row
              no-gutters
              class="py-[5px]"
            >
              <v-col>
                <v-text-field
                  id="txt-model"
                  v-model="currentVehicle.model"
                  variant="filled"
                  color="primary"
                  label="Model"
                  persistent-hint
                  :error-messages="
                    errors.model.message ? errors.model.message : ''
                  "
                  @keyup="onBlur('model')"
                />
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <div class="form__row form__btns">
                  <v-btn
                    id="remove-btn-collateral"
                    size="large"
                    variant="outlined"
                    color="error"
                    :disabled="activeIndex === -1"
                    class="remove-btn float-left"
                    @click="removeVehicle()"
                  >
                    <span
                      v-if="registrationFlowType === RegistrationFlowType.AMENDMENT
                        && currentIndex !== -1
                        && (!currentVehicle.action || currentVehicle.action !== ActionTypes.ADDED)"
                    >
                      Delete
                    </span>
                    <span v-else>Remove</span>
                  </v-btn>

                  <span class="float-right">
                    <v-btn
                      id="done-btn-collateral"
                      size="large"
                      class="ml-auto mr-2"
                      color="primary"
                      @click="onSubmitForm()"
                    >
                      Done
                    </v-btn>

                    <v-btn
                      id="cancel-btn-collateral"
                      size="large"
                      variant="outlined"
                      color="primary"
                      @click="resetFormAndData(true)"
                    >
                      Cancel
                    </v-btn>
                  </span>
                </div>
              </v-col>
            </v-row>
          </v-form>
        </v-col>
      </v-row>
    </v-expand-transition>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, reactive, computed, toRefs } from 'vue'
import { useCollateralValidation, useVehicle } from './factories'
import { APIVehicleTypes } from '@/enums'
import { storeToRefs } from 'pinia'
import { useStore } from '@/store/store'

export default defineComponent({
  props: {
    activeIndex: {
      type: Number,
      default: -1
    },
    invalidSection: {
      type: Boolean,
      default: false
    },
    setShowErrorBar: {
      type: Boolean,
      default: false
    }
  },
  emits: ['resetEvent'],
  setup (props, context) {
    const {
      currentVehicle,
      vehicleTypes,
      vehicleTypesNoMH,
      getSerialLabel,
      getSerialDisabled,
      registrationFlowType,
      getVehicle,
      ActionTypes,
      RegistrationFlowType,
      resetFormAndData,
      removeVehicle,
      addVehicle,
      mustHaveManufacturedHomeCollateral,
      excludesManufacturedHomeCollateral
    } = useVehicle(props, context)
    const {
      errors,
      validateInput,
      validateSerial,
      validateCollateralForm,
      resetSerialError
    } = useCollateralValidation()
    const { isRlTransition } = storeToRefs(useStore())

    const localState = reactive({
      currentIndex: computed((): number => {
        return props.activeIndex
      }),
      showErrorBar: computed((): boolean => {
        return props.setShowErrorBar
      })
    })

    onMounted(() => {
      getVehicle()
      if (currentVehicle.value.manufacturedHomeRegistrationNumber === 'NR') {
        currentVehicle.value.manufacturedHomeRegistrationNumber = ''
      }
      if (mustHaveManufacturedHomeCollateral()) {
        // set the current vehicle type to motor home
        currentVehicle.value.type = APIVehicleTypes.MANUFACTURED_HOME
      }
    })

    const onSubmitForm = async () => {
      const isValid = await validateCollateralForm(currentVehicle.value)
      if (!isValid) {
        return
      }

      addVehicle()
    }

    const onBlur = fieldname => {
      if (fieldname === 'serialNumber') {
        validateSerial(currentVehicle.value)
      } else {
        validateInput(fieldname, currentVehicle.value[fieldname])
        // remove serial number validation if manufactured home number entered
        if (fieldname === 'manufacturedHomeRegistrationNumber') {
          validateSerial(currentVehicle.value)
        }
      }
    }

    return {
      onSubmitForm,
      resetFormAndData,
      removeVehicle,
      onBlur,
      errors,
      currentVehicle,
      vehicleTypes,
      vehicleTypesNoMH,
      getSerialLabel,
      getSerialDisabled,
      registrationFlowType,
      RegistrationFlowType,
      ActionTypes,
      mustHaveManufacturedHomeCollateral,
      excludesManufacturedHomeCollateral,
      resetSerialError,
      isRlTransition,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';d

.container .v-card > .border-error-left {
  border-top-left-radius: unset;
  border-bottom-left-radius: unset;
  margin-left: 0;
}

.border-over {
  margin-left: 25px;
}
</style>
