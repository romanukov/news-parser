<template>
  <layout-main
    @modalToggle="setModalShow"
    :modalShow.sync="modalShow"
    :modalTitle="modalTitle"
    title="Telegram Watcher administration"
    :sidebar="true">
    <p style="font-size: 15px; font-family: 'Roboto'; font-weight: 600; line-height: 18px; margin-top: 20px;">
      <source-icon style="position: relative; top: 4px;margin: 0 5px;" type="telegram"></source-icon>
      Telegram watcher
    </p>
    <div class="cards-container">
      <div class="custom-card">
        <div class="card__header">
          <source-icon mode="ios" type="disc" style="fill: #91a7b3; height: 24px; width: 24px;"></source-icon>
          <span>Feeds</span>
        </div>
        <div class="card__body">
          <span class="card__body--current">{{ $store.state.feed.count }}</span>
        </div>
        <div class="card__footer">
          <b-btn @click="$router.push({name:$route.name,query:{modal:'add_feed'}})" size="xs" variant="primary">
            <source-icon mode="ios" type="disc"></source-icon>
            Add
          </b-btn>
          <b-btn @click="$router.push('/feeds')" size="xs" variant="light">
            <source-icon mode="md" type="create"></source-icon>
            Change
          </b-btn>
        </div>
      </div>
      <div class="custom-card">
        <div class="card__header">
          <source-icon mode="md" type="person" style="fill: #91a7b3; height: 24px; width: 24px;"></source-icon>
          <span>My sources</span>
        </div>
        <div class="card__body">
          <span class="card__body--current">{{ $store.state.source.count }}</span>
        </div>
        <div class="card__footer">
          <b-btn size="xs" variant="primary" @click="$router.push({name:$route.name, query: {modal:'change_source'}})">
            <source-icon mode="ios" type="disc"></source-icon>
            Add
          </b-btn>
          <b-btn size="xs" variant="light" @click="$router.push('/sources/')">
            <source-icon mode="md" type="create"></source-icon>
            Change
          </b-btn>
        </div>
      </div>
    </div>
    <div slot="modal-body">
      <modal-add-feed />
      <modal-change-feed />
      <modal-change-source />
    </div>
  </layout-main>
</template>

<style>
  .card__body--current {
    color: #189cde;
  }
  .custom-card {
    margin: auto;
    background: #fff;
    width: 190px;
    display: inline-block;
    margin-left: 3px;
    margin-top: 5px;
  }
  .cards-container .card-body {
    padding: 0 !important;
  }
  .card__header {
    width: 100%;
    padding: 14px 16px;
    font-size: 15px;
    font-family: 'Roboto';
    font-weight: 500;
  }
  .card__header svg {
    width: 26px;
    height: 26px;
  }
  .card__header span {
    position: relative;
    top: -4px;
    left: 4px;
  }
  .card__body {
    width: 100%;
    padding: 14px 16px 30px 16px;
    font-family: 'Roboto';
    font-weight: 500;
    text-align: center;
    font-size: 30px;
  }
  .card__footer {
    background: #fafbfc;
    padding: 22px 17px;
    display: flex;
    justify-content: space-between;
  }
</style>
<script>
const allowedModals = ['change_feed', 'add_feed', 'add_source', 'change_source'];
export default {
  data() {
    return {
      modalTitle: '',
      modalShow: false,
      modalMode: null,
    };
  },
  computed: {
    modalGetParam() { return this.$route.query.modal; },
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
              this.modalTitle = 'Add new source';
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
      if (!this.$route.query.modal) {
        if (newValue !== this.currentFeed) {
          this.query = {};
          this.$router.push({
            name: this.$route.name,
            query: { ...this.query },
          });
        }
      }
    },
  },
  methods: {
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
