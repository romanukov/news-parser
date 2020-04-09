import plugin from '@/RangedatePicker.vue';

export default {
  install(Vue, options) {
    Vue.component(plugin.name, plugin);
  },
};
