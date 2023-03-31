// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import * as labs from 'vuetify/labs/components'

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
