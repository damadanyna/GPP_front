<!-- src/pages/home.vue or src/components/home.vue -->
<template>
  <v-card style=" position: sticky; top: 0; z-index: 10; background-color: transparent; overflow: hidden;">
    <popup_view v-if="usePopupStore().show_notification.status"></popup_view>
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
          <v-data-table :headers="headers" :items="list_encours" @click:row="onRowClick"  v-model="selectedItems"  item-value="Numero_pret" :search="search" fixed-header height="400px" item-key="id"  ></v-data-table>
        </v-card>
      </v-tabs-window-item>

      <!-- Dialogue qui sera contrôlé par la fonction -->
      <v-dialog v-model="dialog" width="auto">
        <v-card style=" padding: 10px 20px;">
          <v-card-title style=" font-size: 12px;">{{ dialogTitle }}</v-card-title>
          <v-card-text>
            {{ dialogContent }}
          </v-card-text>
          <v-card-actions>
            <div class=""   style=" display: flex; flex-direction: row; align-items: center;">
              <button @click="addIt()" size="24" title="Annuler" style=" color: red  ; padding: 0px 7px; margin-left: 10px; border-radius: 25px;">Oui </button>
              <button @click="closeDialog" size="16" title="Charger le fichier" style=" background: green; padding: 0px 14px; margin-left: 10px; border-radius: 25px;">Non </button>
            </div>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-tabs-window-item value="two">
        <v-card-text>Listes</v-card-text>
      </v-tabs-window-item>
    </v-tabs-window>
  </v-card>

</template>

<script setup>
import api from "@/api/axios";
import { ref } from "vue";
import { onMounted } from "vue";
import { saveData, getData,getAllData } from '@/api/indexDB';
import { usePopupStore } from '../stores/store'



// import Cookies from 'js-cookie';
// import Etat_encours from "./etat_encours.vue";

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

// Variables pour le dialogue
const dialog = ref(false);
const dialogTitle = ref('');
const dialogContent = ref('');
const selectedItems = ref([]); // <- Ici on récupère les items sélectionnés
const selectedRow = ref(null);


const get_encours = async (offset, limit) => {
  try {
    const cacheKey = `encours_${offset}_${limit}`;

    // D'abord, on essaie de récupérer depuis IndexedDB
    const cachedData = await getData(cacheKey);
    if (cachedData) {
      console.log('✅ Données chargées depuis IndexedDB');
      // list_encours.value = cachedData;
      return;
    }

    // Sinon on fait l'appel à l’API
    const response = await api.get(`/api/get_encours?offset=${offset}&limit=${limit}`);
    // list_encours.value = response.data.list_of_data;

    // Sauvegarde dans IndexedDB
    await saveData(cacheKey, response.data.list_of_data);
    console.log('📡 Données récupérées depuis API et stockées localement');

  } catch (error) {
    console.error("❌ Erreur lors de la récupération des fichiers:", error);
  }
};

// Classe de la ligne sélectionnée
const onRowClick = (event,item) => {
  const rowElement = event.target.closest('tr');

  console.log(item.item);
  selectedRow.value=item.item

  // Supprime la classe rouge de toutes les lignes (optionnel si tu veux une seule ligne en rouge)
  document.querySelectorAll('tr.red-row').forEach(row => {
    row.classList.remove('red-row');
  });

  // Ajoute la classe à la ligne cliquée
  if (rowElement) {
    rowElement.classList.add('red-row');
  }
  openDialog('Notification?','Créez le GPP pour:  '+ item.item.Numero_pret)
};

// Fonction pour ouvrir le dialogue avec des paramètres personnalisés
const openDialog = (title , content) => {
  dialogTitle.value = title;
  dialogContent.value = content;
  dialog.value = true;
};
const closeDialog = () => {
  dialog.value = false;
};
const addIt = async () => {
// console.log(selectedItems);

  closeDialog()
  usePopupStore().show_notification.status=true
  usePopupStore().show_notification.message='Effectué'
  usePopupStore().show_notification.ico='mdi mdi-check'

  send_selected_credit()
};


const send_selected_credit = async () => {
  try {
    if (!selectedRow.value) {
      console.warn("⚠️ Aucune ligne sélectionnée à envoyer.");
      return;
    }

    const response = await api.post('/api/insert_credit_row', {
      row_data: selectedRow.value
    });

    console.log("✅ Réponse de l'API :", response.data);
  } catch (error) {
    console.error("❌ Erreur lors de l'envoi du crédit sélectionné :", error);
  }
};


// Exemple de transformation

const loadAllEncours = async () => {
  const step = 1000;
  for (let offset = 0; offset < 10000; offset += step) {
    await get_encours(offset, step);
  }
};

onMounted(async ()=>{
  loadAllEncours();
  const allData = await getAllData();
  list_encours.value = allData;
  // console.log(allData);

  // get_encours(0,10000)
  // setTimeout(() => {
  //   get_encours(0,10000)
  // }, 200);
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
