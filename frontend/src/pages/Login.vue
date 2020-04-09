<template>
  <layout-auth>
    <b-form class="w-100 p-0 m-0">
      <b-container fluid class="container p-5">
        <h3 class="form__name mb-5">Login</h3>
        <b-row class="mt-4">
          <b-col sm="3"><label for="login">E-mail:</label></b-col>
          <b-col sm="9">
            <b-form-input id="login" v-model="email" type="email" name="login">
            </b-form-input>
          </b-col>
        </b-row>
        <b-row class="mt-4">
          <b-col sm="3"><label for="password">Password:</label></b-col>
          <b-col sm="9">
            <b-form-input id="password" v-model="password" type="password" name="password">
            </b-form-input>
          </b-col>
        </b-row>
        <!--<div class="form__link mt-1"><span>Forgot password</span></div>-->
      </b-container>
      <b-container class="form__buttons px-5">
        <!--<b-col sm="7" class="pl-0">-->
          <!--<b-button block variant="light" size="lg">Registration</b-button>-->
        <!--</b-col>-->
        <b-col sm="12" class="pr-0">
          <b-button block variant="primary" type="submit" size="lg" @click.prevent="signUp">
            Login
          </b-button>
        </b-col>
      </b-container>
    </b-form>
  </layout-auth>
</template>

<style scoped>

.form__name {
  font-family: 'Open Sans', sans-serif !important;
  font-weight: bold;
  text-align: center;
}
.form__link {
  font-family: "Open Sans";
  font-style: normal;
  font-stretch: normal;
  line-height: normal;
  letter-spacing: normal;
  color: #189cde;
  font-size: 12px;
  text-align: right;
}
.form__link span:hover {
  color: #0d85b7;
  cursor: pointer;
  transition: 0.2s;
}
.form__link span:active {
  color: #1e96c8;
}

.form__buttons {
  height: 93px;
  width: 100%;
  border-top: solid 1px #edf3fa;
  background-color: #fafbfc;
  display: flex;
  justify-content: space-around;
  align-items: center;
}

</style>

<script>
import { mapActions, mapState } from 'vuex';
// import api from '../store/api';

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
    };
  },
  computed: {
    ...mapState('auth', [
      'token',
    ]),
  },
  methods: {
    ...mapActions('auth', [
      'login',
    ]),
    async signUp() {
      try {
        await this.login({
          email: this.email,
          password: this.password,
        });
        this.$router.push({ name: 'Messages' });
      } catch (err) {
        this.$root.$emit('handleError', err);
      }
    },
  },
  // async created() {
  // },
};
</script>
