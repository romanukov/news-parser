<template>
  <div class="video">
      <canvas ref="canvas" style="height: 100px; display: block" @click="opened=true"></canvas>
      <div v-show="opened" class="video__modal" @click="opened=false">
        <div @click.stop="()=>{}" style="margin: auto; text-align: center">
          <div>
            Click outside video for close
          </div>
          <div>
            <video preload="metadata" controls ref="video">
              <source :src="videoUrl" type="video/mp4">
            </video>
          </div>
          <div>
            <a :href="videoUrl">{{ videoUrl }}</a>
          </div>
        </div>
      </div>
  </div>
</template>
<style>
  .video {
    display: inline-block;
    color: #bbbbbb;
  }
  .video a {
    color: #bbbbbb;
  }
  .video__modal {
    position: fixed;
    display: flex;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 999999;
    background: rgba(0,0,0,0.6);
  }
</style>
<script>
export default {
  name: 'Message',
  data() {
    return {
      opened: false,
    };
  },
  props: {
    videoUrl: String,
  },
  mounted() {
    const videoEl = this.$refs.video;
    const canvasEl = this.$refs.canvas;
    videoEl.addEventListener('loadeddata', () => {
      canvasEl.width = videoEl.videoWidth;
      canvasEl.height = videoEl.videoHeight;
      canvasEl.getContext('2d').drawImage(videoEl, 0, 0, videoEl.videoWidth, videoEl.videoHeight);
    });
  },
};
</script>
