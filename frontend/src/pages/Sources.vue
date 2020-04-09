<template>
  <layout-main
    @modalToggle="setModalShow"
    :modalShow.sync="modalShow"
    :modalTitle="modalTitle"
    @scrollEnd="scrollSources"
    title="Sources"
    :sidebar="true">
    <filters
      @filterChange="setFilter"
      :class="{'show-filtered': modalShow}"
      paginatorLabel="View"
      :paginatorViewSize="showedItems.length < offset ? showedItems.length : offset"
      :paginatorMaxSize="filteredSources ? filteredSources.length : sourceList.length"
      :showNewButton="true"
      :newItemName="'source'"
      @newButtonClick="$router.push({name:$route.name, query: {modal: 'change_source'}})"
      :reverse="false"
      :filters="[]">
    </filters>
    <div
      :class="{'show-filtered': modalShow}" class="feeds mb-4">
      <p class="text-left font-weight-bold feedcol pt-2 mb-0"
         v-show="msgCount">{{msgCount.count}} messages</p>
      <b-table :stacked="adaptive" :fields="feedMap" :items="showedItems" class="bg-white">
        <template
          v-for="(headFeed, feedKey) in feedMap"
          slot-scope="data"
          :slot="'HEAD_' + headFeed">
          <div
            :key="feedKey"
            style="height: 24px;"
            v-if="headFeed === 'index'"
            class="centrify-y">
            <b-form-checkbox
              :value="true"
              :unchecked-value="false"
              v-model="indexFilter" style="margin: auto 0;">
            </b-form-checkbox>
          </div>
          <div
            v-if="headFeed !== 'index'"
            :key="feedKey"
            style="height: 24px;"
            class="feeds-table-header-elem">
            <div
              :class="{
                'm-auto': headFeed === 'Messages' || headFeed === 'Actions'
              }">
              {{data.label}}
            </div>
          </div>
        </template>
        <template
          slot-scope="data"
          :slot="contentFeed"
          v-for="(contentFeed, feedKey) in feedMap">
          <div
            :key="feedKey"
            v-if="contentFeed === 'index'"
            class="centrify-y">
            <b-form-checkbox
              :value="true"
              :unchecked-value="false"
              v-model="indexFilter" style="margin: auto 0;">
            </b-form-checkbox>
          </div>
          <div
            v-if="contentFeed === 'Link'"
            :key="feedKey"
            class="feeds-table-body feeds-table-body--words">
            <span style="display: inline-block; margin-left: 9px; font-size: 12px; font-family: 'Roboto'">
              {{data.item.link}}
              <span v-if="!data.item.active" style="display: inline-block; width: 10px; height: 10px; background-color: red; border-radius: 5px;"></span>
            </span>
          </div>
          <div
            v-if="contentFeed === 'Name'"
            :key="feedKey"
            class="feeds-table-body feeds-table-body--words">
            <span style="display: inline-block; margin-left: 9px; font-size: 12px; font-family: 'Roboto'">
              {{data.item.name}}
            </span>
          </div>
          <div
            v-if="contentFeed === 'Type'"
            :key="feedKey"
            class="feeds-table-body feeds-table-body--words">
            <span style="display: inline-block; vertical-align: top; margin-left: 5px;">
              {{ data.item.type }}
            </span>
          </div>
          <div
            v-if="contentFeed === 'Actions'"
            :key="feedKey"
            class="feeds-table-body feeds-table-body--actions">
            <span
              class="btn-action btn-action-edit"
              @click="$router.push({name:$route.name, query: {modal: 'change_source', id: data.item.id}})">
              <source-icon type="open"></source-icon>
            </span>
            <span @click="_deleteSource(data.item.id)" class="btn-action btn-action-remove">
                <source-icon type="close"></source-icon>
              </span>
          </div>
        </template>
      </b-table>
      <loader v-show="$store.state.source.sourceLoading"></loader>
      <p class="text-left font-weight-bold feedcol">{{ sourceList.length }} sources</p>
    </div>
    <div slot="modal-body">
      <modal-change-source />
      <modal-add-feed />
      <modal-change-feed />
    </div>
  </layout-main>
</template>

