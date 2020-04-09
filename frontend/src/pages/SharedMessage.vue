<template>
  <div class="shared-message">
      <div class="shared-message__form">
        <a href="https://samfeeds.com" class="shared-message__logo"></a>
        <message
          class="shared"
          v-if="message"
          :disablePopovers="true"
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
          :date="message.date">
          <h5 style="
            text-align:center;
            font-weight:bold;
            margin-bottom:20px;">
            Shared message
          </h5>
        </message>
      </div>
      <h3 class="shared-message__text">
        <h1>Tool for tracking Telegram and Twitter</h1>
        <p>Still not using Samfeeds? Discover and try for free!</p>
        <button onclick="window.open('https://samfeeds.com')">Learn more</button>
      </h3>
  </div>
</template>

<style scoped>
  .shared {
    max-width: 800px;
    margin: auto;
  }
  .shared >>> .message__header {
    font-size: 14px;
  }
  .shared >>> .card-body > span {
    font-size: 14px !important;
  }
  .shared-message {
    width: 100%;
    background-color: #36aee2;
    position: absolute;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .shared-message__text {
    background: #ebeef0;
    margin: 170px 0 0 0;
    width: 100%;
    min-height: 400px;
    padding-top: 91px;
  }
  .shared-message__text h1 {
    color: #333;
    margin-bottom: 10px;
    font-weight: 600;
    font-size: 28px;
    line-height: 1.1;
    font-family: 'Poppins', sans-serif;
    text-align: center;
    max-width: 1024px;
    margin: auto;
  }
  .shared-message__text h1 .source-icon {
    height: 35px;
    width: 35px;
  }
  .shared-message__text p {
    color: #333;
    font-size: 18px;
    line-height: 1.8;
    text-align: center;
    max-width: 1024px;
    margin: auto;
    margin-top: 30px;
  }
  .shared-message__text button {
    border: 2px solid #11c15b;
    border-radius: 28px;
    font-family: Arial;
    color: #fff;
    font-size: 16px;
    padding: 15px 30px;
    text-decoration: none;
    transition: all 0.5s;
    box-shadow: 0 5px 25px -7px #000000;
    background: #11c15b;
    cursor: pointer;
    margin: auto;
    display: block;
    margin-top: 30px;
  }
  .shared-message__text button:hover {
    color: #444;
    text-decoration: none;
    opacity: 0.8;
    cursor: pointer;
  }
  .shared-message__form {
    max-width: 1300px;
    width: 100%;
    padding: 0 16px;
  }

  .shared-message__logo {
    width: 240px;
    margin: 10px auto 100px auto;
    height: 60px;
    background-image: url("../assets/logo_samfeeds_auth.png");
    background-size: cover;
    display: block;
  }

</style>

<script>
import { mapActions } from 'vuex';
// import api from '../store/api';
import Message from '../components/Message';

export default {
  name: 'Shared message',
  data() {
    return {
      message: null,
    };
  },
  computed: {
    id() {
      return this.$route.params.id;
    },
  },
  methods: {
    ...mapActions('feed', [
      'getSharedMessage',
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
        // console.log(err);
      }
    },
  },
  async created() {
    try {
      this.message = await this.getSharedMessage(this.id);
    } catch (e) {
      throw e;
    }
  },
  components: { Message },
  // async created() {
  // },
};
</script>
