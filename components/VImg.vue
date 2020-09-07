<template>
  <div class="img">
    <img :src="imgSrc()" :alt="alt" />
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
        const { post } = this.$parent;
        console.log("start");
        if (this.dirp !== null) {
          console.log("new path");
          return require(`~/content/posts/${this.dirp}/${this.src}`);
        } else if (typeof this.$parent !== "undefined") {
          console.log("old path");
          return require(`~/content${post.dir}/${this.src}`);
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
}
img {
  max-width: 100%;
  width: 100%;
  /*object-fit: cover;*/
  object-fit: contain;
}
</style>
