// The Vue build version to load with the `import` command
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
import { VueMasonryPlugin } from 'vue-masonry';
import InfiniteScroll from 'vue-infinite-scroll';
import VueRangedatePicker from 'vue-rangedate-picker';
import VueNativeSock from 'vue-native-websocket';
import VueClickOutside from 'vue-click-outside';
// import infiniteScroll from 'vue-infinite-scroll';
import 'vue-awesome/icons';
import Icon from 'vue-awesome/components/Icon';
import 'vue-resize/dist/vue-resize.css';
// Импорты глобальных модулей
// Components
import Message from '@/components/Message';
import Sidebar from '@/components/Sidebar';
import SourceIcon from '@/components/SourceIcon';
import Filters from '@/components/Filters';
import Modal from '@/components/Modal';
// Packages
import { ResizeObserver } from 'vue-resize';
import moment from 'moment-timezone';
import VueMoment from 'vue-moment';
// Layouts
import LayoutMain from '@/layouts/Main';
import LayoutAuth from '@/layouts/Auth';
import Loader from '@/components/Loader';
// Modals
import ModalAddFeed from '@/components/ModalComponents/AddFeed';
import ModalChangeFeed from '@/components/ModalComponents/ChangeFeed';
import ModalChangeSource from '@/components/ModalComponents/ChangeSource';
// App Components
import router from './router';
import store from './store';

import './styles/bootstrap-customize.css';
import './styles/global.css';

Vue.component('layout-main', LayoutMain);
Vue.component('layout-auth', LayoutAuth);
Vue.component('message', Message);
Vue.component('sidebar', Sidebar);
Vue.component('source-icon', SourceIcon);
Vue.component('filters', Filters);
Vue.component('resize-observer', ResizeObserver);
Vue.component('modal', Modal);
Vue.component('loader', Loader);
Vue.component('modal-add-feed', ModalAddFeed);
Vue.component('modal-change-feed', ModalChangeFeed);
Vue.component('modal-change-source', ModalChangeSource);

Vue.directive('click-outside', VueClickOutside);

Vue.use(VueRangedatePicker);
Vue.use(VueMoment, { moment });
Vue.use(InfiniteScroll);
Vue.use(
  VueNativeSock,
  'wss://app.samfeeds.com/ws/',
  // 'ws://127.0.0.1:8000/ws/',
  {
    connectManually: true,
    store,
    format: 'json',
    // // (Boolean) whether to reconnect automatically (false)
    reconnection: true,
    // // (Number) number of reconnection attempts before giving up (Infinity),
    // reconnectionAttempts: 5,
    // // (Number) how long to initially wait before attempting a new (1000)
    reconnectionDelay: 3000,
  },
);
// Vue.use(infiniteScroll);

Vue.component('icon', Icon);
Vue.use(VueMasonryPlugin);
Vue.use(BootstrapVue);

Vue.config.productionTip = false;

function promisedSetTimeout(before, after, time) {
  return new Promise((resolve) => {
    before();
    setTimeout(() => {
      after();
      resolve();
    }, time);
  });
}
/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  template: `<div id="app">
      <router-view ref="app"/>
      <div class="notifications">
        <transition
            :key="errKey"
            v-for="(err, errKey) in errors" name="fade">
          <div
            :class="err.isError ? 'notification--err' : ''"
            class="notification">
            <div class="notification__icon">
              <source-icon mode="md" type="informationCircle"></source-icon>
            </div>
            <div @click="hideErr(err)" class="notification__exit">
              <source-icon mode="md" type="close"></source-icon>
            </div>
            <div class="notification__body-container">
              <div class="notification__header">{{ err.title }}</div>
              <div class="notification__body" >{{ err.body }}</div>
            </div>
          </div>
        </transition>
      </div>
    </div>`,
  methods: {
    hideErr(errorView) {
      if (~this.errors.indexOf(errorView)) {
        this.errors.splice(this.errors.indexOf(errorView), 1);
      }
    },
  },
  data() {
    return {
      NativeNote: class NativeNote {
        constructor(title, body, isError = false) {
          this.title = title;
          this.body = body;
          this.isError = isError;
        }
      },
      errors: [],
    };
  },
  async created() {
    this.$on('dateNull', () => {
      this.$refs.app.$refs.filter.$refs.date[0].$emit('dateNull');
    });
    this.$on('handleError', async (err) => {
      let errorView;
      if (err && err.status) {
        switch (err.status) {
          case 400:
            let nativeText = '';
            if (err.body) {
              for (const key in err.body) {
                if (key !== 'non_field_errors') {
                  let prettyKey = key;
                  prettyKey = prettyKey[0].toUpperCase() + prettyKey.slice(1, prettyKey.length);
                  for (let ch = 1; ch < prettyKey.length; ++ch) {
                    if (prettyKey[ch] === '_') {
                      prettyKey = `${prettyKey.slice(0, ch)} ${prettyKey.slice(ch + 1, prettyKey.length)}`;
                    }
                  }
                  nativeText += `${prettyKey}: ${err.body[key]}\n`;
                } else {
                  nativeText += `${err.body[key]}\n`;
                }
              }
            }
            errorView = new this.NativeNote(
              'Validation error',
              nativeText || 'Verify that the data entered is correct.',
              true,
            );
            break;
          case 401:
            this.$store.dispatch('auth/logout');
            this.$disconnect();
            this.$router.push('/login');
            break;
          case 403:
            errorView = new this.NativeNote(
              'Access error',
              err.body && err.body.detail ? err.body.detail : 'You do not have access to perform this operation.',
              true,
            );
            break;
          case 404:
            break;
          case 405:
            errorView = new this.NativeNote(
              'Access error',
              err.nativeText ? err.text : 'You do not have access to perform this operation.',
              true,
            );
            break;
          case 500:
            errorView = new this.NativeNote(
              'Internal server error',
              err.nativeText ? err.text : 'An application error occurred. Please reload the page or contact technical support.',
              true,
            );
            break;
          case 502:
            errorView = new this.NativeNote(
              'Server gateway error',
              err.nativeText ? err.text : '502 server error. Please reload page',
              true,
            );
            break;
        }
      }
      if (errorView) {
        this.errors.push(errorView);
        await promisedSetTimeout(
          () => {},
          () => {},
          4000);
        this.hideErr(errorView);
      }
    });
    this.$on('handleNote', async (note) => {
      const errorView = new this.NativeNote(note.title, note.text, false);
      if (errorView) {
        this.errors.push(errorView);
        await promisedSetTimeout(
          () => {},
          () => {},
          4000);
        this.hideErr(errorView);
      }
    });
    if (this.$route.name !== 'Login') {
      try {
        this.$store.dispatch('source/getSourceList');
        if (this.$route.path !== '/') this.$store.dispatch('auth/getProfile');
      } catch (err) {
        this.$emit('handleError', err);
      }
    }
  },
});
