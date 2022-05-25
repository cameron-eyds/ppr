
import { getDescriptiveUserRole } from '@/utils'

describe('Roles helper utility methods', () => { 

    it('should properly construct descriptive role names from authRoles', () => {

        expect(getDescriptiveUserRole(['ppr_staff'])).toBe('STAFF_PPR')

        expect(getDescriptiveUserRole(['staff', 'helpdesk'])).toBe('STAFF_PPR')

        expect(getDescriptiveUserRole(['staff', 'ppr'])).toBe('STAFF_PPR')
        expect(getDescriptiveUserRole(['staff', 'mhr'])).toBe('STAFF_MHR')
        expect(getDescriptiveUserRole(['sbc', 'ppr', 'mhr'])).toBe('STAFF_PPR_MHR')

        expect(getDescriptiveUserRole(['ppr'])).toBe('CLIENT_PPR')
        expect(getDescriptiveUserRole(['mhr'])).toBe('CLIENT_MHR')
        expect(getDescriptiveUserRole(['ppr', 'mhr'])).toBe('CLIENT_PPR_MHR')
    })
 })