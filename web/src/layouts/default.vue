<template>
  <v-responsive class="border rounded">
    <v-app :theme="theme" class="bg-surface-light">
      <v-app-bar class="pr-4"  title="GPT Enjoyers" >

        <v-spacer></v-spacer>
        <v-btn
          :prepend-icon="theme === 'light' ? 'mdi-weather-sunny' : 'mdi-weather-night'"
          :text="theme === 'light' ? 'Светлая' : 'Темная'"
          slim
          @click="onClick"
        ></v-btn>
      </v-app-bar>

      <v-main>
        <v-container>
          <router-view />
        </v-container>
      </v-main>
    </v-app>
  </v-responsive>
</template>

<script lang="ts" setup>
import { ref } from 'vue'

const theme = ref('light')

function onClick () {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
}
</script>
