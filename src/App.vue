<template>
  <v-app>
    <v-navigation-drawer v-model="drawer" :rail="rail" permanent @click="rail = false">
      <v-list-item prepend-avatar="./assets/logo.png" title="GPP App" nav>
        <template v-slot:append>
          <v-btn icon="mdi-chevron-left" variant="text" @click.stop="rail = !rail"></v-btn>
        </template>
      </v-list-item>
      <v-divider></v-divider>

      <v-list density="compact" nav style=" margin-top: 50px;">
        <v-list-item v-for="item,i in listItems" :key="i" :prepend-icon="item.icon" :title="item.title" :value="item.value" :to="item.to"></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <router-view  style=" padding: 40px 20px;" />
    </v-main>
  </v-app>
</template>

<script setup>
import {onMounted, ref } from 'vue';
import router from './router/index';

onMounted(() => {
    router.replace('/dec_credit');
});




const drawer = ref(true);
const rail = ref(true);

const listItems = ref([
  {icon:'mdi-cash-plus',title:'Déclarations des Crédits',value:'Declaration_credit',to:'/dec_credit'},
  {icon:'mdi-cash-fast',title:'Déclarations des Encours',value:'Declaration_encours',to:'/dec_encours'},
  {icon:'mdi-receipt-text-clock-outline',title:'Encours',value:'Encours',to:'/etat_encours'},
])
</script>
