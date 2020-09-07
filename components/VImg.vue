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
        // if (post.hasOwnProperty("dir")) {
        if (this.dirp !== null) {
          console.log("new path");
          // return require(`~/content/${this.dirp}/img/${this.src}`);
          // return require(`/content/posts/${this.dirp}/img/${this.src}`);
          // return require(`/Users/bhoward/jstest2/bst-blog/content/posts/img/${this.src}`);

          /*
          problem is that the path below always seems to make require return undefined
          can't figure out what it's supposed to be relative to
          but clearly it's different if the vue component is called from the markdown
          vs if it's called from the VImg.vue file.
          */
          return require(`~/content/posts/${this.dirp}/${this.src}`);
        } else if (typeof this.$parent !== "undefined") {
          // } else if ("dir" in post) {
          console.log("old path");
          // return require(`~/content${post.dir}/img/${this.src}`);
          return require(`~/content${post.dir}/${this.src}`);
        } else {
          console.log("fell through else");
        }
      } catch (error) {
        console.log("error with finding image  " + this.src);
        if (this.src === "IMG_6371.jpg") {
          console.log(error);
          // console.log("path cwd . = " + process.cwd());
        }
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
