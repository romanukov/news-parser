<template>
  <div class="sidebar" :class="showSidebar ? '' : 'hidden-sidebar'">
    <div class="sidebar__header sidebar__header--blue position-relative justify-content-end">
      <div v-if="show" class="header__menu-button position-absolute top-left" :style="`left: ${ showSidebar ? 16 : 25}px; transition: .2s`" @click="showSidebar=!showSidebar">
        <icon name="bars"  scale="1.5"></icon>
      </div>
      <div class="logo top-left" v-show="showSidebar" @click="$router.push('/')">
        <div class="telegram-logo"></div>
      </div>
    </div>
    <a v-if="show" class="sidebar__header" v-show="showSidebar">
      <h4 style="font-size: 17px; font-family: 'Open Sans'; font-weight: 600; color: #424761;">Feed list</h4>
      <div class="sidebar__buttons">

      <b-button
        variant="primary"
        size="xs"
        @click="$router.push(
          {
            name: $route.name,
            query: Object.assign(
              {},
              $route.query,
              {
                modal: 'add_feed'
              }
            )
          }
        )">
        <source-icon mode="ios" type="disc"></source-icon>
        New feed
      </b-button>
      <b-button
        variant="primary"
        size="xs"
        @click="$router.push(
          {
            name: $route.name,
            query: Object.assign(
              {},
              $route.query,
              {
                modal: 'change_source'
              }
            )
          }
        )">
        <source-icon mode="ios" type="disc"></source-icon>
        New source
      </b-button>
      </div>
    </a>
    <VuePerfectScrollbar
      @ps-y-reach-end="$store.dispatch('feed/getMoreFeedList')"
      v-show="showSidebar"
      class="sidebar-scrollable--full" style="width: 100%;">
      <a v-if="show" class="sidebar__elem"
         v-for="feed in systemFeeds"
         @click="$root.$emit('dateNull'); $route.name === 'Messages' ? $store.dispatch('feed/setCurrentFeed', { feed, query: {} }) : $router.push({name:'Messages', query: {feed: feed.id}})"
         :class="feed.id === $store.state.feed.currentFeed.id ? 'sidebar__elem--active' : ''">
        <div class="sidebar__elem-caption">
          <div class="sidebar__elem-icon sidebar__elem--temp">
            <icon height="11" name="star" v-if="feed.id === 'favorites'"></icon>
            <span style="font-size: 11px;font-family: 'Roboto';font-weight: bold;line-height: 20px;" v-if="feed.id === 'all'">AM</span>
            <span style="font-size: 11px;font-family: 'Roboto';font-weight: bold;line-height: 20px;" v-if="feed.id === 'failover'">FO</span>
          </div>
          <span class="sidebar__elem-caption-text" v-show="showSidebar">
            {{ feed.name }}
          </span>
        </div>
        <div
             v-if="$store.state.feed.currentFeed.new_messages"
             class="sidebar__elem-badge"
             :class="'' ? showSidebar : 'sidebar__elem-badge--transparent'">{{$store.state.feed.currentFeed.new_messages}}</div>
      </a>

      <hr v-if="show" />
      <a v-if="show"
        :key="feedIndex"
         @click="$root.$emit('dateNull'); $route.name === 'Messages' ? $store.dispatch('feed/setCurrentFeed', { feed, query: {} }) : $router.push({name:'Messages', query: {feed: feed.id}})"
        :class="feed.id === $store.state.feed.currentFeed.id ? 'sidebar__elem--active' : ''"
        class="sidebar__elem"
        v-for="(feed, feedIndex) in $store.state.feed.feedList">
        <div class="sidebar__elem-caption">
          <div class="sidebar__elem-icon">
            <span style="font-size: 11px; font-family: 'Roboto'; font-weight: bold; line-height: 20px;">{{ feed.name.slice(0, 2).toUpperCase() }}</span>
          </div>
          <span class="sidebar__elem-caption-text" v-show="showSidebar">{{ feed.name }}</span>
        </div>
        <div @click.stop="changeFeed(feed.id)" v-show="!feed.pre_defined">
          <source-icon type="settings" class="settings-icon"></source-icon>
        </div>
        <div class="sidebar__elem-badge"
             v-if="feed.new_messages"
             :class="'' ? showSidebar : 'sidebar__elem-badge--transparent'">{{feed.new_messages < 100 ? feed.new_messages : '99+'}}</div>
      </a>
      <loader v-if="show" v-show="busy"></loader>
    </VuePerfectScrollbar>
    <VuePerfectScrollbar
      @ps-y-reach-end="$store.dispatch('feed/getMoreFeedList')"
      v-show="!showSidebar"
      class="sidebar-scrollable--adaptive"
      style="width: 100%; background: #fafbfc;">
      <a v-if="show"
         class="sidebar__elem"
         v-for="feed in systemFeeds"
         @click="$root.$emit('dateNull'); $route.name === 'Messages' ? $root.$emit('dateNull') && $store.dispatch('feed/setCurrentFeed', { feed, query: {} }) : $root.$emit('dateNull') && $router.push({name:'Messages', query: {feed: feed.id}})"
         :class="currentFeed && (feed.id === currentFeed.id) ? 'sidebar__elem--active' : ''">
        <div class="sidebar__elem-caption">
          <div class="sidebar__elem-icon sidebar__elem--temp">
            <icon height="11" name="star" v-if="feed.id === 'favorites'"></icon>
            <span style="font-size: 11px;font-family: 'Roboto';font-weight: bold;line-height: 20px;" v-if="feed.id === 'all'">AM</span>
            <span style="font-size: 11px;font-family: 'Roboto';font-weight: bold;line-height: 20px;" v-if="feed.id === 'failover'">FO</span>
          </div>
          <span class="sidebar__elem-caption-text" v-show="showSidebar">
            {{ feed.name }}
          </span>
        </div>
        <div
          v-if="currentFeed.new_messages"
          class="sidebar__elem-badge"
          :class="'' ? showSidebar : 'sidebar__elem-badge--transparent'">{{currentFeed.new_messages}}</div>
      </a>

      <hr v-if="show" />
      <a v-if="show"
         :key="feedIndex"
         @click="$root.$emit('dateNull'); $route.name === 'Messages'
           ? $store.dispatch('feed/setCurrentFeed', { feed, query: {} })
           : $router.push({
               name: 'Messages',
               query: {
                 feed: feed.id
               }
             })"
         :class="currentFeed && (feed.id === currentFeed.id) ? 'sidebar__elem--active' : ''"
         class="sidebar__elem"
         v-for="(feed, feedIndex) in feedList">
        <div class="sidebar__elem-caption">
          <div class="sidebar__elem-icon">
            <span style="font-size: 11px; font-family: 'Roboto'; font-weight: bold; line-height: 20px;">{{ feed.name.slice(0, 2).toUpperCase() }}</span>
          </div>
          <span class="sidebar__elem-caption-text" v-show="showSidebar">{{ feed.id }} {{currentFeed.id}}</span>
        </div>
        <div class="sidebar__elem-badge"
             v-if="feed.new_messages"
             :class="'' ? showSidebar : 'sidebar__elem-badge--transparent'">{{feed.new_messages < 100 ? feed.new_messages : '99+'}}</div>
      </a>
      <loader v-if="show" v-show="busy"></loader>
      <div class="button-container" style="width: 100%;">
        <b-button
          @click="$router.push({
            name: $route.name,
            query: Object.assign(
              {},
              $route.query,
              {
                modal: 'add_feed'
              }
            )
          })" style="margin: 7px auto; display: block; padding: 3px 7px 3px 6px;" variant="primary" size="xs">
          <source-icon mode="ios" type="disc"></source-icon>
          New
        </b-button>
      </div>
    </VuePerfectScrollbar>
  </div>
