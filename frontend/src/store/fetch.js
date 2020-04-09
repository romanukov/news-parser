import _ from 'lodash';

const apiURL = '/api/';
const fetchFunction = async (url, options) => {
  try {
    const response = await fetch(`${apiURL}${url}`, options);
    if (response.status === 502) {
      return await fetchFunction(url, options);
    }
    if (response.status >= 400) {
      let body;
      try {
        body = await response.json();
      } catch (err) {
        throw response;
      }
      const err = {
        body: _.cloneDeep(body),
        status: response.status,
      };
      throw err;
    } else {
      if (response.status === 200 || response.status === 201) {
        return await response.json();
      }
      return { success: true };
    }
  } catch (err) { throw err; }
};
export default fetchFunction;
