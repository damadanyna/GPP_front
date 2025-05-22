<!-- src/pages/home.vue or src/components/home.vue -->
<template>
  <v-card style=" position: sticky; top: 0; z-index: 10; background-color: transparent; overflow: hidden;">


    <popup_view v-if="usePopupStore().show_notification.status"></popup_view>
    <v-tabs v-model="tab" >
      <v-tab value="one">Chèques Entrants</v-tab>
      </v-tabs>
      <v-tabs-window v-model="tab" style="margin-top: 50px; background-color: #212121; padding: 5px 40px; border-radius: 10px;">
        <!--<v-tab value="two">Listes</v-tab>-->
      <v-tabs-window-item value="one" style=" ">
        <v-card title="Tout les chèques entrants" flat>
          <template v-slot:text>
            <v-text-field v-model="search" label="Rechercher..." prepend-inner-icon="mdi-magnify" variant="outlined" hide-details single-line></v-text-field>
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
        <button class="customize_btn" @click="onRowClick_atraiter_">
          <v-icon icon="mdi mdi-download-circle" size="24" />
          Crréer le GPP
        </button>
        <v-card title="LISTE DES DOSSIERS A TRAITER" flat>
          <template v-slot:text>
            <v-text-field v-model="search" label="Search" prepend-inner-icon="mdi-magnify" variant="outlined" hide-details single-line></v-text-field>
          </template>
          <v-data-table :headers="headers_a_traiter" :items="list_a_traiter_"   v-model="selectedItems_a_traiter"  item-value="Numero_pret" :search="search_a_traiter" fixed-header height="400px" item-key="id"  ></v-data-table>
        </v-card>
      </v-tabs-window-item>
    </v-tabs-window>

    <button style="position:  absolute; top: 20px; right: 20px;font-size: 12px; background-color: #212121; color: white; padding: 5px 10px; border-radius: 25px;" @click="load_database()">Charger</button>
<span style="position: absolute; top: 20vh; right: 40px;">{{ total }}</span>
    <!-- Dialogue qui sera contrôlé par la fonction -->
      <v-dialog v-model="dialog_a_traiter" width="auto">
        <v-card style=" padding: 10px 20px;">
          <v-card-title style=" font-size: 12px;">Confirmation</v-card-title>
          <v-card-text>
            Creer le Fichier d'échange GPP Solidis ?
          </v-card-text>
          <v-card-actions>
            <div class=""   style=" display: flex; flex-direction: row; align-items: center;">
              <button @click="Create_It" size="24" title="Annuler" style=" color: red  ; padding: 0px 7px; margin-left: 10px; border-radius: 25px;">Oui </button>
              <button @click="closeDialog" size="16" title="Charger le fichier" style=" background: green; padding: 0px 14px; margin-left: 10px; border-radius: 25px;">Non </button>
            </div>
          </v-card-actions>
        </v-card>
      </v-dialog>


  </v-card>

</template>

<script setup>
import api from "@/api/axios";
import { ref } from "vue";
import { onMounted } from "vue";
import { getData,getAllData } from '@/api/indexDB';
import { usePopupStore } from '../../stores/store'



// import Cookies from 'js-cookie';
// import Etat_encours from "./etat_encours.vue";

const tab = ref("one");

// Déclaration des variables réactives
const search = ref('');
const search_a_traiter = ref('');
const total= ref('...');
const headers= [
  {
    align: 'start',
    key: 'Numero_pret',
    sortable: false,
  },
  { key: 'ftid', title: 'ftid' },
  { key: 'processdate', title: 'processdate' },
  { key: 'recordtype', title: 'Enreg' },
  { key: 'chequenumber', title: 'Cheque' },
  { key: 'orderingrib', title: 'Tireur' },
  { key: 'beneficiaryrib', title: 'Benef' },
  { key: 'solde', title: 'Montant' },
  { key: 'code_anomalie', title: 'Code Anomalie' },
  { key: 'anomailie', title: 'Anomalie' },
  { key: 'ANO', title: 'ANO' }
]


