<template>
  <b-card class="message">
    <slot></slot>
    <div class="message__header" :class="message.new ? 'message__header--new' : ''">
      <div class="message__source-type">
        <source-icon :type="sourceType"></source-icon>
      </div>
      <div class="message__source" :title="source">
        {{ sourceName ? sourceName : source }}
      </div>
      <div v-show="author" class="message__author">
        {{ author }}
      </div>
      <div
        v-if="!disablePopovers"
         @mouseover="setShowPopover(true)"
         @mouseleave="setShowPopover(false)"
         class="message__dropdown ml-auto"
         style="cursor: pointer"
         :id="'message' + id">
        <source-icon class="message__dropdown-icon" mode="ios" type="arrowDown" style=""></source-icon>
      </div>
    </div>
    <transition name="fade">
      <b-popover
        :show.sync="popoverShow"
        placement="bottom" :target="'message' + id">
        <div
          v-if="!favorites"
          @mouseover="setShowPopover(true)"
          @click="addToFavorites(message); setShowPopover(false, true)"
          @mouseleave="setShowPopover(false)" class="popover__link">
          <source-icon mode="md" class="star" type="star"></source-icon>
          <span>Add to favorites</span>
        </div>
        <div
          v-if="favorites"
          @mouseover="setShowPopover(true)"
          @click="removeFromFavorites(message); setShowPopover(false, true)"
          @mouseleave="setShowPopover(false)" class="popover__link">
          <source-icon mode="md" class="star" type="star"></source-icon>
          <span style="white-space: nowrap">Remove from favorites</span>
        </div>
        <div
          v-if="!blacklist"
          @mouseover="setShowPopover(true)"
          @click="addAuthorToBlacklist(message); setShowPopover(false, true)"
          @mouseleave="setShowPopover(false)" class="popover__link">
          <source-icon mode="ios" class="block" type="block"></source-icon>
          <span>Block author</span>
        </div>
        <div
          v-if="blacklist"
          @mouseover="setShowPopover(true)"
          @click="removeAuthorFromBlacklist(message); setShowPopover(false, true)"
          @mouseleave="setShowPopover(false)" class="popover__link">
          <source-icon mode="ios" class="block" type="block"></source-icon>
          <span>Remove author from blacklist</span>
        </div>
      </b-popover>
    </transition>
    <p v-show="message.duplicates_count" style="font-size: 11px; margin: 0; padding: 0;">
      Duplicates: {{message.duplicates_count}} in
      {{ message.duplicates_sources_count === 1 ? 'this source' : `${message.duplicates_sources_count} sources` }}
    </p>
    <div style="font-size: 13px; font-family: 'Roboto'; white-space: pre-line; padding-bottom: 8px;" v-html="higligthWords"></div>
    <div class="website-preview" v-if="message.meta && message.meta.preview">
      <div class="website-preview__site-name">{{ message.meta.preview.site_name }}</div>
      <div class="website-preview__title">{{ message.meta.preview.title }}</div>
      <div class="website-preview__description">
        {{ message.meta.preview.description }}
      </div>
      <div class="website-preview__url">
        <a :href="message.meta.preview.url">{{ message.meta.preview.display_url }}</a>
      </div>
    </div>
    <div>

      <div v-if="message.meta && message.meta.big_file_size">
        <div class="attachement-badge">
          <source-icon mode="md" class="share" type="attach"></source-icon>
          <span>
            Attached files are bigger than 10mb. Please open the original
            message to view them by the following <a :href="link" target="_blank">link</a>
          </span>
        </div>
      </div>
      <div v-if="filesImage.length > 0">
        <div class="attachement-badge">
          <source-icon mode="md" class="share" type="photo"></source-icon>
          <span>Attached photos</span>
        </div>
        <div>
          <a :href="file.file" :key="file.file" v-for="file in filesImage" target="_blank">
            <img :src="file.file" height="100" alt="" />
          </a>
        </div>
      </div>
      <div v-if="filesVideo.length > 0">
        <div class="attachement-badge">
          <source-icon mode="md" class="share" type="video"></source-icon>
          <span>Attached videos</span>
        </div>
        <div>
          <VideoThumbnailModal :key="item.file"
                               v-for="(item, index) in filesVideo"
                               :videoUrl="item.file">
          </VideoThumbnailModal>
        </div>
      </div>
      <div v-if="filesOther.length > 0">
        <div class="attachement-badge">
          <source-icon mode="md" class="share" type="attach"></source-icon>
          <span>Attached files</span>
        </div>
        <div><a :href="file.file" style="font-size: 12px;" :key="file.file"
                v-for="file in filesOther">{{file.file}}</a></div>
      </div>
    </div>
    <div class="message__footer">
      <div class="message__link">
        <div>
          <b-link :href="link" target="_blank" v-show="link">
            {{ link }}
          </b-link>
        </div>

        <div v-if="sourceType === 'telegram'">
          <b-link :href="'tg://resolve?domain=' + message.source.link + '&post=' + message.internal_id" target="_blank" v-show="link">
            tg://resolve?domain={{ message.source.link }}&post={{ message.internal_id }}
          </b-link>
        </div>

      </div>
      <div
        v-if="!disablePopovers"
        @click="_shareMessage(id)"
        class="message__share-link"
         :id="'share' + id">
          <source-icon mode="md" class="share" type="share"></source-icon>
          <span>Share</span>
      </div>
      <transition name="fade">
        <b-popover
          class="popover__share-popover"
          v-if="shareShow"
          :show.sync="shareShow"
          placement="bottom" :target="'share' + id">
          <div
            @mouseleave="setShareShow(false)"
            class="popover__share-container">
            <input v-model="shareInput" type="text">
            <b-btn
              @click="copyLink(shareInput); setShareShow(false, true)"
              variant="primary"
              size="sm">Copy</b-btn>
          </div>
        </b-popover>
      </transition>
      <div class="message__date"><a  :href="'http://' + link" target="_blank">
        {{localDate}}
      </a></div>
    </div>
  </b-card>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import moment from 'moment';
