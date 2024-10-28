<template>
  <v-card class="mx-auto px-4 py-4 pb-6" max-width="600" title="Новое видео" subtitle="Загрузка на сервер и запуск процесса разметки">
    <v-form
      v-model="form"
      @submit.prevent="onSubmit"
    >

      <v-file-input
        class="py-4"
        label="Файл"
        show-size
        v-model="file"
        variant="outlined"
      ></v-file-input>

      <v-btn
        :disabled="!form"
        :loading="loading"
        color="success"
        size="large"
        type="submit"
        variant="elevated"
        block
      >
        Старт
      </v-btn>
    </v-form>
  </v-card>
</template>


<script setup>
const onSubmit = () => {
  console.log('sent')
}

</script>

<script>
export default {
  data: () => ({
    form: false,
    file: undefined,
    loading: false,
  }),
}
</script>