const headers_a_traiter= [
  {
    align: 'start',
    key: 'Numero_pret',
    sortable: false,
  },
  { key: "Id", title: "Id" },
  { key: "Agence", title: "Agence" },
  { key: "Agec", title: "Agec" },
  { key: "Compte", title: "Compte" },
  { key: "Nom", title: "Nom" },
  { key: "Classt", title: "Classt" },
  { key: "Codape", title: "Codape" },
  { key: "Mntcaht", title: "Mntcaht" },
  { key: "Cli_n_a", title: "Cli_n_a" },
  { key: "Nature", title: "Nature" },
  { key: "Typecredit", title: "Typecredit" },
  { key: "Montant", title: "Montant" },
  { key: "Datech", title: "Datech" },
  { key: "Rang", title: "Rang" },
  { key: "Taux", title: "Taux" },
  { key: "Datouv", title: "Datouv" },
  { key: "Genre", title: "Genre" },
  { key: "Group_of", title: "Group_of" },
  { key: "Date_enreg", title: "Date_enreg" }

]

const header_model=[  { key: "Id", title: "Id" },
  { key: "Agence", title: "Agence" },
  { key: "Agec", title: "Agec" },
  { key: "Compte", title: "Compte" },
  { key: "Nom", title: "Nom" },
  { key: "Classt", title: "Classt" },
  { key: "Codape", title: "Codape" },
  { key: "Mntcaht", title: "Mntcaht" },
  { key: "Cli_n_a", title: "Cli_n_a" },
  { key: "Nature", title: "Nature" },
  { key: "Typecredit", title: "Typecredit" },
  { key: "Montant", title: "Montant" },
  { key: "Datech", title: "Datech" },
  { key: "Rang", title: "Rang" },
  { key: "Taux", title: "Taux" },
  { key: "Datouv", title: "Datouv" },
  { key: "Genre", title: "Genre" },
  { key: "Date_enreg", title: "Date_enreg" }
]

const  list_encours=ref([])

// Variables pour le dialogue
const dialog = ref(false);
const dialog_a_traiter = ref(false);
const dialogTitle = ref('');
const dialogContent = ref('');
const selectedItems = ref([]); // <- Ici on récupère les items sélectionnés
const selectedItems_a_traiter = ref([]); // <- Ici on récupère les items sélectionnés
const selectedRow = ref(null);
const list_a_traiter_ = ref(null);
const data_temp=ref([])

