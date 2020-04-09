<template>
  <layout-main
    title="Telegram Watcher administration"
    :sidebar="true">
    <p style="font-size: 15px; font-family: 'Roboto'; font-weight: 600; line-height: 18px; margin-top: 20px;">
      <source-icon style="position: relative; top: 4px;margin: 0 5px;" type="telegram"></source-icon>
      Telegram watcher
    </p>
    <div class="form-container" style="background: #fff;">
      <b-form class="native-form" style="max-width: 377px;">
        <h2 style="font-size: 18px; color: #013752; font-family: 'Open Sans'; font-weight: bold">Profile</h2>

        <b-row style="margin-top: 16px;">
          <b-col sm="3" class="form__label">Login</b-col>
          <b-col sm="8">
            <b>{{ mutableProfile.username }}</b>
          </b-col>
        </b-row>
        <b-row style="margin-top: 16px;">
          <b-col sm="3" class="form__label">Email</b-col>
          <b-col sm="8">
            <b-form-input v-model="mutableProfile.email" type="email"></b-form-input>
          </b-col>
        </b-row>
        <b-row style="margin-top: 16px;">
          <b-col sm="3" class="form__label">Time Zone</b-col>
          <b-col sm="8">
            <b-form-select v-model="mutableProfile.timezone">
              <option v-for="zone in timezones" :value="zone.value">{{ zone.name }}</option>
            </b-form-select>
          </b-col>
        </b-row>
        <b-row class="my-4">
          <b-col sm="3" class="form__label">Password</b-col>
          <b-col sm="8">
            <b-form-input type="password" v-model="mutableProfile.password"></b-form-input>
          </b-col>
        </b-row>
        <!--<b-row class="my-4">-->
          <!--<b-col sm="3" class="form__label">Timezone</b-col>-->
          <!--<b-col sm="8">-->
            <!--<b-form-select></b-form-select>-->
          <!--</b-col>-->
        <!--</b-row>-->
        <!--<b-row class="my-4">-->
          <!--<b-col sm="3" class="form__label">Last login</b-col>-->
          <!--<b-col sm="8">-->
            <!--<p style="font-weight: bold; font-family: Roboto; font-size: 11px; line-height: 28px;">Mar, 22 2018 17:45</p>-->
          <!--</b-col>-->
        <!--</b-row>-->
        <b-row class="my-4" v-if="mutableProfile.is_subscriber">
          <b-col
            style="margin: 0 13px;"
            class="subscribe-text"
            sm="12"
            v-if="!mutableProfile.last_subscribe_till">
            Subscribe and get full access to the service.
          </b-col>
          <b-col
            class="subscribe-text"
            sm="12"
            v-else-if="
              (new Date(mutableProfile.last_subscribe_till)).getTime() < (new Date()).getTime()
            ">
            Your subscription has expired.
          </b-col>
          <b-col
            class="subscribe-text"
            sm="12"
            v-else-if="
              (new Date(mutableProfile.last_subscribe_till)).getTime() > (new Date()).getTime()
            ">
            Your subscription is valid until {{ (new Date(mutableProfile.last_subscribe_till)).toLocaleDateString() }}
          </b-col>
          <b-col
            sm="12"
            style="padding-left: 13px; padding-right: 13px; margin-top: 10px;">
            <button
              @click.prevent="stripe_checkout.open({
                email: profile.email,
                panelLabel: 'Get 7-days trial',
                amount: 0,
              })"
              class="btn btn-primary btn-md"
              v-if="
                !mutableProfile.last_subscribe_till
              ">
                Get 7-days trial
            </button>
            <button
              @click.prevent="stripe_checkout.open({
                email: profile.email,
              })"
              class="btn btn-primary btn-md"
              v-else-if="
                (new Date(mutableProfile.last_subscribe_till)).getTime() < (new Date()).getTime()
              ">
                Renew subscription
            </button>
            <button
              @click.prevent="stripe_checkout.open({
                email: profile.email,
                panelLabel: 'Change payment data',
                amount: 0,
              })"
              class="btn btn-primary btn-md"
              v-else-if="
                (new Date(mutableProfile.last_subscribe_till)).getTime() > (new Date()).getTime()
              ">
                Change payment data
            </button>
          </b-col>
        </b-row>
        <b-row class="my-4" v-if="!mutableProfile.is_subscriber">
          <b-col sm="12" class="subscribe-text">Unlimited subscription</b-col>
        </b-row>
      </b-form>
      <b-form class="native-form" style="max-width: 377px; padding-top: 0">
        <h2 style="font-size: 15px; color: #013752; font-family: 'Open Sans'; font-weight: bold">Black list</h2>
        <div
          v-if="mutableProfile && mutableProfile.username_blacklist">
          <b-row>
            <div
              v-if="item"
              :key="itemIndex"
              v-for="(item, itemIndex) in blackList"
              class="col-md-12 sidebar-elem" style="margin-top: 16px; padding-bottom: 10px; border-bottom: 1px solid #edf3fa">
              <div class="feeds-table-body__rectangle sidebar__elem-icon">{{item.slice(0,2).toUpperCase()}}</div>
              <span class="black-list-label">{{item}}</span>
                <div
                  @click="deleteBlack(itemIndex)"
                  style="display: inline-block; float: right; margin-right: 10px; cursor: pointer;">
                <source-icon
                  class="remove-icon"
                  mode="md"
                  type="close"
                  style="fill: #f56767" />
              </div>
            </div>
          </b-row>
        </div>
        <span
          v-if="!mutableProfile || !mutableProfile.username_blacklist"
          style="font-size: 12px; color: #7F8177">Empty
        </span>
      </b-form>
      <div class="form__footer">
        <b-btn
          :disabled="loading"
          @click="loading ? () => {} : saveProfile()"
          variant="primary"
          size="md">Save</b-btn>
      </div>
    </div>
  </layout-main>
