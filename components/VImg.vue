<template>
  <div class="img">
    <!-- <a :href="imgSrc()">
      <img :src="imgSrc()" :alt="alt">
    </a> -->
    <a :href="imgSrcFancy('large')">
      <img :src="imgSrcFancy('large')" :alt="alt">
    </a>
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
    },
    dirp: {
      type: String,
      required: false,
      default: null
    }
  },
  methods: {
    imgSrc () {
      // const path = require("path");
      try {
        console.log(process.env.NODE_ENV)
        console.log('dirp=' + this.dirp)
        if (this.dirp !== null) {
          console.log('new path')
          return require(`~/content${this.dirp}/${this.src}`)
        } else {
          console.log('fell through else')
        }
      } catch (error) {
        console.log('error with finding image  ' + this.src)
        return null
      }
    },
    imgSrcFancy (imgsize) {
      try {
        // if in production, unless no imgsize is specified, use .imgs instead of fullsize
        // if (imgsize === '' || process.env.NODE_ENV === 'development') {
        if (imgsize === '') { // temporarily force always use .imgs for testing only
          console.log('fallback on full-rez load')
          return require(`~/content${this.dirp}/${this.src}`)
        } else { // production and imgsize not empty
          const path = require('path')
          const ext = path.extname(this.src)
          const name = path.basename(this.src, ext)
          const loadstring = `~/content${this.dirp}/.imgs/${name}_${imgsize}${ext}`
          console.log('fancy load from ' + loadstring)
          return require(`~/content${this.dirp}/.imgs/${name}_${imgsize}${ext}`)
        }
      } catch (error) {
        console.log('error with finding image for:  ' + this.src)
        console.log(error)
        return null
      }
    }
  }
}
</script>

<style scoped>
.img {
  /* border: 1px solid #eee; */
  border-radius: 5px;
  padding: 5px;
  display: inline-block;
  margin-bottom: 2rem;
  margin-top: 1.5rem;
  /* margin-left: 50%; */
  /* transform: translateX(-50%); */
}
img {
  max-height: 600px;
  width: 100%;
  max-width: 100% ;
  /* width: auto ; */
  height: auto ;
  display: inline-block;
  object-fit: contain;
}
</style>
