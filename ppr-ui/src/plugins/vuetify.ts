// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import * as labs from 'vuetify/labs/components'

import {ExecutorBusinessIcon, ExecutorPersonIcon, HomeLocationIcon, HomeOwnersIcon} from '@/assets/svgs';

// vuetify: new Vuetify({
//   iconfont: 'mdi',
//   theme: {
//     themes: {
//       light: {
//         primary: '#1669bb', // same as $$primary-blue
//         darkBlue: '#38598a',
//         lightBlue: '#E2E8EE', // same as $app-lt-blue
//         error: '#d3272c',
//         success: '#1a9031',
//         darkGray: '#495057' // same as theme $gray7
//       }
//     }
//   },
//   icons: {
//     values: {
//       ExecutorBusinessIcon: { // name of our custom icon
//         component: ExecutorBusinessIcon // our custom component
//       },
//       ExecutorPersonIcon: {
//         component: ExecutorPersonIcon
//       },
//       HomeLocationIcon: {
//         component: HomeLocationIcon
//       },
//       HomeOwnersIcon: {
//         component: HomeOwnersIcon
//       }
//     }
//   }

export default createVuetify({
  components: {
    components,
    ...labs,
  },
  directives,
  iconfont: 'mdi',
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1669bb', // same as $$primary-blue
          darkBlue: '#38598a',
          error: '#d3272c',
          success: '#1a9031',
          warning: '#ffc107'
        }
      }
    },
  },
})
