module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
    es6: true,
  },
  parserOptions: {
    parser: "babel-eslint",
  },
  extends: [
    "@nuxtjs",
    /*
    "prettier",
    "prettier/vue",
    "plugin:prettier/recommended",
    */
    "plugin:nuxt/recommended",
  ],
  /* plugins: ["prettier"],*/
  plugins: [],
  // add your custom rules here
  rules: {
    //"no-console": "warn",
    "no-console": "off",
    "vue/no-unused-components": "warn",
    "no-unused-vars": "warn",
    "no-v-html": "off",
    /*
    "prettier/prettier": [
      "error",
      {
        endOfLine: "auto",
      },
    ],
    */
  },
};
