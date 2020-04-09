import api from '../api';

export default {
  namespaced: true,
  state: {
    token: localStorage.getItem('user_token'),
    profile: null,
  },
  mutations: {
    setToken(state, str) {
      state.token = str;
      localStorage.setItem('user_token', str);
    },
    setProfile(state, obj) {
      state.profile = obj;
    },
  },
  actions: {
    async login({ commit, dispatch }, { email, password }) {
      try {
        const response = await api.recieveToken({ email, password });
        commit('setToken', response.token);
        commit('setProfile', (await api.getProfile()));
        dispatch('feed/getFeedList', true, { root: true });
        await dispatch('source/getSourceList', true, { root: true });
      } catch (err) {
        // error handling
        throw err;
      }
    },
    async getProfile({ commit }) {
      try {
        const response = await api.getProfile();
        commit('setProfile', response);
      } catch (err) {
        // error handling
        throw err;
      }
    },
    async putProfile({ commit }, data) {
      try {
        const response = await api.putProfile(data);
        commit('setProfile', response);
      } catch (err) {
        // error handling
        throw err;
      }
    },
    logout({ commit }) {
      commit('setToken', null);
      localStorage.removeItem('user_token');
    },
  },
};
