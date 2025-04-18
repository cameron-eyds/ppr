import { nextTick } from 'vue'
import { useStore } from '@/store/store'
import { FeeSummary } from '@/composables/fees'
import type { RegistrationLengthI } from '@/composables/fees/interfaces'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { UIRegistrationTypes } from '@/enums'
import { createComponent } from './utils'
import type { StaffPaymentIF } from '@/interfaces'

const store = useStore()

const newRegStandard = [
  UIRegistrationTypes.SECURITY_AGREEMENT,
  UIRegistrationTypes.REPAIRERS_LIEN,
  UIRegistrationTypes.MARRIAGE_MH,
  UIRegistrationTypes.SALE_OF_GOODS,
  UIRegistrationTypes.LAND_TAX_LIEN,
  UIRegistrationTypes.MANUFACTURED_HOME_LIEN,
  UIRegistrationTypes.FORESTRY_CONTRACTOR_LIEN,
  UIRegistrationTypes.FORESTRY_CONTRACTOR_CHARGE,
  UIRegistrationTypes.FORESTRY_SUBCONTRACTOR_LIEN
]
const newRegMisc = [
  // miscelaneous registration cc
  UIRegistrationTypes.CARBON_TAX,
  UIRegistrationTypes.EXCISE_TAX,
  UIRegistrationTypes.FOREST,
  UIRegistrationTypes.INCOME_TAX,
  UIRegistrationTypes.INSURANCE_PREMIUM_TAX,
  UIRegistrationTypes.LOGGING_TAX,
  UIRegistrationTypes.MINERAL_LAND_TAX,
  UIRegistrationTypes.MOTOR_FUEL_TAX,
  UIRegistrationTypes.PROPERTY_TRANSFER_TAX,
  UIRegistrationTypes.PETROLEUM_NATURAL_GAS_TAX,
  UIRegistrationTypes.PROVINCIAL_SALES_TAX,
  UIRegistrationTypes.RURAL_PROPERTY_TAX,
  UIRegistrationTypes.SCHOOL_ACT,
  UIRegistrationTypes.SPECULATION_VACANCY_TAX,
  UIRegistrationTypes.TOBACCO_TAX,
  UIRegistrationTypes.OTHER,
  // miscelaneous registration other
  UIRegistrationTypes.LIEN_UNPAID_WAGES,
  UIRegistrationTypes.HERITAGE_CONSERVATION_NOTICE,
  UIRegistrationTypes.MANUFACTURED_HOME_NOTICE,
  UIRegistrationTypes.MAINTENANCE_LIEN,
  UIRegistrationTypes.PROCEEDS_CRIME_NOTICE
]
const newRegistrationTypes = [
  ...newRegStandard,
  ...newRegMisc
]
const renewRegistrationTypes = [
  UIRegistrationTypes.SECURITY_AGREEMENT,
  UIRegistrationTypes.REPAIRERS_LIEN,
  UIRegistrationTypes.SALE_OF_GOODS,
  UIRegistrationTypes.FORESTRY_CONTRACTOR_LIEN,
  UIRegistrationTypes.FORESTRY_CONTRACTOR_CHARGE,
  UIRegistrationTypes.FORESTRY_SUBCONTRACTOR_LIEN
]

