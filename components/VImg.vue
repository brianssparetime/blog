<template>
  <div class="img">
    <!--<nuxt-link tag="img" :src="imgSrc()" :to="imgSrc()" :alt="alt"> </nuxt-link>-->
    <!--<v-interpolation tag="img" :src="imgSrc()" :to="imgSrc()" :alt="alt">-->
    <!--<v-interpolation :src="imgSrc()" :to="imgSrc()" :alt="alt">-->
    <!--<v-interpolation tag="img" :src="imgSrc()" :to="imgSrc()" :alt="alt">
    </v-interpolation>-->
    <a v-interpolation :href="imgSrc()">
      <img :src="imgSrc()" :alt="alt" />
    </a>
  </div>
</template>

<script>
export default {
  props: {
    src: {
      type: String,
      required: true,
    },
    alt: {
      type: String,
      required: true,
    },
    dirp: {
      type: String,
      required: false,
      default: null,
    },
  },
  methods: {
    imgSrc() {
      // const path = require("path");
      try {
        console.log("start");
        console.log("dirp=" + this.dirp);
        if (this.dirp !== null) {
          console.log("new path");
          return require(`~/content${this.dirp}/${this.src}`);
        } else {
          console.log("fell through else");
        }
      } catch (error) {
        console.log("error with finding image  " + this.src);
        return null;
      }
    },
  },
};
</script>

<style scoped>
.img {
  border: 1px solid #eee;
  border-radius: 5px;
  padding: 5px;
  display: inline-block;
  margin-bottom: 2rem;
  margin-top: 1.5rem;
}
img {
  /*max-width: 100%;*/
  max-height: 400px;
  /*width: 100%;*/
  /*object-fit: cover;*/
  display: inline-block;
  object-fit: contain;
}
</style>
