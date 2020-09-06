<template>
  <!-- Top Navbar -->
  <nav
    class="top-navbar flex flex-row align-center p-2 fixed w-full"
    style="z-index: 9001;"
  >
    <!-- Logo Brand -->
    <div class="flex-grow">
      <router-link :to="{ name: 'HomeView' }">
        <img alt="ImStallion Logo" :src="logoIcon" class="w-16 ml-3" />
      </router-link>
    </div>
    <!-- /Logo Brand -->

    <!-- Menu Button -->
    <button class="p-4" @click="toggle">
      <font-awesome-icon :icon="['fas', 'bars']" size="lg"></font-awesome-icon>
    </button>
  </nav>
  <!-- /Top Navbar -->
</template>