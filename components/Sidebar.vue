<template>
  <div class="sidebar">
    <div
      v-show="isPanelOpen"
      class="sidebar-backdrop"
      @click="closeSidebarPanel"
    />
    <transition name="slide">
      <div v-show="isPanelOpen" class="sidebar-panel">
        <slot />
      </div>
    </transition>
  </div>
</template>
<script>
// import { mapGetters, mapMutations } from 'vuex';

import { store, mutations } from '../store/drawer.js'
export default {
  computed: {
    isPanelOpen () {
      return store.isNavOpen
    }
  },
  methods: {
    closeSidebarPanel: mutations.toggleNav
  }
}
</script>
<style>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.2s ease;
}
.slide-enter,
.slide-leave-to {
  transform: translateX(-100%);
  transition: all 150ms ease-in 0s;
}
.sidebar-backdrop {
  background-color: rgba(19, 15, 64, 0.4);

  width: 100vw;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  cursor: pointer;
}
.sidebar-panel {
  /*background-color: #0070fe;*/
  background-color: #ffffff;
  overflow-y: auto;
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  z-index: 999;
  padding: 3rem 20px 2rem 20px;
  width: 300px;
}
</style>