import VideoThumbnailModal from './VideoThumbnailModal';

export default {
  name: 'Message',
  components: { VideoThumbnailModal },
  data() {
    return {
      popoverShow: false,
      shareShow: false,
      timerId: null,
      important: false,
      videoModal: null,
      types: [
        {
          name: 'Telegram',
          value: 'telegram',
          prefix: 'https\://t.me/',
        },
        {
          name: 'Rss',
          value: 'rss',
          prefix: '',
        },
        {
          name: 'twitter',
          value: 'twitter',
          prefix: 'https\://twitter.com/',
        },
      ],
      shareInput: '',
    };
  },
  props: {
    source: String,
    sourceType: String,
    sourceName: String,
    author: String,
    text: String,
    date: String,
    words: String,
    id: Number,
    isNew: Boolean,
    message: Object,
    favorites: Boolean,
    blacklist: Boolean,
    disablePopovers: Boolean,
  },
  computed: {
    ...mapState('auth', ['profile']),
    filesImage() {
      const files = [];
      if ((this.message.meta !== null) && ('media' in this.message.meta)) {
        this.message.meta.media.forEach((media) => {
          if (media.type === 'photo') {
            files.push({ file: media.media_url });
          }
        });
      }
      if ((this.message.meta !== null) && ('preview' in this.message.meta)) {
        if (('image' in this.message.meta.preview)) {
          files.push({ file: this.message.meta.preview.image });
        }
      }
      this.message.files.filter(
        file => ['jpg', 'png', 'webp', 'gif'].indexOf(this.getFileExtension(file.file)) > -1,
      ).forEach((media) => {
        files.push({ file: media.file });
      });
      return files;
    },
    filesVideo() {
      const files = [];
      if ((this.message.meta !== null) && ('media' in this.message.meta)) {
        this.message.meta.media.forEach((media) => {
          if (media.type === 'video') {
            files.push({ file: media.media_url });
          }
        });
      }
      this.message.files.filter(
        file => ['avi', 'mp4'].indexOf(this.getFileExtension(file.file)) > -1,
      ).forEach((media) => {
        files.push({ file: media.file });
      });
      return files;
    },
    filesOther() {
      const files = [];
      if ((this.message.meta !== null) && ('media' in this.message.meta)) {
        this.message.meta.media.forEach((media) => {
          if ((media.type !== 'video') && (media.type !== 'photo')) {
            files.push({ file: media.media_url });
          }
        });
      }
      this.message.files.filter(
        file => ['avi', 'mp4', 'jpg', 'png', 'webp', 'gif'].indexOf(this.getFileExtension(file.file)) === -1,
      ).forEach((media) => {
        files.push({ file: media.file });
      });
      return files;
    },
    hasFiles() {
      return (
        (this.filesImage.length > 0) ||
        (this.filesVideo.length > 0) ||
        (this.filesOther.length > 0)
      );
    },
    localDate() {
      const date = moment.parseZone(this.date);
      return date.format('DD.MM.YYYY, HH:mm:ss');
    },
    wordArr() {
      if (this.words) {
        const wordArr = [];
        let word = '';
        let quote = false;
        for (const ch of this.words) {
          if (ch === '\"') {
            quote = !quote;
          }
          if ((ch !== '\n' && ch !== ' ') || quote) {
            word += ch;
          } else {
            if (word[word.length - 1] === '\r') {
              word = word.slice(0, word.length - 1);
            }
            wordArr.push(word);
            word = '';
          }
        }
        wordArr.push(word);
        return wordArr;
      }
      return [];
    },
    higligthWords() {
      let txt = this.text;
      txt = txt.replace(
        /\[([^\]]+)\]\(([^\)]+)\)/g,
        '<a href="$2" target="_blank">$1</a>',
      );
      txt = txt.replace(
        new RegExp(
          '(https?://[\\S]+)(?![^<]*>|[^<>]*</)',
          'g',
        ),
        match => `<a href="${match}" target="_blank">${match}</a>`,
      );
      if (!this.wordArr || !this.wordArr[0]) {
        return txt;
      }
      for (let i = 0; i < this.wordArr.length; i += 1) {
        if (this.wordArr[i].length > 0) {
          const word = this.wordArr[i].replace(/"/g, '\\b');
          txt = txt.replace(
            new RegExp(`(?<!<[^>]*)${word}`, 'gi'),
            match => `<span class="highlighted_word">${match}</span>`,
          );
        }
      }
      return txt;
    },
    link() {
      let pref;
      let _link = '';
      for (const type of this.types) {
        if (this.sourceType === type.value) pref = type.prefix;
      }
      if (pref) {
        _link = `${pref + this.source}/`;
      } else return null;
      if (this.sourceType === 'twitter') {
        _link = `${_link}status/`;
      }
      if (this.message.internal_id) {
        return `${_link}${this.message.internal_id}/`;
      }
      return _link;
    },
  },
  methods: {
    ...mapActions('feed', [
      'removeFromFavorites',
      'addToFavorites',
      'addAuthorToBlacklist',
      'removeAuthorFromBlacklist',
      'getFeedList',
      'setCurrentFeed',
      'loadMessages',
      'shareMessage',
    ]),
    getFileExtension(fname) {
      return fname.slice((Math.max(0, fname.lastIndexOf('.')) || Infinity) + 1);
    },
    setShowPopover(bool, important) {
      if (this.timerId && !this.important) {
        clearTimeout(this.timerId);
        this.timerId = null;
      }
      if (important) this.important = true;
      this.timerId = setTimeout(() => {
        this.popoverShow = bool;
        this.important = false;
      }, 100);
    },
    copyLink(link) {
      navigator.clipboard.writeText(link);
      document.execCommand('copy', link);
    },
    setShareShow(bool, important) {
      if (this.timerId && !this.important) {
        clearTimeout(this.timerId);
        this.timerId = null;
      }
      if (important) this.important = true;
      this.timerId = setTimeout(() => {
        this.shareShow = bool;
        this.important = false;
      }, 100);
    },
    async _shareMessage(id) {
      await this.shareMessage(id);
      this.shareInput = `https://app.samfeeds.com/shared/${id}/`;
      this.setShareShow(true);
    },
  },
};
</script>

