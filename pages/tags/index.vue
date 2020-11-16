<template>
  <div class="tags">
    <h3>Tags:</h3>
    <v-tags :tags="taglist" />
    <!-- <div v-for="tag in taglist" :key="tag">
      <nuxt-link :to="`/tags/${tag}`">{{ tag }}</nuxt-link>
      &nbsp;
    </div>-->
  </div>
</template>
<script>
export default {
  async asyncData ({ params, error, $content }) {
    // try {
    const posts = await $content('posts', { deep: true }).only('tags').fetch()
    const tagset = new Set()
    console.log('debug working now')
    for (const p of posts) {
      console.log('post = ' + p)
      console.log('tags = ' + p.tags)
      for (const t of p.tags) {
        console.log('tag = ' + t)
        tagset.add(t)
      }
    }
    console.log('tagset = ')
    console.log(tagset)
    const taglist = Array.from(tagset)
    return { taglist }
    /* } catch (err) {
      console.log("error fuck");
      error({
        statusCode: 404,
        message: "Page could not be found foo",
      });
    } */
  },
  head () {
    return {
      title: 'BST: Tags',
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
