import fecha from 'fecha';

const defaultConfig = {};
const defaultI18n = 'ID';
const availableMonths = {
  EN: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November',
    'December'],
  ID: ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November',
    'Desember'],
};

const availableShortDays = {
  EN: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
  ID: ['Min', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab'],
};

const presetRangeLabel = {
  EN: {
    today: 'Today',
    thisMonth: 'This Month',
    lastMonth: 'Last Month',
    lastSevenSays: 'Last 7 Days',
    lastThirtyDays: 'Last 30 Days',
  },
  ID: {
    today: 'Hari ini',
    thisMonth: 'Bulan ini',
    lastMonth: 'Bulan lalu',
    lastSevenDays: '7 Hari Terakhir',
    lastThirtyDays: '30 Hari Terakhir',
  },
};

const defaultCaptions = {
  title: 'Choose Dates',
  ok_button: 'Apply',
};

const defaultStyle = {
  daysWeeks: 'calendar_weeks',
  days: 'calendar_days',
  daysSelected: 'calendar_days_selected',
  daysInRange: 'calendar_days_in-range',
  firstDate: 'calendar_month_left',
  secondDate: 'calendar_month_right',
  presetRanges: 'calendar_preset-ranges',
  dateDisabled: 'calendar_days--disabled',
};

const defaultPresets = function (i18n = defaultI18n) {
  return {
    today() {
      const n = new Date();
      const startToday = new Date(n.getFullYear(), n.getMonth(), n.getDate() + 1, 0, 0);
      const endToday = new Date(n.getFullYear(), n.getMonth(), n.getDate() + 1, 23, 59);
      return {
        label: 'Today',
        active: false,
        dateRange: {
          start: startToday,
          end: endToday,
        },
      };
    },
    last3days() {
      const n = new Date();
      const start = new Date(n.getFullYear(), n.getMonth(), n.getDate() - 3);
      const end = new Date(n.getFullYear(), n.getMonth(), n.getDate() + 1);
      return {
        label: 'Last 3 days',
        active: false,
        dateRange: {
          start,
          end,
        },
      };
    },
    last7days() {
      const n = new Date();
      const start = new Date(n.getFullYear(), n.getMonth(), n.getDate() - 5);
      const end = new Date(n.getFullYear(), n.getMonth(), n.getDate() + 1);
      return {
        label: 'Last week',
        active: false,
        dateRange: {
          start,
          end,
        },
      };
    },
    empty() {
      const n = new Date();
      const startToday = null;
      const endToday = null;
      return {
        label: 'All time',
        active: false,
        dateRange: {
          start: startToday,
          end: endToday,
        },
      };
    },
    thisMonth() {
      const n = new Date();
      const startMonth = new Date(n.getFullYear(), n.getMonth(), 2);
      const endMonth = new Date(n.getFullYear(), n.getMonth() + 1, 1);
      return {
        label: presetRangeLabel[i18n].thisMonth,
        active: false,
        dateRange: {
          start: startMonth,
          end: endMonth,
        },
      };
    },
    lastMonth() {
      const n = new Date();
      const startMonth = new Date(n.getFullYear(), n.getMonth() - 1, 2);
      const endMonth = new Date(n.getFullYear(), n.getMonth(), 1);
      return {
        label: presetRangeLabel[i18n].lastMonth,
        active: false,
        dateRange: {
          start: startMonth,
          end: endMonth,
        },
      };
    },
    others() {
      return {
        label: 'Date range',
        active: false,
        dateRange: null,
      };
    },
  };
};

export default {
  name: 'vue-rangedate-picker',
  props: {
    configs: {
      type: Object,
      default: () => defaultConfig,
    },
    i18n: {
      type: String,
      default: defaultI18n,
    },
    months: {
      type: Array,
      default: () => null,
    },
    shortDays: {
      type: Array,
      default: () => null,
    },
    // options for captions are: title, ok_button
    captions: {
      type: Object,
      default: () => defaultCaptions,
    },
    format: {
      type: String,
      default: 'DD MMM YYYY',
    },
    styles: {
      type: Object,
      default: () => {},
    },
    initRange: {
      type: Object,
      default: () => null,
    },
    startActiveMonth: {
      type: Number,
      default: new Date().getMonth(),
    },
    startActiveYear: {
      type: Number,
      default: new Date().getFullYear(),
    },
    presetRanges: {
      type: Object,
      default: () => null,
    },
    compact: {
      type: String,
      default: 'false',
    },
    righttoleft: {
      type: String,
      default: 'false',
    },
  },
  data() {
    return {
      dateRange: {},
      numOfDays: 7,
      isFirstChoice: true,
      isOpen: false,
      presetActive: '',
      showMonth: false,
      activeMonthStart: this.startActiveMonth,
      activeYearStart: this.startActiveYear,
      activeYearEnd: this.startActiveYear,
      showWrapper: false,
    };
  },
  created() {
    this.$on('dateNull', () => {
      this.dateRange = {};
    });
    if (this.isCompact) {
      this.isOpen = true;
    }
    if (this.activeMonthStart === 11) this.activeYearEnd = this.activeYearStart + 1;
  },
  watch: {
    startNextActiveMonth(value) {
      if (value === 0) this.activeYearEnd = this.activeYearStart + 1;
    },
  },
  computed: {
    monthsLocale() {
      return this.months || availableMonths[this.i18n];
    },
    shortDaysLocale() {
      return this.shortDays || availableShortDays[this.i18n];
    },
    s() {
      return Object.assign({}, defaultStyle, this.style);
    },
    startMonthDay() {
      return new Date(this.activeYearStart, this.activeMonthStart, 1).getDay();
    },
    startNextMonthDay() {
      return new Date(this.activeYearStart, this.startNextActiveMonth, 1).getDay();
    },
    endMonthDate() {
      return new Date(this.activeYearEnd, this.startNextActiveMonth, 0).getDate();
    },
    endNextMonthDate() {
      return new Date(this.activeYearEnd, this.activeMonthStart + 2, 0).getDate();
    },
    startNextActiveMonth() {
      return this.activeMonthStart >= 11 ? 0 : this.activeMonthStart + 1;
    },
    finalPresetRanges() {
      const tmp = {};
      const presets = this.presetRanges || defaultPresets(this.i18n);
      for (const i in presets) {
        const item = presets[i];
        let plainItem = item;
        if (typeof item === 'function') {
          plainItem = item();
        }
        tmp[i] = plainItem;
      }
      return tmp;
    },
    isCompact() {
      return this.compact === 'true';
    },
    isRighttoLeft() {
      return this.righttoleft === 'true';
    },
  },
  methods: {
    toggleCalendar() {
      if (this.isCompact) {
        this.showMonth = !this.showMonth;
        return;
      }
      this.isOpen = !this.isOpen;
      this.showMonth = !this.showMonth;
    },
    getDateString(date, format = this.format) {
      if (!date) {
        return null;
      }
      const dateparse = new Date(Date.parse(date));
      return fecha.format(new Date(dateparse.getFullYear(), dateparse.getMonth(), dateparse.getDate() - 1), format);
    },
    getDayIndexInMonth(r, i, startMonthDay) {
      const date = (this.numOfDays * (r - 1)) + i;
      return date - startMonthDay;
    },
    getDayCell(r, i, startMonthDay, endMonthDate) {
      const result = this.getDayIndexInMonth(r, i, startMonthDay);
      // bound by > 0 and < last day of month
      return result > 0 && result <= endMonthDate ? result : '&nbsp;';
    },
    getNewDateRange(result, activeMonth, activeYear) {
      const newData = {};
      let key = 'start';
      if (!this.isFirstChoice) {
        key = 'end';
      } else {
        newData.end = null;
      }
      const resultDate = new Date(activeYear, activeMonth, result);
      if (!this.isFirstChoice && resultDate < this.dateRange.start) {
        this.isFirstChoice = false;
        return { start: resultDate };
      }

      // toggle first choice
      this.isFirstChoice = !this.isFirstChoice;
      newData[key] = resultDate;
      return newData;
    },
    selectFirstItem(r, i) {
      const result = this.getDayIndexInMonth(r, i, this.startMonthDay) + 1;
      this.dateRange = Object.assign({}, this.dateRange, this.getNewDateRange(result, this.activeMonthStart,
        this.activeYearStart));
      if (this.dateRange.start && this.dateRange.end) {
        this.presetActive = '';
        if (this.isCompact) {
          this.showMonth = false;
        }
      }
    },
    selectSecondItem(r, i) {
      const result = this.getDayIndexInMonth(r, i, this.startNextMonthDay) + 1;
      this.dateRange = Object.assign({}, this.dateRange, this.getNewDateRange(result, this.startNextActiveMonth,
        this.activeYearEnd));
      if (this.dateRange.start && this.dateRange.end) {
        this.presetActive = '';
      }
    },
    isDateSelected(r, i, key, startMonthDay, endMonthDate) {
      const result = this.getDayIndexInMonth(r, i, startMonthDay) + 1;
      if (result < 2 || result > endMonthDate + 1) return false;

      let currDate = null;
      if (key === 'first') {
        currDate = new Date(this.activeYearStart, this.activeMonthStart, result);
      } else {
        currDate = new Date(this.activeYearEnd, this.startNextActiveMonth, result);
      }
      return (this.dateRange.start && this.dateRange.start.getTime() === currDate.getTime()) ||
        (this.dateRange.end && this.dateRange.end.getTime() === currDate.getTime());
    },
    isDateInRange(r, i, key, startMonthDay, endMonthDate) {
      const result = this.getDayIndexInMonth(r, i, startMonthDay) + 1;
      if (result < 2 || result > endMonthDate + 1) return false;

      let currDate = null;
      if (key === 'first') {
        currDate = new Date(this.activeYearStart, this.activeMonthStart, result);
      } else {
        currDate = new Date(this.activeYearEnd, this.startNextActiveMonth, result);
      }
      return (this.dateRange.start && this.dateRange.start.getTime() < currDate.getTime()) &&
        (this.dateRange.end && this.dateRange.end.getTime() > currDate.getTime());
    },
    isDateDisabled(r, i, startMonthDay, endMonthDate) {
      const result = this.getDayIndexInMonth(r, i, startMonthDay);
      // bound by > 0 and < last day of month
      return !(result > 0 && result <= endMonthDate);
    },
    goPrevMonth() {
      const prevMonth = new Date(this.activeYearStart, this.activeMonthStart, 0);
      this.activeMonthStart = prevMonth.getMonth();
      this.activeYearStart = prevMonth.getFullYear();
      this.activeYearEnd = prevMonth.getFullYear();
    },
    goNextMonth() {
      const nextMonth = new Date(this.activeYearEnd, this.startNextActiveMonth, 1);
      this.activeMonthStart = nextMonth.getMonth();
      this.activeYearStart = nextMonth.getFullYear();
      this.activeYearEnd = nextMonth.getFullYear();
    },
    updatePreset(item) {
      if (item.label !== 'Date range') {
        this.presetActive = item.label;
        this.dateRange = item.dateRange;
        // update start active month
        this.activeMonthStart = this.dateRange.start.getMonth();
        this.activeYearStart = this.dateRange.start.getFullYear();
        this.activeYearEnd = this.dateRange.end.getFullYear();
        this.showWrapper = false;
      } else {
        this.presetActive = item.label;
        this.showWrapper = true;
      }
    },
    setDateValue() {
      this.$emit('selected', this.dateRange);
      if (!this.isCompact) {
        this.toggleCalendar();
      }
    },
  },
};
