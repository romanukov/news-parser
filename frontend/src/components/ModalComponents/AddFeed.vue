<template>
  <b-form class="modal-form" v-if="modalMode === 'add_feed'">
    <div class="">
      <b-row class="my-4 px-5">
        <b-col sm="3" class="modal-form__label pt-1">Feed name</b-col>
        <b-col sm="9">
          <b-form-input v-model="name"></b-form-input>
        </b-col>
      </b-row>
      <b-row class="my-4 px-5">
        <b-col sm="3" class="modal-form__label pt-1">Keywords for search</b-col>
        <b-col sm="9">
          <b-row v-for="(word, wordIndex) in words" :key="wordIndex" class="mb-2">
            <div class="col" style="display: flex" sm="12">
              <b-form-select v-model="word.predicat" style="width: 66px;">
                <option value="default" selected>DEFAULT</option>
                <option value="not">NOT</option>
                <option value="precise">PRECISE</option>
              </b-form-select>
              <b-form-input class="ml-2" v-model="word.content" placeholder="Key word..."></b-form-input>
              <b-link @click="deleteWord(wordIndex)" class="text-danger ml-2" style="line-height: 28px; font-size: 11px;">Delete</b-link>
            </div>
          </b-row>
          <div>
            <b-link @click="addWord" style="font-size: 11px;" class="mt-2 font-weight-bold">+ New</b-link>
          </div>
          <p style="color: #797c8a; font-size: 10px;">Leave empty if you want to get all messages from chosen sources without filter.</p>
        </b-col>
      </b-row>
      <b-row class="row my-4 px-5">
        <b-col sm="3" class="modal-form__label pt-1">Select sources</b-col>
        <VuePerfectScrollbar
          @ps-y-reach-end="$store.dispatch('source/getMoreSourceList')"
          style="max-height: 250px;" class="col-sm-9">
          <b-form-input class="mb-2" v-model="filter" placeholder="Search..."></b-form-input>
          <b-form-group>
            <b-form-checkbox
              style="font-size: 12px; display: block"
              :value="true"
              @change="(newValue) => { setAllSources(newValue) }"
              stacked
              name="radiosStacked">
              All sources
            </b-form-checkbox>
            <div
              v-for="(source, sourceKey) in filteredSourceList"
              @click.exact="beginCheckGroup(sourceKey)"
              @click.shift.exact="checkGroup(sourceKey)">
              <b-form-checkbox
                v-if="filteredSourceList[0]"
                :key="sourceKey"
                style="font-size: 12px; display: block"
                :checked="isCheckedSource(source.id)"
                :value="true"
                :unchecked-value="false"
                @change="(newValue) => { setSource(source.id, newValue) }"
                stacked
                name="radiosStacked">
                {{ source.link }}
              </b-form-checkbox>
            </div>
            <loader v-if="$store.state.source.sourceLoading"></loader>
          </b-form-group>
        </VuePerfectScrollbar>
      </b-row>
      <b-row class="my-4 px-5">
        <b-col sm="3" class="modal-form__label pt-1">Available sources groups</b-col>
        <b-col sm="9">
          <VuePerfectScrollbar
            @ps-y-reach-end="() => { if (realLength > offset) offset+=20 }"
            style="max-height: 250px; padding: 0;" class="col-sm-9">
            <b-form-group>
                <b-form-checkbox
                  v-for="(sourceGroup, sourceGroupKey) in sourceGroupsList"
                  :key="sourceGroupKey"
                  style="font-size: 12px; display: block"
                  :checked="isCheckedSourceGroup(sourceGroup.id)"
                  :value="true"
                  :unchecked-value="false"
                  @change="(newValue) => { setSourceGroup(sourceGroup.id, newValue) }"
                  stacked
                  name="radiosGroupsStacked">
                  {{ sourceGroup.name }}
                </b-form-checkbox>
            </b-form-group>
          </VuePerfectScrollbar>
        </b-col>
      </b-row>
      <b-row class="my-4 px-5">
        <b-col sm="3" class="modal-form__label pt-1">Add all new sources to this feed</b-col>
        <b-col sm="9">
          <b-form-checkbox
            style="font-size: 12px; display: block; position: relative; top: -2px"
            :value="true"
            :checked="new_sources"
            @change="(newValue) => { new_sources = newValue }"
            stacked>
          </b-form-checkbox>
        </b-col>
      </b-row>
    </div>
    <div class="px-5 modal__native-footer" style="display: flex; justify-content: space-between">
      <b-btn v-show="!loading" :disabled="loading" @click="createFeed(() => {setDefaultAddMode(); $router.push({name: $route.name, query: {modal: 'add_feed'}})})" variant="light" size="xs" class="w-100 mx-3 py-2 modal__button">Save & Add another</b-btn>
      <b-btn v-show="!loading" :disabled="loading" @click="createFeed('change')" variant="light" size="xs" class="w-100 mx-3 py-2 modal__button">Save & Continue editing</b-btn>
      <b-btn v-show="!loading" :disabled="loading" @click="createFeed(() => {$router.push({name: $route.name})})" variant="primary" size="xs" class="w-100 mx-3 py-2 modal__button">Save</b-btn>
      <loader v-show="loading"></loader>
    </div>
  </b-form>
</template>
<style>
  .ps__scrollbar-y-rail {
    background-color: rgba(220,220,220,0.5) !important;
  }
  .modal__native-footer {
    display: flex;
    border-top: 1px solid #e9ecef;
    width: 100%;
    padding: 30px 20px;
    background: #fafbfc;
  }
  .custom-control-label {
    line-height: 24px;
  }
