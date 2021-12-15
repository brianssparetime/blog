<template>
  <div class="post">
    <!--
    <h1>{{ post.title }}</h1>
    <p class="lead">{{ post.description }}</p>
    <p>
      <i>{{ formatDate(post.date) }}</i>
    </p>
    <v-tags :tags="post.tags" />
    -->
    <PostCard :post="post" />
    <nuxt-content :document="post" />
  </div>
</template>
<script>

import Prism from '~/plugins/prism'

export default {
  async asyncData ({ params, error, $content }) {
    try {
      const postPath = `/posts/${params.slug}`
      const [post] = await $content('posts', { deep: true })
        .where({ dir: postPath })
        .fetch()
      return { post }
    } catch (err) {
      error({
        statusCode: 404,
        message: 'Page could not be found'
      })
    }
  },
  computed: {
    postInfo () {
      const post = this.post || {}
      const { body, ...rest } = post
      return rest
    },
    ogImageLoc () {
      if (process.env.NODE_ENV === 'development') {
        return this.post.image
      } else {
        const newname = this.post.image.replace(/\.\w+$/, '_tn.png')
        return 'gen_tn_imgs/' + newname
      }
    }
  },
  /* env: {
    baseUrl: process.env.BASE_URL || 'http://localhost:3000'
  }, */
  mounted () {
    Prism.highlightAll()
  },
  methods: {
    formatDate (date) {
      const options = { year: 'numeric', month: 'long', day: 'numeric' }
      return new Date(date).toLocaleDateString('en', options)
    }
  },
  head () {
    return {
      title: this.post.title,
      meta: [
        {
          hid: 'description',
          name: 'description',
          content: this.post.description
        },
        {
          hid: 'og:image',
          property: 'og:image',
          // content: 'https://brianssparetime.com' + require(`@/content${this.post.dir}/gen_tn_imgs/${this.post.image.replace(/\.\w+$/, '_tn.png')}`)
          content: 'https://brianssparetime.com' + require(`@/content${this.post.dir}/${this.ogImageLoc}`)
        },
        {
          hid: 'og:url',
          property: 'og:url',
          content: 'https://brianssparetime.com' + this.$route.fullPath
        }
      ]
    }
  }
}
</script>

<style>
/* not scoped*/
.post {
  margin-bottom: 50px;
  margin-top: 0px;
}

.nuxt-content {
  margin-top: 2rem;
}

.nuxt-content h1 {
  margin-bottom: 1.5rem;
  margin-top: 3.5rem;
}
.nuxt-content h2 {
  margin-bottom: 1.5rem;
  margin-top: 2rem;
}

.nuxt-content ol {
  margin-bottom: 1.5rem;
  font-weight: bold;
}
</style>
