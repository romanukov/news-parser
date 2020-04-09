<template>
  <layout-main
    @modalToggle="setModalShow"
    :modalShow.sync="modalShow"
    :modalTitle="modalTitle"
    @modalChangeSourceSave="reboot()"
    @scrollEnd="loadMore"
    :title="($store.state.feed.currentFeed && $store.state.feed.currentFeed.name ? $store.state.feed.currentFeed.name : 'Messages')"
    :sidebar="true">
    <filters
      ref="filter"
      class="px-1"
      @filterChange="setFilter"
      paginatorLabel="View"
      :paginatorViewSize="actualLength !== elemCount ? messages.length : actualLength"
      :paginatorMaxSize="$store.state.feed.elemCount"
      :showNewButton="false"
      :reverse="true"
      :filters="getFilters()">
    </filters>
    <div
      style="margin: 0 10px;"
      class="error-block"
      v-if="error">{{ error }}</div>
    <loader v-if="busy && !messages[0]"></loader>
    <div
      class="messages"
      ref="messagesBlock"
      v-masonry
      transition-duration="0.3s"
      item-selector=".messages__card">
      <div
        class="messages__card"
        v-masonry-tile
        :key="i"
        v-for="(message, i) in messages">
        <message
          :message="message"
          :isNew="i < newCount"
          :source="message.source.link"
          :sourceName="message.source.name"
          :sourceType="message.source.type"
          :author="message.username"
          :text="message.text"
          :favorites="message.favorites"
          :blacklist="message.blacklist"
          :id="message.id"
          :words="currentFeed.words"
          :date="message.date"></message>
      </div>
      <resize-observer @notify="handleResize"></resize-observer>
    </div>
    <loader v-if="busy && messages[0]"></loader>
    <div v-if="!messages[0] && !$store.state.feed.actualLength && !busy">
      <p v-if="feedList.length === 0 && !feedLoading" style="color: #4f5b69; font-size: 12px; text-align: center">
        You have no data sources or feeds now.<br>
        1. To create your first data source please <router-link to="/sources?modal=change_source">click here</router-link>.<br>
        2. To create your first feed please <router-link to="/messages?feed=46&modal=add_feed">click here</router-link>.
        <br><br>
        <iframe width="560" height="315" src="https://www.youtube.com/embed/By1JKWtYliY" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
      </p>
      <p v-else-if="!$store.state.source.sourceList[0] && !$store.state.source.sourceLoading" style="color: #4f5b69; font-size: 12px; text-align: center">
        You have no data sources now. But you already have data feeds with system sources.<br>
        1. Click on one of your data feeds to check new messages.<br>
        2. To create your own first data source please <router-link to="/sources?modal=change_source">click here</router-link>.
        <br><br>
        <iframe width="560" height="315" src="https://www.youtube.com/embed/By1JKWtYliY" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
      </p>
      <p v-else style="color: #4f5b69; font-size: 12px; text-align: center">There are no messages yet.</p>
    </div>
    <div slot="modal-body">
      <modal-change-source />
      <modal-add-feed />
      <modal-change-feed @modalSave="reboot" />
    </div>
  </layout-main>
</template>

<script>
import VuePerfectScrollbar from 'vue-perfect-scrollbar';
import { mapState, mapActions, mapGetters } from 'vuex';

const allowedModals = ['change_feed', 'add_feed', 'change_source'];

