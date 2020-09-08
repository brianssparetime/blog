<template>
  <div class="posts">
    <h3>Posts</h3>
    <PostCard v-for="post in posts" :key="post.dir" :post="post" />
  </div>
</template>
<script>
import PostCard from "~/components/PostCard";
export default {
  components: {
    PostCard,
  },
  props: {
    filttags: {
      type: Array,
      required: false,
      default: null,
    },
    postlimit: {
      type: int,
      required: false,
      default: 5,
    },
  },
  async asyncData({ params, error, $content }) {
    /* how do I set this up so that I don't have a million if statements 
    to configure the asycn request?
    */

    try {
      const posts = await $content("posts", { deep: true })
        .where({ tags: { $containsAny: this.filttags } })
        .limit(this.postlimit)
        .without("body")
        .sortBy("date", "desc")
        .fetch();

      return { posts };
    } catch (err) {
      error({
        statusCode: 404,
        message: "Page could not be found",
      });
    }
  },
};
</script>


<style scoped>
</style>