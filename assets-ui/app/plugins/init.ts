// plugins/init.ts
import { defineNuxtPlugin } from '#app'
import { fetchConfig, initLdClient, setAllFlagDefaults } from '@/utils'

export default defineNuxtPlugin(async (nuxtApp) => {
  await fetchConfig()

  if (import.meta.client && (window as any).ldClientId) {
    console.info('Initializing Launch Darkly...')
    await initLdClient()
  }

  if (import.meta.client && getFeatureFlag('sentry-enable')) {
    console.info('Initializing Sentry...')
    nuxtApp.$sentry.init({
      dsn: (window as any).sentryDsn
    })
  }

  if (process.env.VUE_APP_LOCAL_DEV === 'true') {
    setAllFlagDefaults(true)
  }
})