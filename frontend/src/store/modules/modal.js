/* eslint no-shadow: ["error", { "allow": ["state"] }] */

// initial state
const state = {
  show: true,
};

// getters
const getters = {
  modalShow: state => state.show,
};

// mutations
const mutations = {
  toggleModal(state) {
    state.show = !state.show;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
};
