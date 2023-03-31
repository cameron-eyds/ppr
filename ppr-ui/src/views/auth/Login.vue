<template>
  <sbc-login :redirectUrl="redirectUrl" />
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from 'vue'
// Common Component
import { SbcLogin } from '@/sbc-common-components/components'
import { useRoute } from 'vue-router'

/**
 * Operation:
 * 1. When this component is first loaded (ie, we are not authenticated) then the
 *    SbcLogin component will redirect us to log in.
 */
export default defineComponent({
  name: 'Login',
  components: {
    SbcLogin
  },
  setup (props, context) {
    const route = useRoute()

    const localState = reactive({
      redirectUrl: computed(() => {
        return (route.query.redirect as string)
      })
    })

    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
</style>
