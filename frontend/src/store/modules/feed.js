/* eslint no-shadow: ["error", { "allow": ["state"] }] */
import api from '../api';

// initial state
const state = {
  feedList: [],
  currentFeed: {},
  messages: [],
  shownDuplicates: [],
  elemCount: 0,
  actualLength: 0,
  busy: true,
  feedLoading: false,
  offset: 0,
  count: 0,
  sharedMessage: null,
};

// getters
const getters = {
  feedList: state => state.feedList,
  currentFeed: state => state.currentFeed,
  messages: state => state.messages,
  shownDuplicates: state => state.shownDuplicates,
};

// actions
const actions = {
  async removeFromFavorites({ commit }, message) {
    try {
      commit('toggleMessageFavoritesFlag', message);
      return await api.removeFromFavorites(message.id);
    } catch (err) { throw err; }
  },
  async addToFavorites({ commit }, message) {
    try {
      commit('toggleMessageFavoritesFlag', message);
      return await api.addToFavorites(message.id);
    } catch (err) { throw err; }
  },
  async shareMessage(store, id) {
    try {
      return await api.shareMessage(id);
    } catch (e) { throw e; }
  },
  async getSharedMessage(store, id) {
    try {
      return await api.getSharedMessage(id);
    } catch (e) { throw e; }
  },
  async addAuthorToBlacklist({ commit }, message) {
    try {
      commit('addAuthorToBlacklist', message);
      return await api.addAuthorToBlacklist(message.id);
    } catch (err) { throw err; }
  },
  async removeAuthorFromBlacklist({ commit }, message) {
    try {
      commit('removeAuthorFromBlacklist', message);
      await api.removeAuthorFromBlacklist(message.id);
    } catch (err) { throw err; }
  },
  async getFeedList({ commit, state }, important) {
    if (!state.feedLoading || important) {
      try {
        commit('setFeedLoading', true);
        const feeds = await api.getFeedList();
        commit('setCount', feeds.count);
        commit('setOffset', feeds.results.length);
        commit('setFeedList', feeds.results);
        commit('setFeedLoading', false);
        // return feeds;
      } catch (err) {
        throw err;
      }
    }
  },
  async getMoreFeedList({ commit, state }) {
    if (!state.feedLoading && state.feedList.length < state.count) {
      try {
        commit('setFeedLoading', true);
        const feeds = await api.getMoreFeedList(state.offset);
        commit('setCount', feeds.count);
        commit('setOffset', state.offset += feeds.results.length);
        commit('setFeedList', [...state.feedList, ...feeds.results]);
        commit('setFeedLoading', false);
        // return feeds;
      } catch (err) {
        throw err;
      }
    }
  },
  async getFeedToChange(store, feedId) {
    try {
      if (!isNaN(feedId)) {
        return await api.getFeed(feedId);
      }
      return { id: feedId };
    } catch (err) { throw err; }
  },
  async changeFeed(store, feed) {
    try {
      return await api.putFeed(feed);
    } catch (err) { throw err; }
  },
  async createFeed({ dispatch }, feed) {
    try {
      const response = await api.createFeed(feed);
      await dispatch('getFeedList');
      return response;
    } catch (err) { throw err; }
  },
  async deleteFeed({ commit }, id) {
    try {
      api.deleteFeed(id).then(() => {
        commit('deleteFeedFromList', id);
      });
    } catch (err) { throw err; }
  },
  async setCurrentFeed({ commit }, { feed, query }) {
    try {
      commit('setBusy', true);
      commit('clearMessages', []);
      if (typeof feed.id === 'number') {
        api.getFeed(feed.id).then((fullFeed) => {
          commit('setCurrentFeed', fullFeed);
        });
      } else {
        commit('setCurrentFeed', feed);
      }
      const messages = await api.getMessages(feed.id, 0, query);
      commit('setActualLength', messages.results.length);
      commit('addMessages', messages);
      setTimeout(() => { commit('setBusy', false); }, 20);
    } catch (err) {
      setTimeout(() => { commit('setBusy', false); }, 20);
      throw err;
    }
  },
  async loadMessages({ commit, state }, payload) {
    try {
      commit('setBusy', true);
      const messages = await api.getMessages(
        payload.feed.id,
        state.actualLength + payload.feed.new_messages,
        payload.query,
      );
      commit('setActualLength', state.actualLength + messages.results.length);
      commit('addMessages', messages);
      commit('setBusy', false);
    } catch (err) { throw err; }
  },
};

// mutations
const mutations = {
  setCount(state, num) {
    state.count = num;
  },
  setOffset(state, num) {
    state.offset = num;
  },
  setElemCount(state, num) {
    state.elemCount = num;
  },
  setBusy(state, bool) {
    state.busy = bool;
  },
  setActualLength(state, num) {
    state.actualLength = num;
  },
  setFeedList(state, feeds) {
    state.feedList = feeds;
  },
  setCurrentFeed(state, feed) {
    for (let i = 0; i < state.feedList.length; i += 1) {
      if (state.feedList[i].id === feed.id) {
        state.feedList[i].new_messages = 0;
        break;
      }
    }
    state.currentFeed = feed;
    state.currentFeed.full_loaded = false;
    state.currentFeed.news = state.currentFeed.new_messages;
    state.currentFeed.new_messages = 0;
  },
  deleteFeedFromList(state, id) {
    for (let i = 0; i < state.feedList.length; i += 1) {
      if (state.feedList[i].id === id) {
        state.feedList.splice(i, 1);
        break;
      }
    }
  },
  clearMessages(state) {
    state.messages = [];
    state.shownDuplicates = [];
  },
  addMessages(state, messages) {
    state.elemCount = messages.count;
    if (!state.currentFeed) return;
    if (messages.next === null) {
      state.currentFeed.full_loaded = true;
    }
    const oldLength = state.messages.length;
    let i = oldLength;
    for (
      let j = 0;
      j < messages.results.length;
      j += 1
    ) {
      if (messages.results[j].duplicate_id > 0) {
        if (!state.shownDuplicates.includes(messages.results[j].duplicate_id)) {
          state.shownDuplicates.push(messages.results[j].duplicate_id);
          state.messages.push(messages.results[j]);
        }
      } else {
        state.messages.push(messages.results[j]);
      }
    }
    for (
      i;
      (i < state.messages.length) && (i < oldLength + state.currentFeed.news);
      i += 1
    ) {
      state.messages[i].new = true;
    }
    state.currentFeed.news -= i;
  },
  addAuthorToBlacklist(state, message) {
    if (state.currentFeed && state.currentFeed.id === parseInt(state.currentFeed.id, 10)) {
      for (let i = 0; i < state.messages.length; i += 1) {
        if (state.messages[i].username === message.username) {
          state.messages.splice(i, 1);
          i -= 1;
        }
      }
    } else {
      // eslint-disable-next-line
      message.blacklist = true;
    }
  },
  removeAuthorFromBlacklist(state, message) {
    for (let i = 0; i < state.messages.length; i += 1) {
      if (state.messages[i].username === message.username) {
        state.messages[i].blacklist = false;
        i -= 1;
      }
    }
  },
  toggleMessageFavoritesFlag(state, message) {
    // eslint-disable-next-line
    message.favorites = !message.favorites;
  },
  setFeedLoading(state, bool) {
    state.feedLoading = bool;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
