/* eslint no-shadow: ["error", { "allow": ["state"] }] */
import api from '../api';

// initial state
const state = {
  feedList: [],
  feed: {},
};

// getters
const getters = {
  feedList: state => state.feedList,
  feed: state => state.feed,
};

// actions
const actions = {
  async getFeedList({ commit }, options) {
    const apiResponse = await api.getFeedList(options);
    commit('setFeedList', apiResponse.results);
  },
  async getFeed({ commit }, id) {
    const apiResponse = await api.getFeed(id);
    commit('setFeed', apiResponse);
  },
};

// mutations
const mutations = {
  setFeedList(state, list) {
    state.feedList = list;
  },
  setFeed(state, feed) {
    state.feed = feed;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
