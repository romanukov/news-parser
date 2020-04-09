import makeRequest from './fetch';

function makeUrl(url, query) {
  let result = url;
  if (query && typeof query === 'object') {
    result += '?';
    for (const param in query) {
      if (typeof query[param] !== 'undefined') {
        result += `${param}=${query[param]}&`;
      }
    }
  }
  return result;
}

export default {
  recieveToken({ email, password }) {
    return makeRequest('auth/', {
      method: 'POST',
      body: JSON.stringify({
        username: email,
        password,
      }),
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'same-origin',
    });
  },
  addAuthorToBlacklist(message) {
    return makeRequest(`feed_message/blacklist/${message}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      credentials: 'same-origin',
    });
  },
  removeAuthorFromBlacklist(message) {
    return makeRequest(`feed_message/blacklist/${message}/remove`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      credentials: 'same-origin',
    });
  },
  addToFavorites(message) {
    return makeRequest(`feed_message/favorites/${message}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      credentials: 'same-origin',
    });
  },
  removeFromFavorites(message) {
    return makeRequest(`feed_message/favorites/${message}/remove`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      credentials: 'same-origin',
    });
  },
  getMessages(feed, offset = 0, query = {}) {
    return makeRequest(makeUrl(`feed_message/${feed}/`, { ...query, offset }), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      credentials: 'same-origin',
    }, query);
  },
  getFeedList() {
    return makeRequest('feed/?limit=20&offset=0', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      credentials: 'same-origin',
    });
  },
  getMoreFeedList(offset) {
    return makeRequest(`feed/?limit=20&offset=${offset}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      credentials: 'same-origin',
    });
  },
  getSourceGroupList() {
    return makeRequest('source_group/?limit=1000', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      credentials: 'same-origin',
    });
  },
  getFeed(id) {
    return makeRequest(`feed/${id}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      credentials: 'same-origin',
    });
  },
  putFeed(feed) {
    return makeRequest(`feed/${feed.id}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      body: JSON.stringify(feed),
      credentials: 'same-origin',
    });
  },
  createFeed(feed) {
    return makeRequest('feed/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      body: JSON.stringify(feed),
      credentials: 'same-origin',
    });
  },
  deleteFeed(id) {
    return makeRequest(`feed/${id}/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      credentials: 'same-origin',
    });
  },
  getFavorites() {
    return makeRequest('favorite', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      credentials: 'same-origin',
    });
  },
  getSources() {
    return makeRequest(makeUrl('source', { limit: 20, offset: 0 }), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      credentials: 'same-origin',
    });
  },
  getMoreSources(offset) {
    return makeRequest(makeUrl('source', { limit: 20, offset }), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      credentials: 'same-origin',
    });
  },
  getSource(id) {
    return makeRequest(makeUrl(`source/${id}`), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      credentials: 'same-origin',
    });
  },
  createSource(obj = {}) {
    return makeRequest(makeUrl('source/'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      body: JSON.stringify(obj),
      credentials: 'same-origin',
    });
  },
  putSource(obj) {
    return makeRequest(makeUrl(`source/${obj.id}/`), {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      body: JSON.stringify(obj),
      credentials: 'same-origin',
    });
  },
  deleteSource(id) {
    return makeRequest(makeUrl(`source/${id}/`), {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      credentials: 'same-origin',
    });
  },
  getProfile() {
    return makeRequest('user/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      credentials: 'same-origin',
    });
  },
  putProfile(obj = {}) {
    return makeRequest('user/', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      body: JSON.stringify(obj),
      credentials: 'same-origin',
    });
  },
  getMessageCount(obj = {}) {
    return makeRequest('message/count/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      credentials: 'same-origin',
    });
  },
  shareMessage(id = '') {
    return makeRequest(`message/${id}/share/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `JWT ${localStorage.getItem('user_token')}`,
      },
      credentials: 'same-origin',
    });
  },
  getSharedMessage(id = '') {
    return makeRequest(`shared/${id}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'same-origin',
    });
  },
};
