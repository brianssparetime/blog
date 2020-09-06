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
