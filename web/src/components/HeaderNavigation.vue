<template>
  <v-tabs fixed-tabs>
    <v-tab prepend-icon="mdi-text-search" to="/">Список</v-tab>
    <v-tab prepend-icon="mdi-video-plus" to="/video">Создание</v-tab>
    <v-tab prepend-icon="mdi-file-video-outline" to="/video/123">Карточка</v-tab>
  </v-tabs>
</template>
<script>
export default {
  data: () => ({
    tab: null,
  }),
}
</script>
