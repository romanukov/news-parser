<template>
  <b-form class="modal-form" v-if="modalMode === 'change_feed'">
    <loader v-show="preLoading || loading"></loader>
    <div class="" v-show="!preLoading && !loading">
      <b-row class="my-4 px-5">
        <b-col sm="3" class="modal-form__label pt-1">Feed name</b-col>
        <b-col sm="9">
          <b-form-input v-model="feedToChange.name"></b-form-input>
        </b-col>
      </b-row>
      <b-row class="my-4 px-5">
        <b-col sm="3" class="modal-form__label pt-1">Keywords for search</b-col>
        <b-col sm="9">
          <b-row v-for="(word, wordIndex) in words" :key="wordIndex" class="my-2">
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
      <b-row class="row my-4 px-5" v-if="$store.state.source.sourceList.length > 0">
        <b-col sm="3" class="modal-form__label pt-1">Select sources</b-col>
        <VuePerfectScrollbar
          @ps-y-reach-end="$store.dispatch('source/getMoreSourceList')" style="max-height: 300px;" class="col-sm-9">
          <b-form-input class="mb-2" v-model="filter" placeholder="Search..."></b-form-input>
          <!--<loader v-if="!$store.state.source.sourceList[0]"></loader>-->
          <b-form-group v-if="$store.state.source.sourceList.length > 0">
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
              @click.shift="checkGroup(sourceKey)">
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
          </b-form-group>
          <loader v-if="$store.state.source.sourceLoading"></loader>
          <p
            style="color: #797c8a; font-size: 10px;"
            v-if="!$store.state.source.sourceLoading && !$store.state.source.sourceList[0]">You have no your sources. You can use available readymade sources groups below or add your own in settings.</p>
        </VuePerfectScrollbar>
      </b-row>
      <b-row class="my-4 px-5"  v-if="$store.state.source.sourceGroups.length > 0">
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
      <b-btn
        v-show="!loading"
        :disabled="loading"
        @click="changeFeed(() => {
          $router.push({
            name: $route.name,
            query: {
              modal: 'add_feed'
            }
          });
        })" variant="light" size="xs" class="w-100 mx-3 py-2 modal__button">Save & Add another</b-btn>
      <b-btn v-show="!loading" :disabled="loading" @click="changeFeed('change')" variant="light" size="xs" class="w-100 mx-3 py-2 modal__button">Save & Continue editing</b-btn>
      <b-btn v-show="!loading" :disabled="loading" @click="changeFeed(() => {$router.push({name: $route.name}); $emit('modalSave');})" variant="primary" size="xs" class="w-100 mx-3 py-2 modal__button">Save</b-btn>
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
      loading: false,
      offset: 20,
      new_sources: false,
      preLoading: true,
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
    id() {
      return this.$route.query.id;
    },
  },
  methods: {
    deleteWord(index) {
      this.words.splice(index, 1);
    },
    addWord() {
      this.words.push(new word());
    },
    isCheckedSource(id) {
      if (this.feedToChange.sources) {
        for (const source of this.feedToChange.sources) {
          if (source.id === id) return true;
        }
        return false;
      }
      return false;
    },
    isCheckedSourceGroup(id) {
      if (this.feedToChange.source_groups) {
        for (const source of this.feedToChange.source_groups) {
          if (source.id === id) return true;
        }
        return false;
      }
      return false;
    },
    checkGroup(endIndex) {
      if (endIndex > this.beginOfCheckingGroup) {
        for (let i = this.beginOfCheckingGroup; i <= endIndex; ++i) {
          this.setSource(this.filteredSourceList[i].id, true);
        }
      } else {
        for (let i = this.beginOfCheckingGroup; i >= endIndex; --i) {
          this.setSource(this.filteredSourceList[i].id, true);
        }
      }
    },
    beginCheckGroup(beginIndex) {
      this.beginOfCheckingGroup = beginIndex;
    },
    getSource(id) {
      for (const source of this.$store.state.source.sourceList) {
        if (source.id === id) return source;
      }
      return false;
    },
    getSourceGroup(id) {
      for (const source of this.$store.state.source.sourceGroups) {
        if (source.id === id) return source;
      }
      return false;
    },
    setSource(sourceId, newValue) {
      if (newValue) {
        if (this.feedToChange.sources instanceof Array) {
          this.feedToChange.sources.push(this.getSource(sourceId));
        }
      } else {
        let sourceIndex = -1;
        for (const source of this.feedToChange.sources) {
          if (source.id === sourceId) sourceIndex = this.feedToChange.sources.indexOf(source);
        }
        if (~sourceIndex) {
          this.feedToChange.sources.splice(sourceIndex, 1);
        }
      }
    },
    setSourceGroup(sourceId, newValue) {
      if (newValue) {
        if (this.feedToChange.source_groups instanceof Array) {
          this.feedToChange.source_groups.push(this.getSourceGroup(sourceId));
        }
      } else {
        let sourceIndex = -1;
        for (const source of this.feedToChange.source_groups) {
          if (source.id === sourceId) sourceIndex = this.feedToChange.source_groups.indexOf(source);
        }
        if (~sourceIndex) {
          this.feedToChange.source_groups.splice(sourceIndex, 1);
        }
      }
    },
    async changeFeed(after) {
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
        await this.$store.dispatch('feed/changeFeed', {
          new_sources: this.new_sources ? this.new_sources : false,
          id: this.id,
          name: this.feedToChange.name,
          sources: this.feedToChange.sources,
          source_groups: this.feedToChange.source_groups,
          words,
        });
        this.$root.$emit('handleNote', {
          title: 'Feed changed',
          text: `Feed '${this.feedToChange.name}' successfully changed!`,
        });
        if (after && after !== 'change') {
          after();
        } else if (after === 'change') {
        }
        this.loading = false;
      } catch (err) {
        this.$root.$emit('handleError', err);
        this.loading = false;
      }
    },
    setAllSources(newValue) {
      if (newValue) {
        this.feedToChange.sources = _.cloneDeep(this.filteredSourceList);
      } else {
        this.feedToChange.sources = [];
      }
    },
  },
  watch: {
    async id() {
      if (this.modalMode === 'change_feed') {
        this.preLoading = true;
        try {
          this.feedToChange = await this.$store.dispatch('feed/getFeedToChange', this.id);
          this.words = [];
          this.new_sources = this.feedToChange.new_sources;
          for (const word of this.feedToChange.words.split('\r\n')) {
            const predicat = word[0] === '!' ? 'not' : (word[0] === '"' ? 'precise' : 'default');
            let content = word.replace(/\s{2,}/g, ' ');
            if (predicat === 'not') {
              content = word.split('!')[1];
            } else if (predicat === 'precise') {
              content = word.split('"')[1];
            }
            this.words.push({
              predicat,
              content,
            });
          }
          this.preLoading = false;
        } catch (err) { throw err; }
      }
    },
    filter() {
      this.offset = 20;
    },
  },
  async created() {
    await this.$store.dispatch('source/getSourceGroupList');
  },
  async mounted() {
    this.preLoading = true;
    if (this.$route.query.id && this.modalMode === 'change_feed') {
      this.feedToChange = await this.$store.dispatch('feed/getFeedToChange', this.$route.query.id);
      this.new_sources = this.feedToChange.new_sources;
      this.words = [];
      if (this.feedToChange && this.feedToChange.words) {
        for (const word of this.feedToChange.words.split('\r\n')) {
          const predicat = word[0] === '!' ? 'not' : (word[0] === '"' ? 'precise' : 'default');
          let content = word.replace(/\s{2,}/g, ' ');
          if (predicat === 'not') {
            content = word.split('!')[1];
          } else if (predicat === 'precise') {
            content = word.split('"')[1];
          }
          this.words.push({
            predicat,
            content,
          });
        }
      }
      this.preLoading = false;
      try {
      } catch (err) {
        this.preLoading = false;
        throw err;
      }
    }
  },
};
</script>
