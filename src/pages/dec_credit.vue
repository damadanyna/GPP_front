<!-- src/pages/home.vue or src/components/home.vue -->
<template>
  <v-card style=" position: sticky; top: 0; z-index: 10; background-color: transparent; overflow: hidden;">
    <v-tabs v-model="tab" >
      <v-tab value="one">Création</v-tab>
      <v-tab value="two">Listes</v-tab>
    </v-tabs>
    <v-tabs-window v-model="tab" style="margin-top: 50px; background-color: #212121; padding: 5px 40px; border-radius: 10px;">
      <v-tabs-window-item value="one" style=" ">
        <v-card title="Etat des Encours" flat>
          <template v-slot:text>
            <v-text-field v-model="search" label="Search" prepend-inner-icon="mdi-magnify" variant="outlined" hide-details single-line></v-text-field>
          </template>
          <v-data-table
            :headers="headers" :items="list_encours" @click:row="onRowClick"  v-model="selectedItems"  item-value="Numero_pret" :search="search" fixed-header height="400px" item-key="id"  ></v-data-table>
        </v-card>
      </v-tabs-window-item>

      <v-tabs-window-item value="two">
        <v-card-text>Listes</v-card-text>
      </v-tabs-window-item>
    </v-tabs-window>
  </v-card>

</template>

<script setup>
import { ref } from "vue";
import axios from 'axios';
import { onMounted } from "vue";

const tab = ref("one");

// Déclaration des variables réactives
const search = ref('');

const headers= [
  {
    align: 'start',
    key: 'Numero_pret',
    sortable: false,
    title: 'Code Dossier',
  },
  { key: 'Agence', title: 'Agence' },
{ key: 'identification_client', title: 'identification_client' },
{ key: 'Numero_pret', title: 'Numero_pret' },
{ key: 'linked_appl_id', title: 'linked_appl_id' },
{ key: 'Date_pret', title: 'Date_pret' },
{ key: 'Date_fin_pret', title: 'Date_fin_pret' },
{ key: 'Nom_client', title: 'Nom_client' },
{ key: 'Produits', title: 'Produits' },
{ key: 'Amount', title: 'Amount' },
{ key: 'Duree_Remboursement', title: 'Duree_Remboursement' },
{ key: 'taux_d_interet', title: 'taux_d_interet' },
{ key: 'Nombre_de_jour_retard', title: 'Nombre_de_jour_retard' },
{ key: 'payment_date', title: 'payment_date' },
{ key: 'Statut_du_client', title: 'Statut_du_client' },
{ key: 'Capital_Non_appele_ech', title: 'Capital_Non_appele_ech' },
{ key: 'Capital_Appele_Non_verse', title: 'Capital_Appele_Non_verse' },
{ key: 'Total_capital_echus_non_echus', title: 'Total_capital_echus_non_echus' },
{ key: 'Total_interet_echus', title: 'Total_interet_echus' },
{ key: 'OD Pen', title: 'OD Pen' },
{ key: 'OD & PEN', title: 'OD & PEN' },
{ key: 'Solde du client', title: 'Solde du client' },
{ key: 'Agent_de_gestion', title: 'Agent_de_gestion' },
{ key: 'Secteur_d_activité', title: 'Secteur_d_activité' },
{ key: 'Secteur_d_activité_code', title: 'Secteur_d_activité_code' },
{ key: '.Agent_de_gestion', title: '.Agent_de_gestion' },
{ key: 'Code_Garantie', title: 'Code_Garantie' },
{ key: 'Valeur_garantie', title: 'Valeur_garantie' },
{ key: 'arr_status', title: 'arr_status' }


        ]
const  list_encours=ref([])

const selectedItems = ref([]); // <- Ici on récupère les items sélectionnés
// const selectedRow = ref(null);

const get_encours = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:5000/api/get_encours?offset=10000');
    // console.log(response.data.files);
    console.log(response.data.list_of_data);
    list_encours.value=response.data.list_of_data


    // ecours_list.value=response.data// Affichage des fichiers reçus
  } catch (error) {
    console.error("Erreur lors de la récupération des fichiers:", error); // Gestion des erreurs
  }
};

// Classe de la ligne sélectionnée
const onRowClick = (event,item) => {
  const rowElement = event.target.closest('tr');

  console.log(item.item);

  // Supprime la classe rouge de toutes les lignes (optionnel si tu veux une seule ligne en rouge)
  document.querySelectorAll('tr.red-row').forEach(row => {
    row.classList.remove('red-row');
  });

  // Ajoute la classe à la ligne cliquée
  if (rowElement) {
    rowElement.classList.add('red-row');
  }
};


// Exemple de transformation



onMounted(()=>{
  get_encours()
})


</script>

<style >
tbody{
  color: gray;
}
.red-row {
  background-color: rgba(0, 255, 17, 0.265) !important;
  color: white; /* optionnel pour meilleure visibilité */
}
  </style>
