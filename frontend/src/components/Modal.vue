<template>
  <b-modal ref="modal" v-model="mutableShow" :title="title">
    <slot name="body"></slot>
    <div slot="modal-footer" class="w-100">
      <slot name="footer"></slot>
    </div>
  </b-modal>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      required: true,
    },
    show: {
      type: Boolean,
      required: true,
    },
  },
  computed: {
    mutableShow: {
      get() { return this.show; },
      set(newValue) { this.$emit('modalToggle', newValue); },
    },
  },
  watch: {
    // show(newValue) {
    //   if (newValue) {
    //     console.log(this.$refs.modal);
    //     this.$refs.modal.show();
    //   } else {
    //     this.$refs.modal.hide();
    //   }
    // },
  },
  mounted() {
    // if (this.show) {
    //   this.$refs.modal.show();
    // } else {
    //   this.$refs.modal.hide();
    // }
  },
};
</script>
