<template>
  <div class="img">
    <nuxt-link tag="img" :src="imgSrc()" :to="postlink()" :alt="alt" />
  </div>
</template>

<script>
export default {
  props: {
    src: {
      type: String,
      required: true
    },
    alt: {
      type: String,
      required: true
    }
  },
  methods: {
    imgSrc () {
      // const path = require("path");
      try {
        const { post } = this.$parent
        return require(`~/content${post.dir}/${this.src}`)
      } catch (error) {
        console.log('error with finding image  ' + this.src)
        return null
      }
    },
    postlink () {
      const { post } = this.$parent
      return post.dir
    }
  }
}
</script>

<style scoped>
.img {
  border: 1px solid #eee;
  border-radius: 5px;
  padding: 5px;
  display: inline-block;
  max-width: fit-content;
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
