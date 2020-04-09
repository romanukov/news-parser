<script>
export default {
  async created() {
    if (this.$route.query.access) {
      localStorage.setItem('user_token', this.$route.query.access);
    }
    if (localStorage.getItem('user_token')) {
      await this.$store.dispatch('auth/getProfile');
      this.$router.push('/messages/');
    } else {
      this.$router.push('/login/');
    }
  },
};
</script>ё
