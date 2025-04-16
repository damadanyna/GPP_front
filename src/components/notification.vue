<template>
  <div>

    <div v-if="!is_loading" id="not_elt">
      <span>Valider cette opération?</span>
      <div style=" display: flex;width: 100%;display: flex; justify-content: end;">
        <v-col  cols="auto">
          <v-btn elevation="2" @click="load_database" color="green"  size="small">Oui</v-btn>
        </v-col>
        <v-col cols="auto">
          <v-btn @click="toogle_popup"  variant="outlined" size="small">Non</v-btn>
        </v-col>
      </div>
    </div>
    <div v-else style=" color: white; font-size: 24px; font-weight: bold;">
        <span>Chagement ...</span>
    </div>
  </div>
</template>

<script setup>

import { ref } from 'vue'
import api from '@/api/axios';
import { usePopupStore } from '../stores/store'

const is_loading=ref(false);
const toogle_popup=()=>{
  usePopupStore().togglePopup()

}
const load_database = async () => {
  is_loading.value = true;
  console.log(usePopupStore().loadFile);

  try {
    const response = await api.post('/api/create_table', {
      filename: usePopupStore().loadFile
    });

    console.log("Résultat de l'insertion :", response.data);
  } catch (error) {
    console.error("Erreur lors du chargement du fichier dans la base :", error);
  }

  setTimeout(() => {
    usePopupStore().togglePopup();
  }, 2000);
};


</script>

<style   scoped>
#not_elt{
  background: white;
  color: black;
  width: 400px;
  padding: 10px 30px;
  border-radius: 10px;
}
v-btn{
  font-size: 8px;
}

</style>
