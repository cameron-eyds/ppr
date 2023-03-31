// Core Libraries
import 'core-js/stable' // to polyfill ECMAScript features
import 'regenerator-runtime/runtime' // to use transpiled generator functions
import 'moment'
import * as Sentry from '@sentry/vue'
import { BrowserTracing } from '@sentry/tracing'

// Local
import App from '@/App.vue'
import { createVueRouter } from '@/router'
import store from '@/store'
import { createApp } from 'vue'
// import { fetchConfig, initLdClient } from '@/utils'
import vuetify from './plugins/vuetify'

// Vue Libraries
// import Vue from 'vue'
// import Vuetify from './plugins/vuetify'
import Vuelidate from 'vuelidate'
// import VueCompositionApi from 'vue'
// import { getVueRouter } from '@/router'
// import { getVuexStore } from '@/store'
// import Affix from 'vue-affix'
// import * as Sentry from '@sentry/browser'
// import * as Integrations from '@sentry/integrations'
// import { TiptapVuetifyPlugin } from 'tiptap-vuetify'

// Styles
// NB: order matters - do not change
// import '@mdi/font/css/materialdesignicons.min.css' // ensure you are using css-loader
import '@/assets/styles/base.scss'
import '@/assets/styles/layout.scss'
import '@/assets/styles/overrides.scss'
// import 'vuetify/styles'

// tiptap editor
// import 'tiptap-vuetify/dist/main.css'

// Base App
// import App from './App.vue'

// Helpers
import { getFeatureFlag, fetchConfig, initLdClient, isSigningIn, isSigningOut } from '@/utils'
import KeycloakService from '@/sbc-common-components/services/keycloak.services'

// import { ExecutorBusinessIcon, ExecutorPersonIcon, HomeLocationIcon, HomeOwnersIcon } from './assets/svgs/index'

// get rid of "element implicitly has an 'any' type..."
declare const window: any

// Vue.config.productionTip = false

// Vue.use(VueCompositionApi)
// Vue.use(Vuetify)
// Vue.use(Affix)
// Vue.use(Vuelidate)
// const vuetify = new Vuetify()
// use this package's plugin
// Vue.use(TiptapVuetifyPlugin, {
//   // the next line is important! You need to provide the Vuetify Object to this place.
//   vuetify, // same as "vuetify: vuetify"
//   // optional, default to 'md' (default vuetify icons before v2.0.0)
//   iconsGroup: 'mdi'
// })

// main code
async function start () {
  // fetch config from environment and API
  // must come first as inits below depend on config
  await fetchConfig()
  console.log('Config Fetched')

  const router = createVueRouter()
  console.log('Router Created')

  const app = createApp(App)
  console.log('App Created')

  // Initialize Keycloak / sync SSO
  await syncSession()
  console.log('Sync Session')

  // init sentry if applicable
  // if (getFeatureFlag('sentry-enable')) {
  //   console.info('Initializing Sentry...') // eslint-disable-line no-console
  //   Sentry.init({
  //     app,
  //     dsn: window.sentryDsn,
  //     environment: sessionStorage.getItem('POD_NAMESPACE'),
  //     integrations: [
  //       new BrowserTracing({
  //         routingInstrumentation: Sentry.vueRouterInstrumentation(router),
  //         tracingOrigins: [window.location.hostname, window.location.origin, /^\//],
  //       }),
  //     ],
  //     logErrors: true,
  //     release: 'search-ui@' + process.env.VUE_APP_VERSION,
  //     // Set tracesSampleRate to 1.0 to capture 100%
  //     // of transactions for performance monitoring.
  //     // We recommend adjusting this value in production
  //     tracesSampleRate: window.sentryTSR,
  //   })
  // }

  // initialize Launch Darkly
  if (window.ldClientId) {
    await initLdClient()
  }
  console.log('Past LD Client')


  // start Vue application
  console.info('Starting app...') // eslint-disable-line no-console
  app.use(router).use(store).use(vuetify).mount('#app')
  // new Vue({
  //   vuetify: new Vuetify({
  //     iconfont: 'mdi',
  //     theme: {
  //       themes: {
  //         light: {
  //           primary: '#1669bb', // same as $$primary-blue
  //           darkBlue: '#38598a',
  //           lightBlue: '#E2E8EE', // same as $app-lt-blue
  //           error: '#d3272c',
  //           success: '#1a9031',
  //           darkGray: '#495057' // same as theme $gray7
  //         }
  //       }
  //     },
  //     icons: {
  //       values: {
  //         ExecutorBusinessIcon: { // name of our custom icon
  //           component: ExecutorBusinessIcon // our custom component
  //         },
  //         ExecutorPersonIcon: {
  //           component: ExecutorPersonIcon
  //         },
  //         HomeLocationIcon: {
  //           component: HomeLocationIcon
  //         },
  //         HomeOwnersIcon: {
  //           component: HomeOwnersIcon
  //         }
  //       }
  //     }
  //   }),
  //   vuetify: Vuetify,
  //   router: getVueRouter(),
  //   store: getVuexStore(),
  //   render: h => h(App)
  // }).$mount('#app')
}

// configure Keycloak Service
async function syncSession () {
  console.info('Starting Keycloak service...') // eslint-disable-line no-console
  const keycloakConfig: any = {
    url: `${window.keycloakAuthUrl}`,
    realm: `${window.keycloakRealm}`,
    clientId: `${window.keycloakClientId}`
  }

  await KeycloakService.setKeycloakConfigUrl(keycloakConfig)

  // Auto authenticate user only if they are not trying a login or logout
  if (!isSigningIn() && !isSigningOut()) {
    // Initialize token service which will do a check-sso to initiate session
    await KeycloakService.initializeToken(null).then().catch(err => {
      if (err?.message !== 'NOT_AUTHENTICATED') {
        throw err
      }
    })
  }
}

start().catch(error => {
  console.error(error) // eslint-disable-line no-console
  // alert(
  //   'There was an error starting this page. (See console for details.)\n' +
  //   'Please try again later.'
  // )
})

// // execution and error handling
// start().catch(error => {
//   console.error(error) // eslint-disable-line no-console
//   alert('There was an error starting this page. (See console for details.)\n' +
//     'Please try again later.')
// })
