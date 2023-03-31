const webpack = require('webpack')
const fs = require('fs')
const packageJson = fs.readFileSync('./package.json')
const appName = JSON.parse(packageJson).appName
const appVersion = JSON.parse(packageJson).version
const sbcName = JSON.parse(packageJson).sbcName
const sbcVersion = JSON.parse(packageJson).dependencies['sbc-common-components']
const aboutText1 = (appName && appVersion) ? `${appName} v${appVersion}` : ''
const aboutText2 = (sbcName && sbcVersion) ? `${sbcName} v${sbcVersion}` : ''
const { defineConfig } = require('@vue/cli-service')
const { VuetifyPlugin } = require('webpack-plugin-vuetify')


process.env.VUE_APP_VERSION = process.env.npm_package_version

module.exports = defineConfig({
  configureWebpack: {
    plugins: [
      new VuetifyPlugin({}),
      new webpack.DefinePlugin({
        'process.env': {
          ABOUT_TEXT:
            (aboutText1 && aboutText2) ? `"${aboutText1}<br>${aboutText2}"`
              : aboutText1 ? `"${aboutText1}"`
                : aboutText2 ? `"${aboutText2}"`
                  : ''
        }
      })
    ],
    devtool: 'source-map'
  },
  transpileDependencies: true,
  publicPath: `/${process.env.VUE_APP_PATH}`
})

// COMPAT BUILD CONFIG
// chainWebpack: (config) => {
//   config.resolve.alias.set('vue', '@vue/compat')
//
//   config.module
//     .rule('vue')
//     .use('vue-loader')
//     .tap((options) => {
//       return {
//         ...options,
//         compilerOptions: {
//           compatConfig: {
//             MODE: 2,
//             COMPONENT_V_MODEL: false
//           }
//         }
//       }
//     })
//
//   config.plugin('webpack-plugin-vuetify').use(new VuetifyPlugin({}))
// },
