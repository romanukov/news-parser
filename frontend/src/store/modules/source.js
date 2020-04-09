import api from '../api';

export default {
  namespaced: true,
  state: {
    sourceList: [],
    sourceGroups: [],
    sourceLoading: false,
    offset: 0,
    count: 0,
  },
  mutations: {
    setCount(state, num) {
      state.count = num;
    },
    setSourceLoading(state, bool) {
      state.sourceLoading = bool;
    },
    deleteSourceFromList(state, id) {
      for (let i = 0; i < state.sourceList.length; i++) {
        if (state.sourceList[i].id === id) {
          state.sourceList.splice(i, 1);
          break;
        }
      }
    },
    setSourceList(state, arr) {
      state.sourceList = arr;
    },
    setSourceGroupList(state, arr) {
      state.sourceGroups = arr;
    },
    setOffset(state, num) {
      state.offset = num;
    },
  },
  actions: {
    async getSourceList({ commit, state }, important) {
      try {
        if (!state.sourceLoading || important) {
          commit('setSourceLoading', true);
          const sources = await api.getSources();
          commit('setSourceList', [...sources.results]);
          commit('setOffset', sources.results.length);
          commit('setCount', sources.count);
          commit('setSourceLoading', false);
        }
      } catch (err) { throw err; }
    },
    async getMoreSourceList({ commit, state }) {
      try {
        if (!state.sourceLoading && state.sourceList.length < state.count) {
          commit('setSourceLoading', true);
          const sources = await api.getMoreSources(state.offset);
          commit('setSourceList', [...state.sourceList, ...sources.results]);
          commit('setOffset', state.offset + sources.results.length);
          commit('setCount', sources.count);
          commit('setSourceLoading', false);
        }
      } catch (err) { throw err; }
    },
    async getSourceGroupList({ commit }) {
      try {
        const groups = await api.getSourceGroupList();
        const _result = [...groups.results];
        commit('setSourceGroupList', _result);
      } catch (err) { throw err; }
    },
    async getSource({}, id) {
      try {
        return await api.getSource(id);
      } catch (err) { throw err; }
    },
    async createSource({ dispatch }, obj) {
      try {
        const response = await api.createSource(obj);
        dispatch('getSourceList');
        return response;
      } catch (err) { throw err; }
    },
    async putSource({ dispatch }, obj) {
      try {
        await api.putSource(obj);
        dispatch('getSourceList');
      } catch (err) { throw err; }
    },
    async deleteSource({ commit }, id) {
      try {
        commit('deleteSourceFromList', id);
        return await api.deleteSource(id);
      } catch (err) { throw err; }
    },
    async getMessageCount({ commit }) {
      try {
        return await api.getMessageCount();
      } catch (err) { throw err; }
    },
  },
};