export default {
  name: 'Messages',
  data() {
    return {
      modalTitle: '',
      modalShow: false,
      modalMode: null,
      newCount: 0,
      lastLoadedOffset: 0,
      query: {
        date_from: undefined,
        date_to: undefined,
        source: undefined,
      },
      selected: null,
      options: [
        { value: null, text: 'Please select an option' },
        { value: 'a', text: 'This is First option' },
        { value: 'b', text: 'Selected Option' },
        { value: { C: '3PO' }, text: 'This is an option with object value' },
        { value: 'd', text: 'This one is disabled', disabled: true },
      ],
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
      loaderOffsetTop: 0,
      error: null,
    };
  },
  computed: {
    modalGetParam() { return this.$route.query.modal; },
    ...mapGetters('feed', [
      'feedList',
      'currentFeed',
      'messages',
    ]),
    ...mapState('feed', [
      'actualLength',
      'elemCount',
      'busy',
      'feedLoading',
    ]),
    feedId() {
      return this.$route.query.feed;
    },
    feedLength() {
      return this.feedList.length;
    },
  },
  watch: {
    async modalGetParam(newValue) {
      if (newValue && allowedModals.indexOf(newValue) !== -1) {
        this.modalMode = newValue;
        this.setModalShow(true);
        switch (newValue) {
          case 'add_feed':
            this.modalTitle = 'Add feed';
            break;
          case 'change_feed':
            this.modalTitle = 'Change feed';
            break;
          case 'change_source':
            if (this.$route.query.id) {
              this.modalTitle = 'Change source';
            } else {
              this.modalTitle = 'Add my source';
            }
            break;
          default:
        }
      } else {
        this.setModalShow(false);
        if (!this.currentFeed || !(this.messages && this.messages[0])) {
          await this._setCurrentFeed(this.systemFeeds[0], this.query);
        }
      }
    },
    currentFeed(newValue) {
      if (this.$refs.messagesBlock) {
        this.$refs.messagesBlock.style.height = '0px';
      }
      if (!this.$route.query.modal) {
        this.query = {};
        this.$router.push({
          name: this.$route.name,
          query: {
            ...this.query,
            feed: newValue.id,
          },
        });
      }
    },
    async busy(newValue) {
    },
  },
  methods: {
    ...mapActions('feed', [
      'addToFavorites',
      'removeFromFavorites',
      'removeAuthorFromBlacklist',
      'getFeedList',
      'setCurrentFeed',
      'loadMessages',
      'addAuthorToBlacklist',
    ]),
    setModalShow(bool) {
      if (bool) {
        this.modalShow = true;
      } else {
        this.modalShow = false;
        const query = _.cloneDeep(this.$route.query);
        query.modal = undefined;
        this.$router.push({ name: this.$route.name, query });
      }
    },
    addAuthorToBlacklist(message) {
      this.$store.dispatch('addAuthorToBlacklist', message).then(() => { this.$redrawVueMasonry(); });
    },
    async _setCurrentFeed(feed, query) {
      if (this.$refs.messagesBlock) {
        this.$refs.messagesBlock.style.height = '0px';
      }
      this.newCount = feed.new_messages;
      if (!this.$route.query.modal) {
        this.$router.push({
          name: this.$route.name,
          feed: feed.id,
          query: { ...this.query },
        });
        this.lastLoadedOffset = 0;
        try {
          await this.setCurrentFeed({ feed, query });
          this.error = null;
        } catch (err) {
          if (err.status === 403) {
            this.error = err.body.detail;
          }
          this.$root.$emit('handleError', err);
        }
      }
    },
    async loadMore() {
      if (this.messages.length !== this.lastLoadedOffset) {
        if (!this.messages) return;
        if (!this.currentFeed) return;
        if (this.currentFeed.full_loaded) return;
        this.lastLoadedOffset = this.messages.length;
        try {
          await this.loadMessages({
            feed: this.currentFeed,
            offset: this.$store.state.feed.actualLength,
            query: this.query,
          });
        } catch (err) {
          this.$root.$emit('handleError', err);
        }
      }
    },
    higligthWords(text, words) {
      let txt = text;
      txt = txt.replace(
        new RegExp(
          '(https?://[\\S]+)(?![^<]*>|[^<>]*</)',
          'g',
        ),
        match => `<a href="${match}">${match}</a>`,
      );
      if (!words) {
        return txt;
      }
      const wordArr = [...(function* _(w) {
        const strs = w.split('\r\n');
        for (let i = 0; i < strs.length; i += 1) {
          const wrds = strs[i].split(' ');
          for (let j = 0; j < wrds.length; j += 1) {
            yield wrds[j];
          }
        }
      }(words))];

      for (let i = 0; i < wordArr.length; i += 1) {
        const word = wordArr[i];
        txt = txt.replace(
          new RegExp(`(${word})(?![^<]*>|[^<>]*</)`, 'gi'),
          match => `<span class="highlighted_word">${match}</span>`,
        );
      }
      return txt;
    },
    prettyDate(datestr) {
      const date = this.$moment.parseZone(datestr);
      return date.format('DD.MM.YYYY, HH:mm:ss');
    },
    async handleResize() {
      if (typeof this.$redrawVueMasonry === 'function') {
        await this.$redrawVueMasonry();
        const elements = document.getElementsByClassName('messages__card');
        let max = 0;
        for (const el of elements) {
          // const top = el.style.top;
          if (el.style.top > max) max = el.style.top;
        }
        this.loaderOffsetTop = max;
      }
    },
    getFilters() {
      const filters = [];
      if (this.currentFeed) {
        filters.push({
          name: 'Source',
          type: 'select',
          options: this.currentFeed.sources && this.currentFeed.sources[0]
            ? this.currentFeed.sources.concat({ link: 'All sources', id: '' })
            : this.$store.state.source.sourceList,
          label: 'link',
          value: 'id',
        });
      }
      filters.push({
        name: 'Date',
        type: 'date',
      });
      return filters;
    },
    async reboot() {
      await this._setCurrentFeed(this.currentFeed, this.query);
    },
    async setFilter(obj) {
      if (!obj) {
        this.query = {};
        return;
      }
      if (obj.filter.name === 'Date') {
        if (obj.value.start && obj.value.end) {
          console.log(obj.value.start);
          console.log(obj.value.end);
          this.query.date_from = `${obj.value.start.getFullYear()}-${obj.value.start.getMonth() + 1}-${obj.value.start.getDate()}`;
          this.query.date_to = `${obj.value.end.getFullYear()}-${obj.value.end.getMonth() + 1}-${obj.value.end.getDate()}`;
        } else {
          this.query.date_from = undefined;
          this.query.date_to = undefined;
        }
      }
      if (obj.filter.name === 'Source') {
        this.query = {
          ...this.query,
          source: obj.value ? obj.value : undefined,
        };
      }
      this._setCurrentFeed(this.currentFeed, this.query);
    },
    async _getFeedList() {
      await this.getFeedList();
      await this.$store.dispatch('source/getSourceList', true);
      if (!this.$store.state.source.count &&
           this.$store.state.feed.count &&
           this.$store.state.feed.currentFeed.id !== this.feedList[0].id) {
        await this._setCurrentFeed(this.feedList[0], this.query);
      }
    },
  },
  async created() {
    this._getFeedList();
    await this.$nextTick();
    if (this.modalGetParam && allowedModals.indexOf(this.modalGetParam) !== -1) {
      this.setModalShow(true);
      switch (this.modalGetParam) {
        case 'add_feed':
          this.modalTitle = 'Add feed';
          break;
        case 'change_feed':
          this.modalTitle = 'Change feed';
          break;
        default:
      }
    } else {
      this.setModalShow(false);
      if (!this.$route.query.feed) {
        await this._setCurrentFeed(this.systemFeeds[0], this.query);
      } else {
        const feed = await this.$store.dispatch('feed/getFeedToChange', this.$route.query.feed);
        await this._setCurrentFeed(feed, this.query);
      }
    }
  },
  components: { VuePerfectScrollbar },
};
</script>

<style scoped>
  .messages {
    width: 100%;
    margin-bottom: 15px;
    min-height: 6px;
  }
  .messages__card {
    width: 50%;
    box-sizing: border-box;
    padding: 5px 10px;
    min-width: 280px;
  }
  @media screen and (max-width: 830px) {
    .messages__card {
      width: 100%;
    }
  }
</style>
