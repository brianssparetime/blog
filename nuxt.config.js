export default {
  // Target (https://go.nuxtjs.dev/config-target)
  target: 'static',

  // Global page headers (https://go.nuxtjs.dev/config-head)
  head: {
    title: 'bst-blog',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: '' }
    ],
    link: [
      { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
    ]
  },

  // Global CSS (https://go.nuxtjs.dev/config-css)
  css: [
    '~/static/css/bst.css'
  ],

  // env variables set up in package.json
  //     see https://github.com/nuxt/nuxt.js/issues/1789

  // Plugins to run before rendering page (https://go.nuxtjs.dev/config-plugins)
  plugins: ['~/plugins/prism.js', '~/plugins/globalComponents.js'],

  // Auto import components (https://go.nuxtjs.dev/config-components)
  components: true,

  // Modules for dev and build (recommended) (https://go.nuxtjs.dev/config-modules)
  buildModules: [
    // https://go.nuxtjs.dev/eslint
    '@nuxtjs/eslint-module'
  ],
  env: {
    baseUrl: process.env.BASE_URL || 'http://localhost:3000'
  },
  // Modules (https://go.nuxtjs.dev/config-modules)
  modules: [
    // 'nuxt-interpolation',
    // https://go.nuxtjs.dev/axios
    '@nuxtjs/axios',
    // https://go.nuxtjs.dev/content
    '@nuxt/content'
  ],

  // Axios module configuration (https://go.nuxtjs.dev/config-axios)
  axios: {},

  // Content module configuration (https://go.nuxtjs.dev/config-content)
  content: {
    markdown: {
      prism: {
        theme: false
      }
    },
    nestedProperties: ['post.tags']

  },

  // Build Configuration (https://go.nuxtjs.dev/config-build)
  build: {
    extend (config, ctx) {
      if (ctx.isDev) {
        config.devtool = ctx.isClient ? 'source-map' : 'inline-source-map'
      } // https://medium.com/js-dojo/debugging-nuxt-js-with-vs-code-60a1a9e75cf6
      // https://liftcodeplay.com/2019/12/25/how-to-debug-nuxt-js-with-vs-code/
      if (ctx.isDev && ctx.isClient) {
        config.module.rules.push({
          enforce: 'pre',
          test: /\.(js|vue)$/,
          loader: 'eslint-loader',
          exclude: /(node_modules)/,
          options: {
            fix: true
          }
        })
      }

      config.module.rules.push({
        test: /\.md$/i,
        loader: 'ignore-loader'
      }) // see https://github.com/nuxt/content/issues/106#issuecomment-666283547
      config.module.rules.push({
        test: /\.xcf$/i,
        loader: 'ignore-loader'
      })
      config.module.rules.push({
        test: /\.mov$/i,
        loader: 'ignore-loader'
      })
    }
  }
}
