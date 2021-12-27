<template>
  <div class="img">
    <nuxt-link tag="img" :src="imgSrcFancy('tn')" :to="postlink()" :alt="alt" />
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
    imgSrcFancy (imgsize) {
      try {
        // if in production, unless no imgsize is specified, use .imgs instead of fullsize
        const { post } = this.$parent
        // if (imgsize === '' || imgsize === 'orig' || process.env.NODE_ENV === 'development') {
        // // if (imgsize === '') { // temporarily force always use .imgs for testing only
        //   console.log('fallback on full-rez load')
        //   return require(`~/content${post.dir}/${this.src}`)
        // } else { // production and imgsize not empty
        const path = require('path')
        const ext = path.extname(this.src)
        const name = path.basename(this.src, ext)
        const loadstring = `~/content${post.dir}/gen_tn_imgs/${name}_${imgsize}.png`
        console.log('fancy load from ' + loadstring)
        return require(`~/content${post.dir}/gen_tn_imgs/${name}_tn.png`) // working
        // hacked to make tn literal for memory usage maybe?
        // }
      } catch (error) {
        console.log('error with finding image for:  ' + this.src)
        console.log(error)
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
  /*border: 1px solid #eee;*/
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
