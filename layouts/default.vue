<template>
  <div class="wrapper">
    <nav class="main-nav">
      <Burger></Burger>
      <nuxt-link class="logo" to="/">Brian's Spare Time</nuxt-link>
    </nav>
    <Sidebar>
      <ul class="sidebar-panel-nav" @click="closeSidebarPanel">
        <li>
          <nuxt-link to="/"><b>Home</b></nuxt-link>
        </li>
        <li>&#8226; <nuxt-link to="/posts">All posts</nuxt-link></li>
        <li>&#8226; <nuxt-link to="/tags">Search by tag</nuxt-link></li>
        <li class="padded"><b>Main Interests:</b></li>
        <li>
          &#8226;
          <a href="https://www.youtube.com/channel/UCnKrfUKulxwGP51NpVvmolA">
            BrianGoesFlyin on YT
          </a>
        </li>
        <li>&#8226; <nuxt-link to="/interests/brewing">Brewing</nuxt-link></li>
        <li>
          &#8226;
          <nuxt-link to="/interests/vintage-computing">
            Vintage Computing</nuxt-link
          >
        </li>
        <!--
          <li>&#8226; <nuxt-link to="/ee">EE</nuxt-link></li>
        <li>&#8226; <nuxt-link to="/vintcomp">Vintage Computers</nuxt-link></li>
        <li>&#8226; <nuxt-link to="/wood">Wood Working</nuxt-link></li>
        -->
      </ul>
    </Sidebar>
    <div class="wrapper-inner">
      <nuxt />
    </div>
  </div>
</template>

<script>
import Burger from "../components/Burger.vue";
import Sidebar from "../components/Sidebar.vue";
import { mutations } from "../store/drawer.js";
export default {
  components: {
    Burger,
    Sidebar,
  },
  methods: {
    closeSidebarPanel: mutations.toggleNav,
  },
  head() {
    return {
      title: "BriansSpareTime",
    };
  },
};
</script>
<style>
html {
  /*font-family: "Lucida Grande", "Lucida Sans Unicode", "Lucida Sans", Geneva,
    "Arial", sans-serif;*/
  font-family: medium-content-serif-font, Georgia, Cambria, "Times New Roman",
    Times, serif;
  font-size: 16px;
  box-sizing: border-box;
}

p {
  margin-bottom: 10px;
}

.logo {
  font-weight: 600;
  font-family: "Lucida Grande", "Lucida Sans Unicode", "Lucida Sans", Geneva,
    "Arial", sans-serif;
  /*font-weight: bold;*/
  text-align: left;
  display: block;
  color: black;
  /*font-size: 30px;*/
  line-height: 40px;
  font-size: 36px;
  letter-spacing: -0.022em;
  margin: 0 0 0.5rem 2rem;
  text-decoration: none;
}

*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
}

.wrapper {
  margin: 0 auto;
  padding: 2rem;
}

.wrapper-inner {
  /*max-width: 720px;*/
  max-width: 1024px;
  margin: 0 auto;
  padding: 2rem;
}

.main-nav {
  display: flex;
  /*justify-content: space-between;*/
  /*padding: 0.5rem 0.8rem;*/
  padding: 0.5rem 0rem;
}

ul.sidebar-panel-nav {
  list-style-type: none;
}

ul.sidebar-panel-nav > li {
  text-decoration: none;
  font-size: 1rem;
  display: block;
  padding-bottom: 0.5rem;
}
.padded {
  padding-top: 2rem;
}
</style>
