<template>
  <div class="wrapper">
    <nav class="main-nav">
      <Burger></Burger>
      <nuxt-link class="logo" to="/">Brian's Spare Time</nuxt-link>
    </nav>
    <Sidebar>
      <ul class="sidebar-panel-nav">
        <li><a href="#home">Home</a></li>
        <li><a href="#about">About</a></li>
        <li><a href="#contact">Contact</a></li>
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
export default {
  components: {
    Burger,
    Sidebar,
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
  font-family: "Arial", sans-serif;
  font-size: 16px;
  box-sizing: border-box;
}

p {
  margin-bottom: 10px;
}

.logo {
  font-weight: bold;
  text-align: left;
  display: block;
  color: black;
  font-size: 30px;
  margin: 0 0 2rem 2rem;
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
  max-width: 720px;
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

ul.sidebar-panel-nav > li > a {
  color: #fff;
  text-decoration: none;
  font-size: 1.5rem;
  display: block;
  padding-bottom: 0.5em;
}
</style>
