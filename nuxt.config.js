export default {
  target: "static",


  /*
   ** Nuxt rendering mode
   ** See https://nuxtjs.org/api/configuration-mode
   */
  mode: "universal",


  // do I need this?  added for nuxt-content images...
  components:true, 

  /* 
  // don't need this atm
  env : {
    brewing_tags : ["brewing", "ale", "beer", "mead", "acerglyn"],
  }, */


  /*
   ** Headers of the page
   ** See https://nuxtjs.org/api/configuration-head
   */
  head: {
    title: process.env.npm_package_name || "",
    meta: [
      { charset: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      {
        hid: "description",
        name: "description",
        content: process.env.npm_package_description || "",
      },
    ],
    link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
  },


  /*
   ** Global CSS
   */
  css: [],


  /*
   ** Plugins to load before mounting the App
   ** https://nuxtjs.org/guide/plugins
   */
  plugins: ["~/plugins/prism.js", "~/plugins/globalComponents.js"],


  /*
   ** Nuxt.js dev-modules
   */
  buildModules: [
    // Doc: https://github.com/nuxt-community/eslint-module
    "@nuxtjs/eslint-module",
  ],


  /*
   ** Nuxt.js modules
   */
  modules: [["@nuxt/content"], ['nuxt-interpolation'],],


  /* hooks for nuxt content */
  /*
  hooks: {
    /* 
    extract from filename and path:
    - the post date?
    - the title? 

    const dirp_rx = /^/

    'content:file:beforeInsert': (document) => {
      if (document.extension === '.md') {
        document.foo = true;
      }
    }
  },*/


  /*
   ** Nuxt Content configuration
   */
  content: {
    markdown: {
      prism: {
        theme: false,
      },
    },
    nestedProperties: ['post.tags'],
  },


  /*
   ** Build configuration
   ** See https://nuxtjs.org/api/configuration-build/
   */
  build: {
    extend(config, ctx) {
      if (ctx.isDev) {
        config.devtool = ctx.isClient ? 'source-map' : 'inline-source-map'
      } // https://medium.com/js-dojo/debugging-nuxt-js-with-vs-code-60a1a9e75cf6
      //https://liftcodeplay.com/2019/12/25/how-to-debug-nuxt-js-with-vs-code/
      if (ctx.isDev && ctx.isClient) {
        config.module.rules.push({
          enforce: "pre",
          test: /\.(js|vue)$/,
          loader: "eslint-loader",
          exclude: /(node_modules)/,
          options: {
            fix: true,
          },
        });
      }
      config.module.rules.push({
        test: /\.md$/i,
        loader: 'ignore-loader'
      }); // see https://github.com/nuxt/content/issues/106#issuecomment-666283547
    },
  },
};
//process.env.DEBUG = 'nuxt:*'