</style>
<script>
import _ from 'lodash';
import VuePerfectScrollbar from 'vue-perfect-scrollbar';

class word {
  constructor(word = {}) {
    this.predicat = word.predicat ? word.predicat : 'default';
    this.content = word.content ? word.content : '';
  }
}
export default {
  components: { VuePerfectScrollbar },
  data() {
    return {
      feedToChange: {},
      words: [new word()],
      filter: '',
      name: '',
      sources: [],
      sourceGroups: [],
      offset: 20,
      new_sources: false,
      beginOfCheckingGroup: null,
      loading: false,
    };
  },
  computed: {
    realLength() {
      const sources = this.$store.state.source.sourceList;
      if (this.filter) {
        const result = [];
        for (const source of sources) {
          if (~source.link.indexOf(this.filter)) result.push(source);
        }
        return result.length;
      }
      return sources.length;
    },
    filteredSourceList() {
      const sources = this.$store.state.source.sourceList;
      if (this.filter) {
        const result = [];
        for (const source of sources) {
          if (~source.link.indexOf(this.filter)) result.push(source);
        }
        return result.slice(0, this.offset);
      }
      return sources.slice(0, this.offset);
    },
    sourceGroupsList() {
      return this.$store.state.source.sourceGroups;
    },
    modalMode() {
      return this.$route.query.modal;
    },
  },
  methods: {
    setDefaultAddMode() {
      this.sources = [];
      this.name = '';
      this.new_sources = false;
      this.words = [new word()];
    },
    onScroll(arg) {
    },
    deleteWord(index) {
      this.words.splice(index, 1);
    },
    addWord() {
      this.words.push(new word());
    },
    isCheckedSource(id) {
      if (this.sources) {
        for (const source of this.sources) {
          if (source.id === id) return true;
        }
        return false;
      }
      return false;
    },
    isCheckedSourceGroup(id) {
      if (this.sourceGroups) {
        for (const source of this.sourceGroups) {
          if (source.id === id) return true;
        }
        return false;
      }
      return false;
    },
    getSource(id) {
      for (const source of this.$store.state.source.sourceList) {
        if (source.id === id) return source;
      }
      return false;
    },
    getSourceGroup(id) {
      for (const sourceGroup of this.$store.state.source.sourceGroups) {
        if (sourceGroup.id === id) return sourceGroup;
      }
      return false;
    },
    setSourceGroup(sourceId, newValue) {
      if (newValue) {
        if (this.sourceGroups instanceof Array) {
          this.sourceGroups.push(this.getSourceGroup(sourceId));
        }
      } else {
        let sourceIndex = -1;
        for (const source of this.sourceGroups) {
          if (source.id === sourceId) sourceIndex = this.sourceGroups.indexOf(source);
        }
        if (~sourceIndex) {
          this.sourceGroups.splice(sourceIndex, 1);
        }
      }
    },
    setSource(sourceId, newValue) {
      if (newValue) {
        if (this.sources instanceof Array) {
          this.sources.push(this.getSource(sourceId));
        }
      } else {
        let sourceIndex = -1;
        for (const source of this.sources) {
          if (source.id === sourceId) sourceIndex = this.sources.indexOf(source);
        }
        if (~sourceIndex) {
          this.sources.splice(sourceIndex, 1);
        }
      }
    },
    setAllSources(newValue) {
      if (newValue) {
        this.sources = _.cloneDeep(this.$store.state.source.sourceList);
      } else {
        this.sources = [];
      }
    },
    async checkGroup(endIndex) {
      await this.$nextTick(() => {
        if (endIndex > this.beginOfCheckingGroup) {
          for (let i = this.beginOfCheckingGroup; i <= endIndex; ++i) {
            this.setSource(this.filteredSourceList[i].id, true);
          }
        } else {
          for (let i = this.beginOfCheckingGroup; i >= endIndex; --i) {
            this.setSource(this.filteredSourceList[i].id, true);
          }
        }
      });
    },
    beginCheckGroup(beginIndex) {
      this.beginOfCheckingGroup = beginIndex;
    },
    async createFeed(after) {
      this.loading = true;
      try {
        let words = '';
        for (const word of this.words) {
          if (word.predicat === 'default') {
            words += `${word.content}\r\n`;
          } else if (word.predicat === 'not') {
            words += `!${word.content}\r\n`;
          } else if (word.predicat === 'precise') {
            words += `"${word.content}"\r\n`;
          }
        }
        const response = await this.$store.dispatch('feed/createFeed', {
          new_sources: this.new_sources,
          name: this.name,
          sources: this.sources,
          source_groups: this.sourceGroups,
          words,
        });
        this.$root.$emit('handleNote', {
          title: 'Feed created',
          text: `Feed '${this.name}' successfully created!`,
        });
        if (after && after !== 'change') {
          after(response);
        } else if (after === 'change') {
          this.$router.push({
            name: this.$route.name,
            query: {
              modal: 'change_feed',
              id: response.id,
            },
          });
        }
        this.loading = false;
      } catch (err) {
        this.$root.$emit('handleError', err);
        this.loading = false;
      }
    },
  },
  watch: {
    filter() {
      this.offset = 20;
    },
  },
  async created() {
    await this.$store.dispatch('source/getSourceGroupList');
  },
};
</script>
