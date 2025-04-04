<!-- src/pages/home.vue or src/components/home.vue -->
<template>
  <div>
    <div style=" display: flex; width: 100%; justify-content: end;">
      <span>Déclarations des crédits</span>
    </div>
    <v-card style="margin-top: 50px; position: sticky; top: 0; z-index: 10; background-color: transparent;">
      <v-tabs v-model="tab" >
        <v-tab value="one">Création</v-tab>
        <v-tab value="two">Listes</v-tab>
      </v-tabs>

      <v-tabs-window v-model="tab" style="margin-top: 50px; background-color: #212121; padding: 20px 40px; border-radius: 10px;">
        <v-tabs-window-item value="one" style=" ">
          <v-icon icon="mdi mdi-account-filter-outline"></v-icon>
          <span> Recherches</span>
          <div style="display: grid; width: 100%; grid-template-columns: repeat(2, 1fr); align-items: center; margin-top: 12px; padding: 20px 30px;">
            <v-combobox label="Agence" :items="listAgence" variant="solo-filled" style=" margin-right: 10px;"></v-combobox>
            <v-text-field label="N° Client" variant="solo-filled" style=" margin-left: 10px;"></v-text-field>
            <v-text-field label="Code Arrangement" variant="solo-filled" style=" margin-right: 10px;"></v-text-field>
            <v-combobox label="Arrangement - Nom client" style=" margin-left: 10px;" :items="['California', 'Colorado', 'Florida', 'Georgia', 'Texas', 'Wyoming']" variant="solo-filled"></v-combobox>
          </div>
          <v-card title="Etat des Encours" flat>
            <!-- <v-text-field v-model="search" label="Search" prepend-inner-icon="mdi-magnify" variant="outlined" hide-details single-line></v-text-field> -->
            <v-data-table :headers="headers" :items="desserts" :search="search"></v-data-table>
          </v-card>
        </v-tabs-window-item>

        <v-tabs-window-item value="two">
          <v-card-text>Listes</v-card-text>
        </v-tabs-window-item>
      </v-tabs-window>
    </v-card>

  </div>
</template>

<script setup>
import { ref } from "vue";

const tab = ref("one");

const search= ''
const headers= [
          {
            align: 'start',
            key: 'name',
            sortable: false,
            title: 'Dessert (100g serving)',
          },
          { key: 'calories', title: 'Calories' },
          { key: 'fat', title: 'Fat (g)' },
          { key: 'carbs', title: 'Carbs (g)' },
          { key: 'protein', title: 'Protein (g)' },
          { key: 'iron', title: 'Iron (%)' },
        ]
const  desserts= [
          {
            name: 'Frozen Yogurt',
            calories: 159,
            fat: 6.0,
            carbs: 24,
            protein: 4.0,
            iron: 1,
          },
          {
            name: 'Ice cream sandwich',
            calories: 237,
            fat: 9.0,
            carbs: 37,
            protein: 4.3,
            iron: 1,
          },
          {
            name: 'Eclair',
            calories: 262,
            fat: 16.0,
            carbs: 23,
            protein: 6.0,
            iron: 7,
          },
          {
            name: 'Cupcake',
            calories: 305,
            fat: 3.7,
            carbs: 67,
            protein: 4.3,
            iron: 8,
          },
          {
            name: 'Gingerbread',
            calories: 356,
            fat: 16.0,
            carbs: 49,
            protein: 3.9,
            iron: 16,
          },
          {
            name: 'Jelly bean',
            calories: 375,
            fat: 0.0,
            carbs: 94,
            protein: 0.0,
            iron: 0,
          },
          {
            name: 'Lollipop',
            calories: 392,
            fat: 0.2,
            carbs: 98,
            protein: 0,
            iron: 2,
          },
          {
            name: 'Honeycomb',
            calories: 408,
            fat: 3.2,
            carbs: 87,
            protein: 6.5,
            iron: 45,
          },
          {
            name: 'Donut',
            calories: 452,
            fat: 25.0,
            carbs: 51,
            protein: 4.9,
            iron: 22,
          },
          {
            name: 'KitKat',
            calories: 518,
            fat: 26.0,
            carbs: 65,
            protein: 7,
            iron: 6,
          },
        ]

const listAgence = ref([
      '00001','00002','00003','00004','00005','00006','00007','00008','00009','00010','00011','00012','00013','00021','00022','00023','00024','00025','00031','00041','00051','00052','00053','00054','00061',
])
</script>
