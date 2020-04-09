<script>
import logoIonic from 'vue-ionicons/dist/logo-ionic';
import mdRadio from 'vue-ionicons/dist/md-radio';
import mdOpen from 'vue-ionicons/dist/md-open';
import mdClose from 'vue-ionicons/dist/md-close';
import mdAlert from 'vue-ionicons/dist/md-alert';
import mdShare from 'vue-ionicons/dist/md-share';
import mdSettings from 'vue-ionicons/dist/md-settings';
import mdExit from 'vue-ionicons/dist/md-exit';
import mdStar from 'vue-ionicons/dist/md-star';
import mdCreate from 'vue-ionicons/dist/md-create';
import iosDisc from 'vue-ionicons/dist/ios-disc';
import mdPerson from 'vue-ionicons/dist/md-person';
import mdPeople from 'vue-ionicons/dist/md-people';
import mdVideo from 'vue-ionicons/dist/md-videocam';
import mdPhoto from 'vue-ionicons/dist/md-photos';
import mdChatbubbles from 'vue-ionicons/dist/md-chatbubbles';
import mdAttach from 'vue-ionicons/dist/md-attach';
import iosArrowDown from 'vue-ionicons/dist/ios-arrow-down';
import iosCloseCircleOutline from 'vue-ionicons/dist/ios-close-circle-outline';
import mdInformationCircle from 'vue-ionicons/dist/md-information-circle';

const components = {
  logoIonic,
  iosDisc,
  iosArrowDown,
  iosCloseCircleOutline,
  mdInformationCircle,
  mdRadio,
  mdOpen,
  mdClose,
  mdAlert,
  mdSettings,
  mdExit,
  mdStar,
  mdCreate,
  mdPerson,
  mdPeople,
  mdChatbubbles,
  mdShare,
  mdAttach,
  mdVideo,
  mdPhoto,
};
export default {
  components,
  name: 'SourceIcon',
  computed: {
    sourceTypes() {
      return ['telegram', 'twitter', 'rss', '', 'star', 'block'];
    },
  },
  props: {
    mode: String,
    type: String,
  },
  render(createElement) {
    const cssClasses = {};
    let type = '';
    let content = '';
    if (this.sourceTypes.indexOf(this.type) !== -1) {
      type = this.type;
      cssClasses['source-icon'] = true;
      if (type) {
        cssClasses[`source-icon--${type}`] = true;
      } else {
        content = 'X';
      }
      return createElement('div', { class: cssClasses }, content);
    }
    let mode = 'md';
    if (this.mode) mode = this.mode;
    const componentName = `${mode}${this.type.charAt(0).toUpperCase() + this.type.slice(1)}`;
    return createElement(componentName, { class: cssClasses }, content);
  },
};
</script>

<style scoped>
.source-icon {
  display: inline-block;
  width: 18px;
  height: 18px;
  background-size: 100%;
  background-repeat: no-repeat;
}
.source-icon--telegram {
  background-image: url("../assets/telegram-logo.png");
}
.source-icon--rss {
  background-image: url("../assets/rss-logo.png");
}
.source-icon--twitter {
  background-image: url("../assets/twitter-logo.png");
}
.source-icon--star {
  background-image: url("../assets/Shape.svg");
}
.source-icon--block {
  background-image: url("../assets/Block.svg");
}
.source-icon--share {
  color: black;
}

</style>
