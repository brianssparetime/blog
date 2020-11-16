<template>
  <div class="posts">
    <h1>Tags: {{ $route.params.slug }}</h1>
    <div v-if="!posts.length" class="results">
      No posts found for this tag
    </div>
    <PostCard v-for="post in posts" :key="post.dir" :post="post" />
  </div>
</template>
<script>
export default {
/*
  props: {
    postlimit: {
      type: int,
      required: false,
      default: 5
    }
  },
*/
  // why error on int here but not in postlist?
  async asyncData ({ params, error, $content }) {
    try {
      const posts = await $content('posts', { deep: true })
        .where({ tags: { $contains: params.slug } })
        // why error on this but not in postlist.vue?
        // .limit(this.postlimit)
        .without('body')
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
  data (params) {
    return {
      title: 'Tag: ' + this.$route.params.slug
    }
  },
  head () {
    return {
      title: this.title,
      meta: [
        {
          hid: 'description',
          name: 'description',
          content: 'Cool nuxt blog tags'
        }
      ]
    }
  }
}
</script>
<style scoped>
.results {
  padding-top: 20px;
}
</style>