</template>
<style>
  .settings-icon {
    position: absolute !important;
    right: 35px !important;
    top: 10px !important;
  }
  .sidebar {
    white-space: nowrap;
    transition-property: width;
    transition-duration: .2s;
    min-width: 221px;
    overflow: hidden;
    transition: 0.02s;
  }
  .hidden-sidebar {
    min-width: 68px !important;
  }
  .hidden-sidebar .sidebar__elem-badge {
    position: relative;
    top: 2px;
  }
  .sidebar-scrollable--full {
    height: calc(100% - 112px);
  }
  .sidebar-scrollable--adaptive {
    height: calc(100% - 56px);
  }
  .sidebar__header h4 {
    margin: 0;
    font-weight: bolder;
  }
  .sidebar > hr {
    width: 90%;
    border: 0;
    border-bottom: 2px solid #37aee2;
  }
  .sidebar__header {
    height: 63px;
    box-sizing: border-box;
    padding: 5px 15px;
    align-items: center;
    justify-content: space-between;
    text-align: center;
    line-height: 53px;
    display: flex;
    cursor: pointer;
  }
  .sidebar__header--blue {
    justify-content: space-around;
    background-color: #36aee2;
    background-size: cover;
    height: 53px !important;
  }
  .sidebar__header h4 {
    margin: 0;
  }
  .layout__screen > .navbar {
    box-shadow: 2px 4px 3px rgba(0, 0, 0, 0.05);
  }
  .telegram-logo {
    width: 140px;
    margin-right: 10px;
    height: 40px;
    background-image: url("../assets/logo_samfeeds_auth.png");
    background-size: cover;
    position: relative !important;
    bottom: 3px !important;
    left: 25px !important;
  }
  .logo {
    font-size: 1.2rem;
    font-weight: bold;
    color: white;
    display: inline-flex;
    align-items: center;
    width: 100%;
  }
  .sidebar__elem {
    height: 42px;
    box-sizing: border-box;
    padding: 0.5rem 4px;
    display: flex;
    align-items: center;
    margin: 0 11px;
    position: relative;
    justify-content: space-between;
    cursor: pointer;
  }
  .sidebar__elem:hover .settings-icon {
    fill: #91a7b3;
  }
  .sidebar__elem:hover .settings-icon:hover {
    fill: #788591;
  }
  .sidebar__elem:hover:before {
    content: " ";
    position: absolute;
    top: 0;
    bottom: 0;
    width: 3px;
    left: -11px;
    background-color: #aaaaaa;
  }
  .sidebar__elem--active:before {
    content: " ";
    position: absolute;
    top: 0;
    bottom: 0;
    width: 3px;
    left: -11px;
    background-color: #37aee2;
  }
  .sidebar__elem + .sidebar__elem {
    border-top: 1px solid #edf3fa;
  }
  .sidebar__elem-caption {
    align-items: center;
    display: flex;
  }
  .sidebar__elem-caption-text {
    font-size: 12px;
    font-family: 'Roboto';
    font-weight: bold;
  }
  .sidebar__elem-icon {
    width: 20px;
    font-weight: bold;
    height: 20px;
    background-color: #a767f5;
    border-radius: 4px;
    font-size: 14px;
    text-align: center;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #EEEEEE;
    line-height: 30px;
  }
  .sidebar__elem-icon + span {
    margin-left: 10px;
  }
  .sidebar__elem:nth-child(2n) .sidebar__elem-icon {
    background-color: #9ad647;
  }
  .sidebar__elem:nth-child(3n) .sidebar__elem-icon {
    background-color: #f56767;
  }
  .sidebar__elem:nth-child(5n) .sidebar__elem-icon {
    background-color: #5ea4ff;
  }
  .sidebar__elem:nth-child(7n) .sidebar__elem-icon {
    background-color: #1A01Cc;
  }
  .sidebar__elem--temp {
    background-color: #797c8a !important;
  }
  .sidebar__buttons {
    display: inline-flex;
    flex-direction: column;
    height: 100%;
    justify-content: space-around;
  }
  .header__menu-button {
    width: auto;
    height: 43px;
    color: white;
    text-align: center;
    margin-right: 7px;
  }
  .sidebar__elem-badge {
    font-size: 10px;
    text-align: center;
    line-height: 20px;
    font-weight: 500;
    height: 20px;
    min-width: 20px;
    border-radius: 50%;
    background-color: #ebf8ff !important;
    color: #189cde;
    margin-left: 3px;
  }
  .sidebar__elem-badge--transparent {
    background-color: transparent;
  }
