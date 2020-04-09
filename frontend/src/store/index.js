import Vue from 'vue';
import Vuex from 'vuex';
import feed from './modules/feed';
import auth from './modules/auth';
import feedAdmin from './modules/feedAdmin';
import modal from './modules/modal';
import source from './modules/source';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    socket: {
      isConnected: false,
      reconnectError: false,
    },
    token: null,
  },
  getters: {
    token: state => state.token,
  },
  actions: {
    feedNewMessage({ commit }, action) {
      commit('incrementNewMessage', action.feed);
    },
  },
  mutations: {
    incrementNewMessage(state, feedId) {
      for (let i = 0; i < state.feed.feedList.length; i += 1) {
        const f = state.feed.feedList[i];
        if (f.id === feedId) {
          f.new_messages += 1;
        }
      }
    },
    SOCKET_ONOPEN(state) {
      // event as second argument
      state.socket.isConnected = true;
    },
    SOCKET_ONCLOSE(state) {
      state.socket.isConnected = false;
    },
    SOCKET_ONERROR() {
    },
    // default handler called for all methods
    SOCKET_ONMESSAGE() {
    },
    // mutations for reconnect methods
    SOCKET_RECONNECT() {
    },
    SOCKET_RECONNECT_ERROR(state) {
      state.socket.reconnectError = true;
    },
  },
  modules: {
    feed,
    auth,
    feedAdmin,
    modal,
    source,
  },
  strict: false,
});
