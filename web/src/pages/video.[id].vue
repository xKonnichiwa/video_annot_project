<template>
  <v-breadcrumbs :items="items"></v-breadcrumbs>

  <v-card v-if="file" class="px-4 py-4 mb-4" max-height="500px" title="Сцены"
          subtitle="Здесь можно посмотреть каждую сцену подробно" :loading="loading">
    <v-tabs
      v-model="tab"
      color="primary"
      direction="horizontal"
      class="overflow-x-auto"
      show-arrows
    >
      <v-tab v-for="scene in file.scenes" :text="'#'+scene.id" :value="'tab-'+scene.id"></v-tab>
    </v-tabs>
  </v-card>

  <v-tabs-window v-model="tab" v-if="file">
    <v-tabs-window-item v-for="(scene, id) in file.scenes" :value="'tab-'+scene.id">


      <v-card v-if="file" class="px-4 pb-4 pt-6 mb-4" max-height="500px" :loading="loading">
        <v-timeline align="center" side="start" direction="horizontal"
                    :truncate-line=" id === 0 ? 'start' : id === file.scenes.length -1 ? 'end' : undefined ">
          <v-timeline-item
            dot-color="teal-lighten-3"
            size="small"
            class=""
          >
            <div class="d-flex flex-column align-center justify-center">
              <strong>{{ scene.time_from }}</strong>
              <div class="text-caption mb-2">
                Начало
              </div>
            </div>
          </v-timeline-item>

          <v-timeline-item
            dot-color="teal-lighten-3"
            size="small"
          >
            <div class="d-flex flex-column align-center justify-center">
              <strong>{{ scene.time_to }}</strong>
              <div class="text-caption mb-2">
                Конец
              </div>
            </div>
          </v-timeline-item>
        </v-timeline>

      </v-card>

      <v-card class="px-4 py-4 mb-4" max-height="500px" title="Видео"
              subtitle="Анализ по видео каналу" :loading="loading">
        <v-container>
          <v-row no-gutters>
            <v-col cols="12" sm="4">
              <v-card-subtitle>Объекты</v-card-subtitle>
              <v-card-text class="py-0" v-for="item in scene.detections">
                {{ item.avg }}% - {{ item.class }}
              </v-card-text>
            </v-col>
            <v-col cols="12" sm="4">
              <v-card-subtitle>События</v-card-subtitle>
              <v-card-text class="py-0" v-for="item in scene.events">
                {{ item.probability }}% - {{ item.name }}
              </v-card-text>
            </v-col>
            <v-col cols="12" sm="4">
              <v-card-subtitle>Эмоции</v-card-subtitle>
              <v-card-text class="py-0" v-for="item in scene.faces">
                {{ item.emotion_probability }}% - {{ item.emotion_label }}
              </v-card-text>
            </v-col>
          </v-row>
        </v-container>
      </v-card>

      <v-card v-if="file" class="px-4 py-4 mb-4" max-height="500px" title="Аудио. Транскрипция"
              subtitle="Формирование текста по аудио каналу" :loading="loading">
        <v-card-text>{{ scene.transcription }}</v-card-text>
      </v-card>

      <v-card v-if="file" class="px-4 py-4 mb-4" max-height="500px" title="Сводка"
              subtitle="Краткий пересказ через LLM" :loading="loading">
        <v-card-text>{{ scene.summary }}</v-card-text>
      </v-card>

      <v-card v-if="file" class="px-4 py-4 mb-4" max-height="500px" title="Аудио. Тональность"
              subtitle="Определение эмоциональной окраски" :loading="loading">
        <v-card-text>{{ scene.sentiment_confidence }}% - {{ scene.sentiment_label }}</v-card-text>
      </v-card>

      <v-card v-if="file" class="px-4 py-4 mb-4" max-height="500px" title="Аудио. Тип аудио"
              subtitle="Определение класса аудио" :loading="loading">
        <v-card-text>{{ scene.clap_labels }}</v-card-text>
      </v-card>

      <v-card v-if="file" class="px-4 py-4 mb-4" max-height="500px" title="Аудио. Метка-триггер"
              subtitle="Определение слов триггеров / синонимов" :loading="loading">
        <v-card-text>{{ scene.labeled_transcriptions }}</v-card-text>
      </v-card>

    </v-tabs-window-item>
  </v-tabs-window>
</template>


<script setup>
const onSubmit = () => {
  console.log('sent')
}

</script>

<script>
import {http} from "@/shared";
import {fi} from "vuetify/locale";

export default {
  data: () => ({
    tab: null,
    items: [{
      title: 'Главная',
      disabled: false,
      to: '/'
    }, {
      title: `Карточка видео`,
    }],
    form: false,
    file: undefined,
    loading: false,
  }),
  mounted() {
    this.load();
  },
  methods: {
    async load() {
      this.loading = true;
      try {
        const result = await http.request(`/api/v1/video/${this.$route.params.id}`, {}, {}, {}, 'GET')
        this.file = result.data;
        console.log(result)
      } finally {
        this.loading = false;
      }
    },
    formatDetection(scene) {
      return scene.detections.map(s => {
        return s.class + ` (${s.avg})`
      }).join(',');
    }
  },
}
</script>
