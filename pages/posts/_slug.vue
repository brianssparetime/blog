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
          // content: process.env.baseUrl + this.post.dir + '/' + this.post.image
          // not sure why the above doesn't work...
          content: 'https://brianssparetime.com/_nuxt/content' + this.post.dir + '/' + this.post.image
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

.nuxt-content h2 {
  margin-bottom: 1.5rem;
  margin-top: 2rem;
}

.nuxt-content ol {
  margin-bottom: 1.5rem;
  font-weight: bold;
}
</style>