</template>

<style>
  .native-form {
    padding: 26px 28px;
  }
  .form__footer {
    padding: 23px 20px;
    background: #fafbfc
  }
  .black-list-person + span {
    position: relative;
    top: -5px;
  }
  .black-list-person {
    width: 20px;
    height: 20px;
    background: #edf3fa;
    border-radius: 50%;
    display: inline-block;
  }
  .black-list-person .ion {
    margin: auto;
    display: block;
    position: relative;
    top: 5px;
  }
  .black-list-person svg {
    margin: auto;
    display: block;
    fill: #91a7b3;
    width: 11px;
    height: 11px;
  }
  .black-list-label {
    font-size: 12px;
    font-weight: bold;
    margin-left: 7px;
    line-height: 20px;
  }
  .remove-icon svg {
    width: 15px;
    height: 15px;
  }
  .form__label {
    font-size: 11px;
    font-family: 'Roboto';
    color: #797c8a;
    line-height: 28px;
  }
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
  .sidebar__elem:nth-child(3n) .sidebar__elem-icon {
    background-color: #f56767 !important;
  }
</style>

<script>
import { mapState, mapActions } from 'vuex';
import _ from 'lodash';

const timezones = [
  { value: 'Etc/GMT+12', name: 'GMT-12' },
  { value: 'Etc/GMT+11', name: 'GMT-11' },
  { value: 'Etc/GMT+10', name: 'GMT-10' },
  { value: 'Etc/GMT+9', name: 'GMT-9' },
  { value: 'Etc/GMT+8', name: 'GMT-8' },
  { value: 'Etc/GMT+7', name: 'GMT-7' },
  { value: 'Etc/GMT+6', name: 'GMT-6' },
  { value: 'Etc/GMT+5', name: 'GMT-5' },
  { value: 'Etc/GMT+4', name: 'GMT-4' },
  { value: 'Etc/GMT+3', name: 'GMT-3' },
  { value: 'Etc/GMT+2', name: 'GMT-2' },
  { value: 'Etc/GMT+1', name: 'GMT-1' },
  { value: 'Etc/GMT+0', name: 'GMT-0' },
  { value: 'Etc/GMT-0', name: 'GMT+0' },
  { value: 'Etc/GMT-1', name: 'GMT+1' },
  { value: 'Etc/GMT-2', name: 'GMT+2' },
  { value: 'Etc/GMT-3', name: 'GMT+3' },
  { value: 'Etc/GMT-4', name: 'GMT+4' },
  { value: 'Etc/GMT-5', name: 'GMT+5' },
  { value: 'Etc/GMT-6', name: 'GMT+6' },
  { value: 'Etc/GMT-7', name: 'GMT+7' },
  { value: 'Etc/GMT-8', name: 'GMT+8' },
  { value: 'Etc/GMT-9', name: 'GMT+9' },
  { value: 'Etc/GMT-10', name: 'GMT+10' },
  { value: 'Etc/GMT-11', name: 'GMT+11' },
  { value: 'Etc/GMT-12', name: 'GMT+12' },
  { value: 'Etc/GMT-13', name: 'GMT+13' },
  { value: 'Etc/GMT-14', name: 'GMT+14' },
];
export default {
  name: 'Profile',
  data() {
    return {
      mutableProfile: {},
      currentProfile: null,
      blackList: [],
      loading: false,
      timezones,
      // eslint-disable-next-line
      stripe_checkout: null
    };
  },
  computed: {
    ...mapState('auth', [
      'profile',
    ]),
  },
  methods: {
    ...mapActions('auth', [
      'putProfile',
    ]),
    async saveProfile() {
      try {
        this.loading = true;
        const profile = _.cloneDeep(this.mutableProfile);
        profile.username_blacklist = this.blackList.join('\n');
        if (!profile.password) delete profile.password;
        await this.putProfile(profile);
        this.$root.$emit('handleNote', {
          title: 'Profile updated!',
          text: 'Your profile data was successfully updated!',
        });
        this.loading = false;
      } catch (err) {
        this.loading = false;
        this.$root.$emit('handleError', err);
      }
    },
    deleteBlack(itemKey) {
      this.blackList.splice(itemKey, 1);
    },
  },
  async created() {
    try {
      await this.$store.dispatch('auth/getProfile');
      this.mutableProfile = {
        password: '',
        ..._.cloneDeep(this.profile),
      };
      this.blackList = [];
      this.mutableProfile.username_blacklist.split('\n').forEach((item) => {
        if (item && item !== '\n' && item !== ' ') this.blackList.push(item);
      });
      window.addEventListener('popstate', () => {
        this.stripe_checkout.close();
      });
      fetch('/api/stripe_description/', {
        method: 'GET',
      }).then(async (response) => {
        const data = await response.json();
        // eslint-disable-next-line
        this.stripe_checkout = StripeCheckout.configure({
          key: data.public_key,
          locale: 'auto',
          name: data.name,
          image: 'https://stripe.com/img/documentation/checkout/marketplace.png',
          description: data.description,
          amount: data.amount,
          zipCode: false,
          billingAddress: false,
          allowRememberMe: true,
          token: async (token) => {
            // You can access the token ID with `token.id`.
            // Get the token ID to your server-side code for use.
            try {
              const headers = new Headers();
              headers.append('Authorization', `JWT ${localStorage.getItem('user_token')}`);
              headers.append('Content-Type', 'application/json');
              await fetch('/api/stripe_checkout/', {
                method: 'POST',
                body: JSON.stringify(token),
                headers,
              });
              await this.$store.dispatch('auth/getProfile');
              this.mutableProfile = {
                password: '',
                ..._.cloneDeep(this.profile),
              };
            } catch (err) {
              throw err;
            }
          },
        });
      });
    } catch (err) {
      this.$emit('handleError', err);
    }
  },
};
</script>