<style>
  .message__header--new::before {
    background: #72b317;
    width: 6px;
    content: '';
    height: 6px;
    position: absolute;
    left: 7px;
    top: 22px;
    border-radius: 50%;
  }
  .popover {
    top: -10px !important;
  }
  .popover-body {
    padding: 0 !important;
    width: auto;
    min-width: 170px;
  }
  .popover__link {
    font-size: 12px;
    padding: 0.5rem 0.75rem;
    cursor: pointer;
  }
  .popover__link:hover {
    background: #eaeaea;
  }
  .popover__link span {
    position: relative;
    top: -2px;
    left: 5px;
  }
  .popover__link .star {
    fill: #f5c223;
    width: 15px;
    height: 15px;
  }
  .popover__link .block {
    fill: #ff3939;
    width: 15px;
    height: 15px;
  }
  .message__dropdown-icon {
    fill: #91a7b3 !important;
    position: relative;
    top: -2px;
  }
  .highlighted_word {
    color: red;
  }
  .message__footer {

    margin-top: 5px;
    font-size: 12px;
  }
  .message__link a {
    color: #189cde;
  }
  .message__link {
  }
  .message__share-link {
    margin-left: 5px;
    cursor: pointer;
    color: #aaaaaa;
    font-weight: 600;
  }
  .message__share-link:hover {
    color: #888;
  }
  .message__footer > div {
    display: block;
    float: left;
  }
  .message__date {
    float: right !important;
    color: #8298ad;
  }
  .message__date a {
    color: #8298ad;
  }
  .message__header {
    display: flex;
    padding: 0 0 4px 0;
    line-height: 22px;
  }
  .message {
    border-radius: 8px;
  }
  .message__source {
    color: #189cde;
    font-weight: bold;
    font-size: 12px;
    line-height: 17px;
  }
  .message__source-type {
    color: #189cde;
    font-weight: bold;
    margin-right: 8px;
  }
  .message__source-type::before {
    /*content: '';*/
    position: absolute;
    left: 8px;
    top: 22px;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #72b317;
  }
  .message__author {
    color: #8298ad;
    font-weight: bold;
    font-size: 12px;
    padding-left: 4px;
    line-height: 17px;
  }

  .message__author:before {
    content: "|";
    padding: 0 5px;
    font-weight: bold;
    display: inline;
  }
  .share {
    fill: #aaaaaa !important;
    margin-right: 4px;
  }
  .share svg {
    height: 16px;
    width: auto;
  }
  .popover__share-container {
    max-width: 600px !important;
    width: 100% !important;
    padding: 15px 20px;
  }
  .popover__share-container input {
    width: 250px;
    height: 30px;
    border: 1px solid #aaa;
    position: relative;
    top: 1px;
    left: 3px;
    border-radius: 2px 0 0 2px;
    font-size: 12px;
    padding: 0 10px;
    color: #777;
  }
  .popover__share-container button {
    background: #1c97c8;
    border-radius: 0 2px 2px 0;
    color: white;
    border: 0;
    height: 30px;
    padding-left: 15px !important;
    padding-right: 15px !important;
  }

  .popover__share-popover {
    max-width: 600px !important;
    width: 100% !important;

  }
  .attachement-badge {
    font-size: 12px;
    font-family: 'Roboto';
    line-height: 1.38;
    white-space: pre-line;
    color: #aaaaaa;
    font-weight: 500;
    margin: 4px 0;
  }
  .website-preview {
    display: block;
    border-left: solid 2px #0d85b7;
    padding: 0 8px;
    font-family: 'Roboto';
    font-weight: 400;
    font-size: 12px;
  }
  .website-preview__title {
    font-weight: 600;
  }
  .website-preview__site-name {
    font-weight: 600;
    color: #0e90d2;
  }
</style>
