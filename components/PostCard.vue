<template>
  <div class="post">
    <v-img-pc class="img" :src="post.image" alt="Cat" />
    <div>
      <nuxt-link :to="post.dir">
        <h3 class="heading">
          {{ post.title }}
        </h3>
      </nuxt-link>
      <p>
        <i>{{ formatDate(post.date) }}</i>
      </p>
      <p>{{ post.description }}</p>
      <v-tags :tags="post.tags" />
    </div>
  </div>
</template>

<script>
export default {
  props: {
    post: {
      type: Object,
      required: true
    }
  },
  methods: {
    formatDate (date) {
      const options = { year: 'numeric', month: 'long', day: 'numeric' }
      return new Date(date).toLocaleDateString('en', options)
    }
  }
}
</script>

<style scoped>
.post {
  border-radius: 8px;
  box-shadow: 1px 1px 10px 0 rgba(32, 33, 36, 0.1);
  padding: 15px 20px;
  margin: 10px 0;
  display: flex;
}
.img {
  width: 200px;
  min-width: 100px;
  margin-right: 10px;
  padding: 0;
  display: inline-block;
  position: relative;
}
.img /deep/ img {
  /*position: absolute;*/
  width: 100%;
  height: 100%;
  max-height: 150px;
  /*object-fit: cover;*/
  display: inline-block;
  object-fit: contain;
}
.heading {
  margin-bottom: 5px;
}
</style>