describe('FeeSummary component tests', () => {
  let wrapper
  // registration length only effects the component when infinite/select years is selectable
  const registrationLength: RegistrationLengthI = {
    lifeInfinite: false,
    lifeYears: 0
  }
  beforeEach(async () => {
    await store.setLengthTrust({
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 3,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    await store.setStaffPayment({ isPriority: false } as StaffPaymentIF)
    // these props will be changed in each test
    wrapper = await createComponent(FeeSummary,
      {
        setFeeType: FeeSummaryTypes.NEW,
        setRegistrationLength: { ...registrationLength },
        setRegistrationType: newRegistrationTypes[0],
        setFeeOverride: null
      }
    )
  })

  for (let i = 0; i < newRegistrationTypes.length; i++) {
    it(`new registrations: ${newRegistrationTypes[i]}: renders with correct values`, async () => {
      expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
      wrapper = await createComponent(FeeSummary, {
        setFeeType: FeeSummaryTypes.NEW,
        setRegistrationLength: { ...registrationLength },
        setRegistrationType: newRegistrationTypes[i],
        setFeeOverride: null
      })
      expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.NEW)
      expect(wrapper.vm.registrationLength).toEqual(registrationLength)
      expect(wrapper.vm.registrationType).toBe(newRegistrationTypes[i])
      expect(wrapper.vm.feeLabel).toBe(newRegistrationTypes[i])

      const noFeeStandard = [UIRegistrationTypes.LAND_TAX_LIEN, UIRegistrationTypes.MANUFACTURED_HOME_LIEN]
      if ([...newRegMisc, ...noFeeStandard].includes(newRegistrationTypes[i])) {
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(0)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(0)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('Infinite Registration (default)')
        // check renders the same for non billable
        // await wrapper.setProps({ setFeeOverride: { feeAmount: 0, serviceFee: 4 } })
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(0)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(0)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('Infinite Registration (default)')
      } else if (newRegistrationTypes[i] === UIRegistrationTypes.REPAIRERS_LIEN) {
        expect(wrapper.vm.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(5)
        expect(wrapper.vm.totalAmount).toBe(6.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('180 Day Registration (default)')
      } else if (newRegistrationTypes[i] === UIRegistrationTypes.MARRIAGE_MH) {
        expect(wrapper.vm.feeSummary.feeAmount).toBe(10)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(10)
        expect(wrapper.vm.totalAmount).toBe(11.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('Infinite Registration (default)')
      } else {
        // standard selectable years / selectable infinite
        expect(wrapper.vm.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.feeSummary.quantity).toBe(0)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(1.5)
        expect(wrapper.vm.isComplete).toBe(false)
        expect(wrapper.vm.hintFee).toBe('Select registration length')
      }

      it(`${newRegistrationTypes[i]}: renders with correct values for infinite length`, async () => {
        // Set infinite
        wrapper = await createComponent(FeeSummary, {
          setFeeType: FeeSummaryTypes.NEW,
          setRegistrationLength: {
            setRegistrationLength: {
              lifeInfinite: true,
              lifeYears: 0
            }
          },
          setRegistrationType: newRegistrationTypes[i],
          setFeeOverride: null
        })
        await nextTick()

        expect(wrapper.vm.feeSummary.feeAmount).toBe(500)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(500)
        expect(wrapper.vm.totalAmount).toBe(501.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('Infinite Registration')
      })

      it(`${newRegistrationTypes[i]}: renders with correct values for 1 year length`, async () => {
        // Set infinite
        wrapper = await createComponent(FeeSummary, {
          setFeeType: FeeSummaryTypes.NEW,
          setRegistrationLength: {
            setRegistrationLength: {
              lifeInfinite: false,
              lifeYears: 1
            }
          },
          setRegistrationType: newRegistrationTypes[i],
          setFeeOverride: null
        })
        await nextTick()

        expect(wrapper.vm.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(5)
        expect(wrapper.vm.totalAmount).toBe(6.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('1 Year @ $5.00/year')
      })

      it(`${newRegistrationTypes[i]}: renders with correct values for 12 year length`, async () => {
        // Set infinite
        wrapper = await createComponent(FeeSummary, {
          setFeeType: FeeSummaryTypes.NEW,
          setRegistrationLength: {
            setRegistrationLength: {
              lifeInfinite: false,
              lifeYears: 12
            }
          },
          setRegistrationType: newRegistrationTypes[i],
          setFeeOverride: null
        })
        await nextTick()

        expect(wrapper.vm.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.feeSummary.quantity).toBe(12)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(60)
        expect(wrapper.vm.totalAmount).toBe(61.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('12 Years @ $5.00/year')
      })
      it(`${newRegistrationTypes[i]}: renders with correct values for Non Billable`, async () => {
        // Set infinite
        wrapper = await createComponent(FeeSummary, {
          setFeeType: FeeSummaryTypes.NEW,
          setRegistrationLength: { ...registrationLength },
          setRegistrationType: newRegistrationTypes[i],
          setFeeOverride: { feeAmount: 0, serviceFee: 2.5 }
        })
        await nextTick()

        expect(wrapper.vm.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.feeSummary.quantity).toBe(12)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(60)
        expect(wrapper.vm.totalAmount).toBe(61.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('12 Years @ $5.00/year')
      })

    })
  }

  for (let i = 0; i < newRegistrationTypes.length; i++) {
    it(`total discharge: ${newRegistrationTypes[i]}: renders with correct values`, async () => {
      wrapper = await createComponent(FeeSummary, {
        setFeeType: FeeSummaryTypes.DISCHARGE,
        setRegistrationLength: null,
        setRegistrationType: newRegistrationTypes[i]
      })
      expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
      expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.DISCHARGE)
      expect(wrapper.vm.registrationType).toBe(newRegistrationTypes[i])
      expect(wrapper.vm.feeLabel).toBe('Total Discharge')
      expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
      expect(wrapper.vm.feeSummary.quantity).toBe(1)
      expect(wrapper.vm.feeSummary.serviceFee).toBe(0)
      expect(wrapper.vm.totalFees).toBe(0)
      expect(wrapper.vm.totalAmount).toBe(0)
      expect(wrapper.vm.isComplete).toBe(true)
      expect(wrapper.vm.hintFee).toBe('')
    })
  }

  for (let i = 0; i < renewRegistrationTypes.length; i++) {
    it(`renewals: ${renewRegistrationTypes[i]}: renders with correct values`, async () => {
      expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
      wrapper = await createComponent(FeeSummary, {
        setFeeType: FeeSummaryTypes.RENEW,
        setRegistrationLength: { ...registrationLength },
        setRegistrationType: renewRegistrationTypes[i],
        setFeeOverride: null
      })
      await nextTick()
      expect(wrapper.vm.feeType).toBe(FeeSummaryTypes.RENEW)
      expect(wrapper.vm.registrationLength).toEqual(registrationLength)
      expect(wrapper.vm.registrationType).toBe(renewRegistrationTypes[i])
      expect(wrapper.vm.feeLabel).toBe('Registration Renewal')

      const noFeeStandard = [UIRegistrationTypes.LAND_TAX_LIEN, UIRegistrationTypes.MANUFACTURED_HOME_LIEN]
      if ([...newRegMisc, ...noFeeStandard].includes(renewRegistrationTypes[i])) {
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(0)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(0)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('Infinite Registration (default)')
        // check renders the same for non billable
        expect(wrapper.vm.feeSummary.feeAmount).toBe(0)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(0)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(0)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('Infinite Registration (default)')
      } else if (renewRegistrationTypes[i] === UIRegistrationTypes.REPAIRERS_LIEN) {
        expect(wrapper.vm.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(5)
        expect(wrapper.vm.totalAmount).toBe(6.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('180 Day Registration (default)')
      } else if (renewRegistrationTypes[i] === UIRegistrationTypes.MARRIAGE_MH) {
        expect(wrapper.vm.feeSummary.feeAmount).toBe(10)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(10)
        expect(wrapper.vm.totalAmount).toBe(11.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('Infinite Registration (default)')
      } else {
        // standard selectable years / selectable infinite
        expect(wrapper.vm.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.feeSummary.quantity).toBe(0)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(0)
        expect(wrapper.vm.totalAmount).toBe(1.5)
        expect(wrapper.vm.isComplete).toBe(false)
        expect(wrapper.vm.hintFee).toBe('Select registration renewal length')
      }

      it(`${renewRegistrationTypes[i]}: renders with correct values for infinite length`, async () => {
        // Set infinite
        wrapper = await createComponent(FeeSummary, {
          setFeeType: FeeSummaryTypes.NEW,
          setRegistrationLength: {
            setRegistrationLength: {
              lifeInfinite: true,
              lifeYears: 0
            }
          },
          setRegistrationType: renewRegistrationTypes[i],
          setFeeOverride: null
        })
        await nextTick()

        expect(wrapper.vm.feeSummary.feeAmount).toBe(500)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(500)
        expect(wrapper.vm.totalAmount).toBe(501.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('Infinite Registration')
      })

      it(`${renewRegistrationTypes[i]}: renders with correct values for 1 year length`, async () => {
        // Set infinite
        wrapper = await createComponent(FeeSummary, {
          setFeeType: FeeSummaryTypes.NEW,
          setRegistrationLength: {
            setRegistrationLength: {
              lifeInfinite: false,
              lifeYears: 1
            }
          },
          setRegistrationType: renewRegistrationTypes[i],
          setFeeOverride: null
        })
        await nextTick()

        expect(wrapper.vm.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.feeSummary.quantity).toBe(1)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(5)
        expect(wrapper.vm.totalAmount).toBe(6.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('1 Year @ $5.00/year')
      })

      it(`${renewRegistrationTypes[i]}: renders with correct values for 12 year length`, async () => {
        // Set infinite
        wrapper = await createComponent(FeeSummary, {
          setFeeType: FeeSummaryTypes.NEW,
          setRegistrationLength: {
            setRegistrationLength: {
              lifeInfinite: false,
              lifeYears: 12
            }
          },
          setRegistrationType: renewRegistrationTypes[i],
          setFeeOverride: null
        })
        await nextTick()

        expect(wrapper.vm.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.feeSummary.quantity).toBe(12)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(60)
        expect(wrapper.vm.totalAmount).toBe(61.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('12 Years @ $5.00/year')
      })
      it(`${renewRegistrationTypes[i]}: renders with correct values for Non Billable`, async () => {
        // Set infinite
        wrapper = await createComponent(FeeSummary, {
          setFeeType: FeeSummaryTypes.NEW,
          setRegistrationLength: { ...registrationLength },
          setRegistrationType: renewRegistrationTypes[i],
          setFeeOverride: { feeAmount: 0, serviceFee: 2.5 }
        })
        await nextTick()

        expect(wrapper.vm.feeSummary.feeAmount).toBe(5)
        expect(wrapper.vm.feeSummary.quantity).toBe(12)
        expect(wrapper.vm.feeSummary.serviceFee).toBe(1.5)
        expect(wrapper.vm.totalFees).toBe(60)
        expect(wrapper.vm.totalAmount).toBe(61.5)
        expect(wrapper.vm.isComplete).toBe(true)
        expect(wrapper.vm.hintFee).toBe('12 Years @ $5.00/year')
      })

    })
  }
})
