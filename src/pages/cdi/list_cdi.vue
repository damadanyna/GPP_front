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
        <v-card title="Liste des CDI" flat>
          <template v-slot:text>
            <v-text-field v-model="search" label="Search" prepend-inner-icon="mdi-magnify" variant="outlined" hide-details single-line></v-text-field>
          </template>
          <v-data-table :headers="headers" :items="list_encours" @click:row="onRowClick"  v-model="selectedItems"  item-value="Numero_pret" :search="search" fixed-header height="400px" item-key="id"  >
            <!-- Slot pour tronquer l'ID -->
            <template v-slot:item.ID="{ item }">
              {{ item.ID ? item.ID.slice(0, 2) : '' }}
            </template>
          </v-data-table>
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

const headers= [
  {
    align: 'start',
    sortable: false,
  },
    // { key: 'ID', title: 'ID' },
    // { key: 'ID.1', title: 'ID.1' },
    // { key: 'ErrorMessage', title: 'ErrorMessage' },
    { key: 'ProcessStatus', title: 'ProcessStatus' },
    { key: 'ProcessDate', title: 'ProcessDate' },
    { key: 'ValidationStatus', title: 'ValidationStatus' },
    { key: 'OrderingBank', title: 'OrderingBank' },
    { key: 'OrderingBranch', title: 'OrderingBranch' },
    { key: 'VoucherNumber', title: 'VoucherNumber' },
    { key: 'RecordType', title: 'RecordType' },
    { key: 'PaymentRef', title: 'PaymentRef' },
    { key: 'ChequeType', title: 'ChequeType' },
    { key: 'ChequeAmt', title: 'ChequeAmt' },
    { key: 'ChequeNumber', title: 'ChequeNumber' },
    { key: 'OrderingRib', title: 'OrderingRib' },
    { key: 'OrderingName', title: 'OrderingName' },
    { key: 'OrderingAddr', title: 'OrderingAddr' },
    { key: 'BeneficiaryBank', title: 'BeneficiaryBank' },
    { key: 'BeneficiaryBranch', title: 'BeneficiaryBranch' },
    { key: 'BeneficiaryRib', title: 'BeneficiaryRib' },
    { key: 'BeneficiaryName', title: 'BeneficiaryName' },
    { key: 'BeneficiaryAddr', title: 'BeneficiaryAddr' },
    { key: 'DateChqIssue', title: 'DateChqIssue' },
    { key: 'PaymentDetails', title: 'PaymentDetails' },
    { key: 'RepresentReason', title: 'RepresentReason' },
    { key: 'ClearanceDate', title: 'ClearanceDate' },
    { key: 'DatePresented', title: 'DatePresented' },
    { key: 'SettlementDate', title: 'SettlementDate' },
    { key: 'RejectCode', title: 'RejectCode' },
    { key: 'CanRcpFile', title: 'CanRcpFile' },
    { key: 'FtId', title: 'FtId' },
    { key: 'OlbFtId', title: 'OlbFtId' },
    { key: 'RevOlbFt', title: 'RevOlbFt' },
    { key: 'HoldIntmCdtFt', title: 'HoldIntmCdtFt' },
    { key: 'OVERRIDE', title: 'OVERRIDE' },
    { key: 'RECORD.STATUS', title: 'RECORD.STATUS' },
    { key: 'CURR.NO', title: 'CURR.NO' },
    // { key: 'INPUTTER', title: 'INPUTTER' },
    // { key: 'DATE.TIME', title: 'DATE.TIME' },
    // { key: 'AUTHORISER', title: 'AUTHORISER' },
    { key: 'CO.CODE', title: 'CO.CODE' },
    { key: 'DEPT.CODE', title: 'DEPT.CODE' },
    { key: 'AUDITOR.CODE', title: 'AUDITOR.CODE' },
    { key: 'AUDIT.DATE.TIME', title: 'AUDIT.DATE.TIME' },
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

const get_list_cdi = async (offset, limit) => {
  try {
    const response = await api.get(`/api/get_list_cdi?offset=${offset}&limit=${limit}`);

    for (let index = 0; index < response.data.list_of_data.length; index++) {
      const element = response.data.list_of_data[index];
      data_temp.value.push (element);
      list_encours.value.push (element);
      console.log(list_encours.value);

    }

  } catch (error) {
    console.error("❌ Erreur lors de la récupération des fichiers:", error);
  }
};
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
  const rowElement = event.target.closest('tr');

  // console.log(item.item);
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
const loadAllEncours = async () => {
  const step = 10;
  for (let offset = 0; offset < 100; offset += step) {
    await get_list_cdi(offset, step);
  }

  await get_list_a_traiter();
};

const onRowClick_atraiter_=()=>{

  dialog_a_traiter.value = true;

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


onMounted(async ()=>{
  loadAllEncours();
  // get_list_a_traiter()
  const allData = await getAllData();
  list_encours.value = allData;
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
