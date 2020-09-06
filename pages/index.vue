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
  async asyncData({ params, error, $content }) {
    try {
      const posts = await $content("posts", { deep: true }).fetch();
      return { posts };
    } catch (err) {
      error({
        statusCode: 404,
        message: "Page could not be found",
      });
    }
  },
  head() {
    return {
      title: "BriansSpareTime",
      meta: [
        {
          hid: "description",
          name: "description",
          content: "Cool nuxt blog",
        },
      ],
    };
  },
};
</script>
