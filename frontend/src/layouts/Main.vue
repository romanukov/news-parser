<template>
  <div class="layout">
    <sidebar :show="sidebar" @newButtonClick="$emit('sidebarNewButtonClick')" />
    <div class="layout__screen">
      <b-navbar toggleable="md" type="light" variant="light" class="layout__navbar">
        <b-navbar-toggle target="nav_collapse"></b-navbar-toggle>
        <b-collapse is-nav id="nav_collapse" style="background: #f8f9fa;
    padding: 5px 10px;">
          <b-navbar-brand href="#" class="my-navbar-brand">
            {{ navbarHeader }}
          </b-navbar-brand>
          <!-- Right aligned nav items -->
          <b-navbar-nav class="ml-auto">
            <b-nav-item v-if="profile" style="font-size: 12px; line-height: 20px; margin-right: 28px;" href="#" right>
              <span class="font-weight-bold" style="font-size: 12px; color: #424761;">Welcome, {{profile.username}}</span>
            </b-nav-item>
            <b-nav-item @click="$router.push('/profile/')" style="font-size: 11px; line-height: 20px;" href="#" right>
              <span>Profile</span>
              <span style="margin-left: 10px;">|</span>
            </b-nav-item>
            <b-nav-item @click="$router.push('/settings/')" style="font-size: 11px; line-height: 20px;" href="#" right>
              <span>Settings</span>
              <span></span>
            </b-nav-item>
            <b-nav-item style="font-size: 11px; line-height: 20px;" right class="layout__navbar-text-wrapper">|</b-nav-item>
            <b-nav-item @click="openHelp" target="_blank" style="font-size: 11px; line-height: 20px;" href="#" right>
              <span>Help</span>
              <span style="margin-left: 10px;">|</span>
            </b-nav-item>
            <b-nav-item style="font-size: 11px; line-height: 20px;" href="#" right @click="$store.dispatch('auth/logout'); $router.push('/login/')">
              <span>
                Logout
                <source-icon type="exit" mode="md" style="fill: #91a7b3"></source-icon>
              </span>
            </b-nav-item>
          </b-navbar-nav>
        </b-collapse>
      </b-navbar>
      <VuePerfectScrollbar
        ref="app"
        :settings="{
          suppressScrollX: true,
        }"
        :suppress-scroll-x="true"
        @ps-y-reach-end="() => { $emit('scrollEnd') }" class="layout__content" :class="!sidebar ? 'content--full' : ''">
        <div class="layout__content-main"
             style="padding-left: 10px; padding-right: 10px;">
          <slot></slot>
        </div>
      </VuePerfectScrollbar>
    </div>
    <modal v-if="_modalShow"
           @modalSave="$emit('modalChangeSourceSave')"
           @modalToggle="(newValue) => {_modalShow = newValue}"
           :title="modalTitle" :show.sync="_modalShow">
      <div slot="body">
        <slot name="modal-body"></slot>
      </div>
      <div slot="footer">
        <slot name="modal-footer"></slot>
      </div>
    </modal>
  </div>
</template>

<style scoped>
  .layout {
    display: flex;
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    overflow: hidden;
  }
  @media screen and (max-width: 767px) {
    .layout__navbar-text-wrapper {
      display: none;
    }
  }
  @media screen and (max-width: 392px) {
    .layout__content {
      padding: 0 !important;
    }
  }
  .layout__sidebar {
    width: auto;
  }
  .layout__screen {
    width: auto;
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    position: relative;
    height: 100%;
    overflow: hidden;
    background-color: #ebeef0;
  }
  .layout__navbar {
    position: sticky;
    display: block;
    top: 0;
    z-index: 9999;
    box-shadow: 2px 4px 3px rgba(0, 0, 0, 0.05);
    padding: 11px 20px 12px 20px;
    box-sizing: content-box;
    height: 30px !important;
  }
  .navbar-collapse.collapse {
    width: 100% !important;
    height: 33px;
  }
  @media screen and (max-width: 767px) {
    .navbar-collapse.collapse {
      box-shadow: 0px 10px 12px 2px rgba(20, 20, 20, 0.3);
      height: auto !important;
    }
  }
  .my-navbar-brand {
    font-family: 'Open Sans', sans-serif !important;
    font-weight: bolder;
    font-size: 18px;
    line-height: 28px;

  }
  .layout__navbar-avatar {
    display: inline-block;
    width: 35px;
    height: 35px;
  }
  .layout__content-head {
    min-width: 280px;
  }

  .layout__content {
    overflow-x: hidden !important;
    background-color: #ebeef0;
    padding: 5px 0;
    overflow-y: auto;
  }
  .layout__content-main {
  }
  .content--full {
    padding-left: 15px;
    padding-right: 15px;
  }
</style>

<script>
import { mapState, mapActions } from 'vuex';
import VuePerfectScrollbar from 'vue-perfect-scrollbar';

export default {
  name: 'Main',
  data() {
    return {
    };
  },
  props: {
    sidebar: {
      type: Boolean,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    modalShow: {
      type: Boolean,
      required: false,
      default: false,
    },
    modalTitle: {
      type: String,
      required: false,
      default: '',
    },
  },
  methods: {
    ...mapActions('auth', [
      'getProfile',
    ]),
    logout() {
      this.$store.dispatch('auth/logout');
      this.$disconnect();
      this.$router.push('/');
    },
    openHelp() {
      window.open('https://samfeeds.com/samfeeds_help.pdf', '_blank');
    },
  },
  computed: {
    ...mapState('auth', [
      'profile',
    ]),
    navbarHeader() {
      return this.title;
    },
    _modalShow: {
      get() {
        return this.modalShow;
      },
      set(newValue) {
        this.$emit('modalToggle', newValue);
      },
    },
  },
  components: { VuePerfectScrollbar },
  created() {
    this.$connect();
  },
};
</script>