</style>
<script>
import VuePerfectScrollbar from 'vue-perfect-scrollbar';
import { mapState, mapActions } from 'vuex';

export default {
  name: 'Sidebar',
  data() {
    return {
      showSidebar: true,
      busy: false,
      systemFeeds: [
        {
          id: 'all',
          name: 'All messages',
          words: '',
          last_retrieve: '',
          new_messages: 0,
        },
        {
          id: 'favorites',
          name: 'Favorites',
          words: '',
          last_retrieve: '',
          new_messages: 0,
        },
        {
          id: 'failover',
          name: 'Fail Over',
          words: '',
          last_retrieve: '',
          new_messages: 0,
        },
      ],
    };
  },
  computed: {
    ...mapState('feed', [
      'feedList',
      'currentFeed',
    ]),
  },
  async created() {
    this.$store.dispatch('feed/getFeedList');
    if (window.innerWidth < 600) this.showSidebar = false;
  },
  props: {
    show: {
      type: Boolean,
      required: true,
    },
  },
  components: {
    VuePerfectScrollbar,
  },
  methods: {
    ...mapActions('feedAdmin', ['getFeed']),
    async changeFeed(id) {
      await this.getFeed(id);
      this.$router.push({ name: this.$route.name, query: { modal: 'change_feed', id } });
    },
  },
};
</script>
