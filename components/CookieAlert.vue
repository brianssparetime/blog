<template>
  <div
    v-if="isOpen"
    class="cookieBar"
  >
    <div>
      I'm using cookies because I'm curious who comes here.
      <BR />
      No commercial use of your data.
      This is my spare time after all...
      <div class="priv-button-yes" @click="accept">
        Yeah, sure
      </div>
      <div class="priv-button-no" @click="deny">
        <!-- &times; -->
        Nope
      </div>
    </div>
  </div>
</template>

<script>

import { bootstrap } from 'vue-gtag'

export default {
  data () {
    return {
      isOpen: false
    }
  },
  mounted () {
    if (!this.getGDPR() === true) {
      this.isOpen = true
    }
  },
  methods: {
    deny () {
      if (process.browser) {
        this.isOpen = false
        localStorage.setItem('GDPR:accepted', false)
      }
    },
    accept () {
      if (process.browser) {
        bootstrap().then((gtag) => {
          this.isOpen = false
          localStorage.setItem('GDPR:accepted', true)
          location.reload()
        })
      }
    },
    getGDPR () {
      if (process.browser) {
        return localStorage.getItem('GDPR:accepted', true)
      }
    }
  }
}
</script>

<style scoped>
.cookieBar {
  position:fixed;
  z-index:99;
  bottom:0;
  width:100%;
  padding:1rem;
  padding-left: 10%;
  padding-right: 10%;
  font-size: 10pt;
  border-top: solid;
  text-align:center;
  background-color:white;
  background-repeat:no-repeat;
  background-size:contain;
  transition: 1s ease;
  -webkit-transition: 1s ease;
  -moz-transition: 1s ease;
  /* display: flex;
  justify-content: space-between; */
}

.priv-button-yes {
  color: white;
  background: green !important;
  padding: 1px 7px 1px 5px;
  font-family: "Roboto Mono", monospace;
  text-decoration: none;
  margin: 5px 0;
  border-radius: 3px;
  float: left;
}
.priv-button-no {
  color: white;
  background: red !important;
  padding: 1px 7px 1px 5px;
  font-family: "Roboto Mono", monospace;
  text-decoration: none;
  margin: 5px 0;
  border-radius: 3px;
  float: right;
}
</style>
