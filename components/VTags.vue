<template>
  <p class="tags">
    <span v-for="tag in tags" :key="tag" class="tag">
      <nuxt-link :to="`/tags/${tag}`">{{ tag }}</nuxt-link>&nbsp;
    </span>
  </p>
</template>

<script>
export default {
  props: {
    tags: {
      type: Array,
      default: () => []
    }
  }
}
</script>

<style scoped>
.tag a {
  color: white;
  text-decoration: none;
  margin: 5px 0;
  display: inline-block;
  border-radius: 3px;
}
</style>
