<!-- src/pages/home.vue or src/components/home.vue -->
<template>
  <div>
    <h1>Historique de Déclarations</h1>
    <!-- Your home page content -->
    <v-card class="mx-auto">
  <v-list v-model:opened="open">
    <v-list-group
      v-for="(group, i) in list_final"
      :key="i"
      :value="group.group"
    >
      <template v-slot:activator="{ props }">
        <v-list-item
          v-bind="props"
          prepend-icon="mdi-folder"
          :title="group.label"
        />
      </template>

      <v-list-item>
        <table class="w-full text-sm border-collapse">
          <thead class="bg-gray-100">
            <tr>
              <th class="text-left px-4 py-2 border-b">Id</th>
              <th class="text-left px-4 py-2 border-b">Agence</th>
              <th class="text-left px-4 py-2 border-b">Compte</th>
              <th class="text-left px-4 py-2 border-b">Datech</th>
              <th class="text-left px-4 py-2 border-b">Datouv</th>
              <th class="text-left px-4 py-2 border-b">Nom et prénom</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(item, j) in group.children"
              :key="j"
              class="hover:bg-gray-50"
            >
              <td class="px-4 py-2 border-b">{{ item.Id }}</td>
              <td class="px-4 py-2 border-b">{{ item.Agence }}</td>
              <td class="px-4 py-2 border-b">{{ item.Compte }}</td>
              <td class="px-4 py-2 border-b">{{ item.Datech }}</td>
              <td class="px-4 py-2 border-b">{{ item.Datouv }}</td>
              <td class="px-4 py-2 border-b">{{ item.Nom }}</td>
            </tr>
          </tbody>
        </table>
      </v-list-item>
    </v-list-group>
  </v-list>
</v-card>


  </div>
</template>

<script setup>

import api from "@/api/axios";
import { onMounted } from "vue";
import { ref } from "vue";
// Home component logic
const open = ref(['Users'])
// const  admins=ref( [
//     ['Management', 'mdi-account-multiple-outline'],
//     ['Settings', 'mdi-cog-outline']
// ])
const list_donne=ref([])
const list_final=ref([])

const get_list_a_traiter = async ( ) => {
  try {

    // Sinon on fait l'appel à l’API
    const response = await api.get(`/api/get_liste_faites`);

    list_donne.value = response.data.list_of_data;
    list_donne.value = list_donne.value.map(item => {
      // Créer une copie de l'objet pour ne pas modifier l'original
        const newItem = { ...item };
        // Formater Datech si elle existe
        if (newItem.Datech) {
          const date = new Date(newItem.Datech);
          newItem.Datech = date.getDate().toString().padStart(2, '0') + '.' +
                              (date.getMonth() + 1).toString().padStart(2, '0') + '.' +
                              date.getFullYear();
        }
        // Formater Datouv si elle existe
        if (newItem.Datouv) {
          const date = new Date(newItem.Datouv);
          newItem.Datouv = date.getDate().toString().padStart(2, '0') + '.' +
                          (date.getMonth() + 1).toString().padStart(2, '0') + '.' +
                          date.getFullYear();
        }

        return newItem;
      });

      list_final.value = groupArray(list_donne.value)
      console.log(list_final.value);

    // console.log('📡 Données récupérées depuis API et stockées localement',list_donne.value);
  } catch (error) {
    console.error("❌ Erreur lors de la récupération des fichiers:", error);
  }
};

const groupArray = (data) => {
  const groupedMap = {}

  // Grouper les objets selon la valeur de 'group_of'
  for (const item of data) {
    const group = item.Group_of
    if (!groupedMap[group]) {
      groupedMap[group] = []
    }
    groupedMap[group].push(item)
  }

  // Construire la liste finale avec la structure demandée
  const result = Object.entries(groupedMap).map(([group, children]) => ({
    group: group,
    label: children[0].Creating_date,
    children: children
  }))

  return result
}



onMounted(()=>{
  get_list_a_traiter();
  // Regrouper les objets par leur valeur group_of

})
</script>