<style>
  @media screen and (min-width: 700px) {
  }
  .feeds-table-body--actions {
    justify-content: center;
  }
  .btn-action-edit svg {
    height: 15px;
    width: 15px;
  }
  .btn-action-remove svg {
    height: 15px;
    width: 15px;
  }
  .modal__footer {
    padding: 20px;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }
  .show-filtered {
    filter: blur(5px)
  }
  .feedcol {
    font-family: 'Roboto';
    font-size: 12px;
    padding-left: 3px;
  }
  .feeds {
    padding: 0 15px;
    padding-bottom: 40px;
    height: 100%;
    background: white;
  }
  @media screen and (max-width: 700px) {
    /*.b-table-stacked td::before {*/
    /*text-align: left !important;*/
    /*}*/
    .feeds-table-body {
      display: block !important;
    }
    .b-table-stacked .centrify-content {
      display: block;
    }
  }
  .feeds-table-header-elem {
    color: #91a7b3;
    font-family: 'Roboto';
    font-size: 15px;
    text-transform: uppercase;
    font-weight: 400;
    display: flex;
  }
  .feeds-table-body {
    display: flex;
  }
  .feeds-table-body > * {
  }
  .feeds-table-body.feeds-table-body--name {
    font-family: 'Roboto';
    font-weight: 500;
    line-height: 20px;
    padding-right: 30px;
    min-width: 199px;
  }
  .feeds-table-body.feeds-table-body--source {
    font-family: 'Roboto';
    color: #91a7b3;
    font-weight: 400;
    line-height: 20px;
    font-size: 12px;
    min-width: 150px;
  }
  .feeds-table-body .feeds-table-body--messages {
    font-family: 'Roboto';
    font-weight: 400;
    line-height: 20px;
    font-size: 12px;
    color: #189cde;
    margin: auto;
    display: flex;
    max-width: 300px;
  }
  .feeds-table-body--words {
    font-family: 'Roboto';
    font-size: 12px;
    color: #424761;
  }
  .feeds-table-body .feeds-table-body--messages-container {
    width: 20px;
    height: 20px;
    background: #ebf8ff;
    border-radius: 50%;
    display: inline-flex;
  }
  .feeds-table-body__rectangle {
    width: 20px;
    font-weight: bold;
    height: 20px;
    border-radius: 4px;
    font-size: 11px;
    text-align: center;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #EEEEEE;
    line-height: 20px;
  }
  .rect-pink {
    background-color: #a767f5;
  }
  .rect-lightblue {
    background-color: #5ea4ff;
  }
  .rect-darkblue {
    background-color:  #1A01Cc;
  }
  .rect-green {
    background-color: #9ad647;
  }
  .rect-red {
    background-color: #f56767;
  }
</style>

<script>
import { mapActions, mapState } from 'vuex';
import _ from 'lodash';

const allowedModals = ['change_feed', 'add_feed', 'change_source'];

export default {
  name: 'Feeds',
  data() {
    return {
      indexFilter: false,
      adaptive: false,
      modalTitle: 'Add feed',
      modalShow: null,
      offset: 20,
      filteredSources: null,
      msgCount: 0,
    };
  },
  watch: {
    modalGetParam(newValue) {
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
        this.modalMode = null;
        this.setModalShow(false);
      }
    },
    id(newValue) {
      switch (this.modalGetParam) {
        case 'change_source':
          if (newValue) {
            this.modalTitle = 'Change source';
          } else {
            this.modalTitle = 'Add my source';
          }
          break;
        default:
      }
    },
  },
  computed: {
    ...mapState('source', [
      'sourceList',
    ]),
    id() { return this.$route.query.id; },
    modalGetParam() {
      return this.$route.query.modal;
    },
    feedMap() {
      return ['index', 'Link', 'Name', 'Type', 'Actions'];
    },
    showedItems() {
      return this.sourceList;
    },
    filters() {
      const filters = [];
      filters.push({
        name: 'Type',
        type: 'select',
        options: [
          {
            name: 'All',
            value: 'all',
          },
          {
            name: 'Telegram',
            value: 'telegram',
          },
          {
            name: 'RSS',
            value: 'rss',
          },
          {
            name: 'Twitter',
            value: 'twitter',
          },
        ],
        label: 'name',
        value: 'value',
      });
      return filters;
    },
  },
  methods: {
    ...mapActions('feed', [
      'removeFromFavorites',
      'addToFavorites',
      'addAuthorToBlacklist',
      'removeAuthorFromBlacklist',
      'setCurrentFeed',
      'loadMessages',
      'getFeedList',
    ]),
    ...mapActions('source', [
      'deleteSource',
    ]),
    async scrollSources() {
      await this.$store.dispatch('source/getMoreSourceList');
    },
    setFilter(newValue) {
      switch (newValue.filter.name) {
        case 'Type':
          if (newValue.value === 'all') {
            this.filteredSources = null;
            this.offset = 20;
          } else if (newValue.value) {
            const result = [];
            for (const source of this.sourceList) {
              if (source.type === newValue.value) result.push(source);
            }
            this.filteredSources = result;
            this.offset = 20;
          }
          break;
        default:
      }
    },
    async _deleteSource(id) {
      try {
        await this.deleteSource(id);
      } catch (err) {
        this.$root.$emit('handleError', err);
      }
    },
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
  },
  async created() {
    try {
      await this.getFeedList();
      this.msgCount = await this.$store.dispatch('source/getMessageCount');
    } catch (err) {
      this.$root.$emit('handleError', err);
    }
    if (this.modalGetParam && allowedModals.indexOf(this.modalGetParam) !== -1) {
      this.setModalShow(true);
      switch (this.modalGetParam) {
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
            this.modalTitle = 'Add new source';
          }
          break;
        default:
      }
    } else {
      this.setModalShow(false);
    }
  },
};
</script>
