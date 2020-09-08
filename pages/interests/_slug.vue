<template>
  <div class="interest">
    <h1>{{ interest.title }}</h1>
    <!--<p class="lead">{{ interest.description }}</p>-->
    <div class="tags">
      Tags:
      <v-tags :tags="interest.tags" />
    </div>
    <div class="nc">
      <nuxt-content :document="interest" />
    </div>
    <p v-if="interest.date" class="ludate">
      <i>Last updated {{ formatDate(interest.date) }}</i>
    </p>
    <hr />
    <h2>Recent related posts:</h2>
    <!--<li v-for="post in posts" :key="post.title">
      {{ post.title }}
    </li>-->
    <PostCard v-for="post in posts" :key="post.dir" :post="post" />
  </div>
</template>
<script>
import Prism from "~/plugins/prism";
// import PostCard from "~/components/PostCard";
export default {
  async asyncData({ params, error, $content }) {
    try {
      const intPath = `/interests/${params.slug}`;
      const [interestd] = await $content("interests", { deep: true })
        .where({ dir: intPath })
        .fetch();
      const posts = await $content("posts", { deep: true })
        .where({ tags: { $containsAny: interestd.tags } }) // this depends on above query
        .without("body")
        .sortBy("date", "desc")
        // .limit(5)
        .fetch();
      console.log("post data = " + JSON.stringify(posts));
      return { interest: interestd, posts };
      // return { interest }; // works
      // return { interest };
      //, post: post.data };
    } catch (err) {
      error({
        statusCode: 404,
        message: "Page could not be found",
      });
    }
  },
  computed: {
    /* intInfo() {
      const interest = this.interest || {};
      const { body, ...rest } = interest;
      return rest;
    }, */
  },
  mounted() {
    Prism.highlightAll();
  },
  methods: {
    formatDate(date) {
      if (date) {
        const options = { year: "numeric", month: "long", day: "numeric" };
        return new Date(date).toLocaleDateString("en", options);
      } else {
        return null;
      }
    },
  },
  head() {
    return {
      title: this.interest.title,
      meta: [
        {
          hid: "description",
          name: "description",
          content: this.interest.description,
        },
      ],
    };
  },
};
</script>

<style scoped>
.interest {
  margin-bottom: 50px;
  margin-top: 0px;
}
h1 {
  margin-bottom: 2rem;
}
h2 {
  margin-bottom: 2rem;
  margin-top: 2rem;
}
.lead {
  font-size: 0.9em;
}
.tags {
  display: inline-block;
}
.nc {
  margin-top: 2rem;
  margin-bottom: 2rem;
}
.ludate {
  margin-top: 2rem;
  margin-bottom: 2rem;
  font-size: 0.6em;
}
</style>
