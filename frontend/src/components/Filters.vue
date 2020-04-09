<template>
  <div class="filters-container">
    <div class="head__view">
      <!--<span>{{ paginatorLabel }}</span>-->
      <!--<span class="head__msgs-new">{{ paginatorViewSize }}</span>-->
      <!--<span class="head__msgs">/ {{ paginatorMaxSize }}</span>-->
    </div>
    <div class="filters" :class="{'filters--reversed': reverse}">
      <div
        class="filter"
        :key="key"
        v-for="(filter, key) in mutableFilters">
        <div class="filter__caption">
          <span>{{ filter.name }}</span>
        </div>
        <div class="filter__input w-100 position-relative">
          <b-form-select
            v-if="filter.type === 'select'"
            v-model="selectValue"
            @input="(newValue) => {$emit('filterChange', { filter, value: newValue, })}"
            class="mb-3">
            <option
              selected="selected"
              :value="''">
              All sources
            </option>
            <option
              :selected="option[filter.label] === 'All sources'"
              v-for="option in filter.options"
              :value="option[filter.value]"
              :key="option[filter.value]">
              {{ option[filter.label] }}
            </option>
          </b-form-select>
            <Datepicker
              v-if="filter.type === 'date'"
              ref="date"
              righttoleft="false"
              i18n="EN"
              v-model="filter.value"
              @selected="newValue => { $emit('filterChange', { filter, value: newValue, })}"
            />
        </div>
      </div>
      <div class="new-button-container" style="display: flex; padding: 6px;"
          v-if="showNewButton">
        <b-button
          size="xs"
          variant="primary"
          @click="$emit('newButtonClick')">
          <source-icon mode="logo" type="ionic"></source-icon>
          {{ newItemName ? 'New ' + newItemName : 'New' }}
        </b-button>
      </div>
    </div>
  </div>
</template>

<style>
.input-date {
  width: 100% !important;
  margin-bottom: 0 !important;
  background: #fff;
  height: 28px;
  line-height: 12px;
  padding: 0.375rem 0.75rem 0.375rem 0.75rem !important;
  font-family: 'Roboto', sans-serif !important;
  border-color: #dfe7f2 !important;
  border-radius: 0.25rem;
}
.calendar {
  right: 10px;
  height: auto !important;
  box-shadow: 0px 5px 15px -3px rgba(20,20,20,0.5) !important;
}
.calendar-btn-apply {
  cursor: pointer;
}
.calendar-wrap {
  width: 100% !important;
}
.calendar-range-mobile {
  width: 100% !important;
}
</style>
<style scoped>
  .filters-container {
    padding-left: 10px !important;
    padding-right: 10px !important;
    display: flex;
    width: 100%;
    justify-content: space-between;
  }
  @media screen and (max-width: 880px) {
    .filters-container {
      padding-left: 10px !important;
      padding-right: 10px !important;
      display: flex;
    }
    .new-button-container {
      display: flex;
      width: 100%;
      justify-content: flex-end;
      margin: 5px 0;
    }
  }
  .head__msgs {
    color: #91a7b3;
    position: relative;
  }
  .head__msgs-new {
    color: #189cde;
  }
  .head__view {
    line-height: 38px;
    white-space: nowrap;
    font-weight: bold;
    font-size: 12px;
    display: inline;
  }
  .filters {
    font-weight: normal;
    display: flex;
    justify-content: flex-end;
  }
  .filters--reversed {
  }
  div.filter--reversed + div.filter--reversed {
    margin-left: 15px;
    margin-right: 0;
  }
  .filter {
    min-width: 250px;
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .filter div+button {
    margin-left: 20px;
  }
  .filter + .filter {
    margin-left: 15px;
  }
  @media screen and (max-width: 800px) {
    .filter + .filter {
      margin-right: 0 !important;
      margin-left: 0 !important;
    }
    .filters {
      display: block;
    }
    .filter {
      align-items: left;
      justify-content: space-between;
      flex-wrap: wrap;

    }
    .filter select {
      float: right;
    }
  }
  .filter__input select {
    margin: 0 !important;
  }
  .filter__caption {
    white-space: nowrap;
    margin-right: 10px;
    color: #797c8a;
    line-height: 38px;
    font-size: 11px;
  }
  .new-button-container {

  }
</style>

<script>
import Datepicker from '@/components/Datepicker/RangedatePicker';

export default {
  name: 'Filters',
  data() {
    return {
      showCalendar: false,
      selectValue: '',
    };
  },
  computed: {
    mutableFilters() {
      return this.filters;
    },
  },
  props: {
    /*
    * Label of paginator
    * */
    paginatorLabel: {
      type: String,
      required: true,
    },
    /*
    * Current size of pagination
    * */
    paginatorViewSize: {
      type: Number,
      required: true,
    },
    /*
    * Maximal size of pagination
    * */
    paginatorMaxSize: {
      type: Number,
      required: true,
    },
    /*
    * if true, on left part will showed button for add of element
    * emits 'newItemButtonClick' event
    * */
    showNewButton: {
      type: Boolean,
      required: false,
      default: false,
    },
    /*
    * string in "new" button
    * */
    newItemName: {
      type: String,
      required: false,
    },
    /*
    * filters - array of objects with signature
    * {
    *   name: String,
    *   type: "select" || "string",
    *   value,
    *   options: Array
    * }
    * */
    filters: {
      type: Array,
      required: false,
    },
    /*
    * if true, selects showing from right to left (and aligning by right side)
    * */
    reverse: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  watch: {
    showCalendar(newValue) {
      this.$refs.date[0].$el.children[1].style.display = newValue ? 'block' : 'none';
    },
  },
  methods: {
    test() {
    },
  },
  components: { Datepicker },
  mounted() {
    this.$on('dateNull', () => {
      this.$refs.date[0].$emit('dateNull');
    });
  },
};
</script>
