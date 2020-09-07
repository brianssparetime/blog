<template>
  <div class="posts">
    <h3>Brewing</h3>
    <!--I like to brew beer and mead-->
    <PostCard v-for="post in posts" :key="post.dir" :post="post" />
  </div>
</template>
<script>
import PostCard from "~/components/PostCard";
const filttags = ["brewing", "ale", "beer", "mead", "acerglyn"];
export default {
  components: {
    PostCard,
  },
  async asyncData({ params, error, $content }) {
    try {
      // const posts = await $content("posts", { deep: true }).fetch();
      console.log("ft = " + filttags);
      console.log("pebt = " + process.env.brewing_tags);
      const posts = await $content("posts", { deep: true })
        // .where({ "post.tags": { $in: ["mead", "brewing"] } })
        // .where({ tags: { $in: ["mead", "brewing"] } })
        // .where({ title: "Mead Experiment" })
        // .where({ dirp: "mead-experiment" })
        // .where({ tags: { $contains: filttags } })
        // .where({ tags: { $contains: process.env.brewing_tags } })
        // .where({ tags: { $contains: ["mead", "brewing", "beer", "acerglyn", "ale"] }, })
        .where({ tags: { $contains: ["mead", "brewing"] } })
        /* currently, this returns posts where the supplied tags are a subset of the 
        posts tags.

        Problem 1)  I don't like having this defined here, but I can't get it to work 
        defined elsewhere.  This maybe because of problem 2.

        Problem 2) I want this to return posts where any tag is among the supplied tags


        */
        .without("body")
        .fetch();
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
