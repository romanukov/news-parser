<template>
  <b-form class="modal-form" v-if="modalMode === 'change_source'">
    <div class="">
      <b-row class="my-4 px-5">
        <b-col sm="3" class="modal-form__label">Link</b-col>
        <b-col sm="8">
          <b-form-input v-model="mutableLink"></b-form-input>
        </b-col>
      </b-row>
      <b-row class="row my-4 pl-5 pr-3">
        <b-col sm="3" class="modal-form__label">Source type</b-col>
        <div class="col-sm-9">
          <b-form-group>
            <b-form-radio
              :key="typeIndex"
              v-for="(type, typeIndex) in types"
              style="font-size: 12px; display: block"
              @change="(newValue) => { setType(type) }"
              stacked
              :value="true"
              :checked="sourceToChange && type.value === sourceToChange.type"
              name="radiosStacked">
              {{ type.name }}
            </b-form-radio>
          </b-form-group>
        </div>
      </b-row>
      <!--<b-row class="row my-4 pl-5 pr-3" v-if="sourceToChange">-->
        <!--<b-col sm="3" class="modal-form__label">Language</b-col>-->
        <!--<div class="col-sm-9">-->
          <!--<b-form-select v-model="sourceToChange.language" class="mb-2">-->
            <!--<option-->
              <!--v-for="lang in languages"-->
              <!--:value="lang.value"-->
              <!--:key="lang.value"-->
            <!--&gt;-->
              <!--{{ lang.name }}-->
            <!--</option>-->
          <!--</b-form-select>-->
        <!--</div>-->
      <!--</b-row>-->
      <b-row class="row my-4 pl-5 pr-3"
             v-if="
             sourceToChange && $store.state.auth.profile && $store.state.auth.profile.is_staff
      ">
        <b-col sm="3" class="modal-form__label">Store days</b-col>
        <div class="col-sm-9">
          <b-form-input v-model="sourceToChange.store_days"
                        class="mb-2"
                        type="number"
                        placeholder="Search...">
          </b-form-input>
        </div>
      </b-row>
    </div>
    <div class="px-5 modal__native-footer" style="display: flex; justify-content: space-between">
      <b-btn v-show="!loading" :disabled="loading"
             @click="changeSource(() => {
             setDefaultAddMode(); $router.push({name: $route.name, query: {modal: 'change_source'}})
             })"
             variant="light"
             size="xs" class="w-100 mx-3 py-2 modal__button">Save & Add another</b-btn>
      <b-btn v-show="!loading" :disabled="loading"
             @click="changeSource('change')"
             variant="light" size="xs" class="w-100 mx-3 py-2 modal__button">
        Save & Continue editing
      </b-btn>
      <b-btn v-show="!loading" :disabled="loading"
             @click="changeSource(() => {
             $router.push({name: $route.name
             })})" variant="primary" size="xs" class="w-100 mx-3 py-2 modal__button">Save</b-btn>
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
  .custom-checkbox  .custom-control-label {
    line-height: 29px;
  }
</style>
<script>
import VuePerfectScrollbar from 'vue-perfect-scrollbar';
import _ from 'lodash';

const sourceSignature = {
  link: '',
  type: 'telegram',
  language: 'NONE',
  store_days: 28,
};
export default {
  components: { VuePerfectScrollbar },
  data() {
    return {
      sourceToChange: null,
      types: [
        {
          name: 'Telegram',
          value: 'telegram',
          prefix: 'https://t.me/',
        },
        {
          name: 'Rss',
          value: 'rss',
          prefix: '',
        },
        {
          name: 'twitter',
          value: 'twitter',
          prefix: 'https://twitter.com/',
        },
      ],
      type: {
        name: 'Telegram',
        value: 'telegram',
        prefix: 'https://t.me/',
      },
      link: '',
      loading: false,
      languages: [
        {
          name: 'Russian',
          value: 'rus',
        },
        {
          name: 'English',
          value: 'eng',
        },
        {
          name: 'German',
          value: 'deu',
        },
        {
          name: 'Dutch',
          value: 'nld',
        },
      ],
    };
  },
  computed: {
    mutableLink: {
      get() {
        return this.type.prefix + this.link;
      },
      set(newValue) {
        const prefix = this.type.prefix;
        if (prefix && newValue.indexOf(prefix) === -1) {
          this.link = '';
        } else {
          this.link = newValue.replace(prefix, '');
        }
      },
    },
    modalMode() {
      return this.$route.query.modal;
    },
    id() {
      return this.$route.query.id;
    },
  },
  methods: {
    async getSource(id) {
      try {
        return await this.$store.dispatch('source/getSource', id);
      } catch (err) {
        return null;
      }
    },
    async changeSource(after) {
      this.loading = true;
      try {
        if (this.id) {
          await this.$store.dispatch('source/putSource', {
            id: this.id,
            link: this.link,
            type: this.type.value,
            language: this.sourceToChange.language,
            store_days: this.sourceToChange.store_days,
          });
          this.$root.$emit('handleNote', {
            title: 'Source changed',
            text: `Source ${this.link} successfully changed!`,
          });
          if (after && after !== 'change') {
            after();
          }
          this.loading = false;
        } else {
          const response = await this.$store.dispatch('source/createSource', {
            link: this.link,
            type: this.type.value,
            language: this.sourceToChange.language,
            store_days: this.sourceToChange.store_days,
          });
          this.$root.$emit('handleNote', {
            title: 'Source created',
            text: `Source ${this.link} successfully created!`,
          });
          if (after && after !== 'change') {
            after();
          } else if (after === 'change') {
            this.$router.push({
              name: this.$route.name,
              query: {
                modal: 'change_source',
                id: response.id,
              },
            });
          }
          this.loading = false;
        }
      } catch (err) {
        this.$root.$emit('handleError', err);
        this.loading = false;
      }
    },
    setType(type) {
      this.type = type;
      if (this.sourceToChange) {
        this.sourceToChange.type = type.value;
      }
    },
    setDefaultAddMode() {
      this.sourceToChange = _.cloneDeep(sourceSignature);
      this.link = '';
    },
  },
  watch: {
    async id(newValue) {
      if (this.modalMode === 'change_source') {
        if (newValue) {
          try {
            this.sourceToChange = await this.getSource(this.id);
          } catch (err) { throw err; }
        } else {
          this.setDefaultAddMode();
        }
      }
    },
  },
  async created() {
    this.type = this.types[0];
    if (this.id && this.modalMode === 'change_source') {
      try {
        this.sourceToChange = await this.getSource(this.id);
        if (!this.sourceToChange) {
          const query = _.cloneDeep(this.$route.query);
          query.id = undefined;
          this.$router.push({
            name: this.$route.name,
            query,
          });
          this.setDefaultAddMode();
        } else {
          this.link = this.sourceToChange.link;
          for (let i = 0; i < this.types.length; i += 1) {
            if (this.sourceToChange.type === this.types[i].value) {
              this.type = this.types[i];
            }
          }
        }
      } catch (err) {
        this.setDefaultAddMode();
      }
    } else {
      this.setDefaultAddMode();
    }
  },
};
</script>
