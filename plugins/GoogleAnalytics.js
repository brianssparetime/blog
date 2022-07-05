// import Vue from 'vue'
// import VueGtag from 'vue-gtag'

// export default ({ app }) => {
//   Vue.use(VueGtag, {
//     config: { id: 'G-JDHYEEB466' },
//     appName: 'bstblog'
//   }, app.router)
// }

import Vue from 'vue'
import VueGtag from 'vue-gtag'

export default ({ app }) => {
  const getGDPR = localStorage.getItem('GDPR:accepted')

  Vue.use(VueGtag, {
    config: { id: 'G-JDHYEEB466' },
    bootstrap: getGDPR === 'true',
    appName: 'bstblog',
    enabled: getGDPR === 'true',
    pageTrackerScreenviewEnabled: true
  }, app.router)
}