const get_chq = async (offset,limit) => {
  try {
    // Sinon on fait l'appel à l’API
    const response = await api.get(`/api/get_chq_in?offset=${offset}&limit=${limit}`);


    for (let index = 0; index < response.data.list_of_data.length; index++) {
      const element = response.data.list_of_data[index];
      data_temp.value.push (element);
      list_encours.value.push (element);
      // console.log(element);

    }

  } catch (error) {
    console.error("❌ Erreur lors de la récupération des fichiers:", error);
  }
};
const load_database = async () => {
  try {
    // Sinon on fait l'appel à l’API
    const response = await api.get(`/api/import_tables_to_sipem_app`);
    console.log(response);

  } catch (error) {
    console.log(error);

  }
}
const get_list_a_traiter = async ( ) => {
  try {
    const cacheKey = `a_traiter`;

    // D'abord, on essaie de récupérer depuis IndexedDB
    const cachedData = await getData(cacheKey);

    // console.log(cachedData);
    if (cachedData) {
      console.log('✅ Données chargées depuis IndexedDB');

    }
    // Sinon on fait l'appel à l’API
    const response = await api.get(`/api/get_liste_a_traiter`);

    list_a_traiter_.value = response.data.list_of_data;
    list_a_traiter_.value = list_a_traiter_.value.map(item => {
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
    // console.log(list_a_traiter_);

    usePopupStore().list_a_traiter=list_a_traiter_.value


    console.log('📡 Données récupérées depuis API et stockées localement',list_a_traiter_.value);

  } catch (error) {
    console.error("❌ Erreur lors de la récupération des fichiers:", error);
  }
};

// Classe de la ligne sélectionnée
const onRowClick = (event,item) => {
  // const rowElement = event.target.closest('tr');

  // // console.log(item.item);
  // selectedRow.value=item.item

  // // Supprime la classe rouge de toutes les lignes (optionnel si tu veux une seule ligne en rouge)
  // document.querySelectorAll('tr.red-row').forEach(row => {
  //   row.classList.remove('red-row');
  // });

  // // Ajoute la classe à la ligne cliquée
  // if (rowElement) {
  //   rowElement.classList.add('red-row');
  // }
  // openDialog('Notification?','Créez le GPP pour:  '+ item.item.Numero_pret)
};

// Fonction pour ouvrir le dialogue avec des paramètres personnalisés
const openDialog = (title , content) => {
  dialogTitle.value = title;
  dialogContent.value = content;
  dialog.value = true;
};
const closeDialog = () => {
  dialog.value = false;
  dialog_a_traiter.value = false;
};
const addIt = async () => {
// console.log(selectedItems);

  closeDialog()
  usePopupStore().show_notification.status=true
  usePopupStore().show_notification.message='Effectué'
  usePopupStore().show_notification.ico='mdi mdi-check'
  send_selected_credit()
  get_list_a_traiter()
};
const Create_It = async () => {
// console.log(selectedItems);
  create_gpp_()
  closeDialog()
  setTimeout(() => {
    usePopupStore().show_notification.status=true
    usePopupStore().show_notification.message="Le GPP Crée"
    usePopupStore().show_notification.ico='mdi mdi-check'
  }, 400);
  get_list_a_traiter()
  downloadCSVFromProxyData(list_a_traiter_.value,header_model)
  console.log(list_a_traiter_.value);

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

const onRowClick_atraiter_=()=>{

  // dialog_a_traiter.value = true;

};
const create_gpp_ = async () => {
  try {
    const response = await api.post("/api/update_is_create");

    const result = response.data;

    if (result.status === "success") {
      console.log("Mise à jour réussie :", result);
      console.log(`✔ ${result.updated} ligne(s) mise(s) à jour.\nGroup: ${result.group_of}`);
      // Optionnel : recharger la liste ici
    } else {
      console.error("Erreur lors de la mise à jour :", result.error);
      console.log(`❌ Erreur : ${result.error}`);
    }

  } catch (error) {
    console.error("Erreur API :", error);
    console.log("❌ Une erreur est survenue lors de l'appel API.");
  }
};

const loadAllEncours = async () => {
  const step = 1000;
  for (let offset = 0; offset < 10000; offset += step) {
    await  get_chq (offset, step);
  }

  await get_list_a_traiter();
};

onMounted(()=>{
  loadAllEncours()

  setTimeout(() => {
    total.value=0
    console.log(list_encours.value);
    for (let index = 0; index < list_encours.value.length; index++) {
        const soldeStr = list_encours.value[index].solde.replace(/,/g, '');
        total.value += parseFloat(soldeStr);
    }
    total.value=total.value+' Ar'

  }, 100);
})
function downloadCSVFromProxyData(proxyData, headers) {
  const dataArray = Array.from(proxyData);

  const csvHeaders = headers.map(h => h.title).join(";");
  const csvRows = dataArray.map(row =>
    headers.map(h => `"${(row[h.key] ?? "").toString().replace(/"/g, '""')}"`).join(";")
  );

  const csvContent = [csvHeaders, ...csvRows].join("\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");

  // 👉 Générer la date et l'heure au format voulu
  const now = new Date();
  const day = String(now.getDate()).padStart(2, '0');
  const month = String(now.getMonth() + 1).padStart(2, '0'); // janvier = 0
  const year = now.getFullYear();
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');

  const formattedDate = `${day}${month}${year}${hours}${minutes}${seconds}`;

  // 👉 Utiliser cette date comme nom de fichier
  link.href = URL.createObjectURL(blob);
  link.setAttribute("download", `RGPP_${formattedDate}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}




</script>

<style >
tbody{
  color: gray;
}
.red-row {
  background-color: rgba(0, 255, 17, 0.265) !important;
  color: white; /* optionnel pour meilleure visibilité */
}
.customize_btn {
  position: absolute;
  top: 10px;
  right: 20px;
  z-index: 10;
  background: green ;
  padding: 4px 10px;
  border-radius: 20px;
}

  </style>
