<!--
NOT USED ANYMORE
-->
<template>
  <div class="posts">
    <h3>Brewing</h3>
    <!--I like to brew beer and mead-->
    <PostCard v-for="post in posts" :key="post.dir" :post="post" />
  </div>
</template>
<script>
import PostCard from '~/components/PostCard'
const filttags = ['brewing', 'ale', 'beer', 'mead', 'acerglyn']
export default {
  components: {
    PostCard
  },
  async asyncData ({ params, error, $content }) {
    try {
      const posts = await $content('posts', { deep: true })
        .where({ tags: { $containsAny: filttags } })
        // https://github.com/techfort/LokiJS/wiki/Query-Examples#find-queries
        .without('body')
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
        }
      ]
    }
  }
}
</script>
