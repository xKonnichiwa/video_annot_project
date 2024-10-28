<template>
  <v-container class="px-0">
    <v-form class="d-flex">
      <v-text-field
        v-model="searchBar"
        class="mr-4"
        label="Введите запрос"
        variant="solo"
      ></v-text-field>

      <v-btn
        :loading="loading"
        color="success"
        size="large"
        type="button"
        variant="elevated"
        icon="mdi-magnify"
        @click="()=>search = searchBar"
      ></v-btn>
    </v-form>
  </v-container>

  <v-card class="mx-auto px-4 py-4" title="Результат поиска"
          subtitle="Список видео подходящих под условия">

    <v-data-table-server
      v-model:items-per-page="itemsPerPage"
      :headers="headers"
      :items="serverItems"
      :items-length="totalItems"
      :loading="loading"
      :search="search"
      hover
      item-selectable
      item-key="id"
      @update:options="loadItems"
      @click:row="rowClick"
    >
      <template v-slot:item.data-table-select>

      </template>

    </v-data-table-server>
  </v-card>
</template>
<script>
import {http} from '@/shared'

export default {
  data: () => ({
    itemsPerPage: 5,
    headers: [
      {
        title: 'ID',
        align: 'start',
        sortable: false,
        key: 'id',

      },
      {
        title: 'Название',
        align: 'start',
        sortable: false,
        value: 'name',
      },
    ],
    search: '',
    searchBar: '',
    serverItems: [],
    loading: true,
    totalItems: 0,
  }),
  methods: {
    rowClick(item, row) {
      this.$router.push(`/video/${row.item.id}`)
    },
    async loadItems({page, itemsPerPage}) {
      this.loading = true
      const result = await http.request('/api/v1/video', {}, {
        limit: itemsPerPage,
        offset: (page - 1) * itemsPerPage,
        search: this.search,
      }, {}, 'GET')

      this.serverItems = result.data.items;
      this.totalItems = result.data.meta.total;
      this.loading = false;
    },
  },
}
</script>
