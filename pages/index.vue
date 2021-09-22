<template>
  <div class="posts">
    I'm Brian and this is some stuff I've done in my spare time...
    <BR /><BR />
    <BR /><BR />
    <h3>Posts</h3>
    <PostCard v-for="post in posts" :key="post.dir" :post="post" />
    <BR /><BR />
    The code that runs this blog is on <a href="https://github.com/brianssparetime/blog">github</a>.
  </div>
</template>
<script>
import PostCard from '~/components/PostCard'
export default {
  components: {
    PostCard
  },
  async asyncData ({ params, error, $content }) {
    try {
      const posts = await $content('posts', { deep: true })
        .where({ tags: { $containsNone: ['work-in-progress'] } })
        .sortBy('date', 'desc')
        .fetch()

      return { posts }
    } catch (err) {
      error({
        statusCode: 404,
        message: 'Page could not be found'
      })
    }
  },
  head () {
    return {
      title: 'BriansSpareTime',
      meta: [
        {
          hid: 'description',
          name: 'description',
          content: 'Cool nuxt blog'
        },
        {
          hid: 'og:image',
          property: 'og:image',
          // content: process.env.baseUrl + '/favicon.ico'
          content: 'https://brianssparetime.com/favicon.ico'
        }
      ]
    }
  }
}
</script>
