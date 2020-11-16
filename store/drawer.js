/*
export const state = () => ({
  drawer: false,
});

export const mutations = {
  toggle(state) {
    state.drawer = !state.drawer;
  },
};

export const getters = {
  getDrawerState(state) {
    return state.drawer;
  },
};
*/
import Vue from 'vue'

export const store = Vue.observable({
  isNavOpen: false
})

export const mutations = {
  setIsNavOpen (yesno) {
    store.isNavOpen = yesno
  },
  toggleNav () {
    store.isNavOpen = !store.isNavOpen
  }
}
