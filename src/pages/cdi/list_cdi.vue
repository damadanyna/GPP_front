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

            <template #item.index="{ index }">
              {{ index + 1 }}
            </template>
          </v-data-table>
        </v-card>
      </v-tabs-window-item>

      <!-- Dialogue qui affiche un formulaire en lecture seule -->
      <v-dialog v-model="dialog" width="auto">
        <v-card style="padding: 10px 20px; max-height: 90vh; overflow-y: auto;">
          <v-col>
            <v-card-title style="font-size: 12px;">{{ dialogTitle }}</v-card-title>
            <v-card-title style="font-size: 24; font-weight: bold;color: #FF5555;">{{ check_type() }}</v-card-title>
          </v-col>
          <v-card-text>
            <v-form>
              <v-container>
            <v-row dense>
              <v-col
                v-for="(value, key) in dialogData"
                :key="key"
                :cols="key === 'Référence de la lettre d’injonction (LI)' || key === 'Référence envoi de la lettre d’injonction' ? 12 : 6"
                sm="6"
                md="3"
              >
                <!-- Editable fields for LI references -->
                <v-text-field
                  v-if="key === 'Référence de la lettre d’injonction (LI)' || key === 'Référence envoi de la lettre d’injonction'"
                  :label="key"
                  v-model="dialogData[key]"
                  dense
                  variant="outlined"
                  class="green-border"
                 @keyup="check_key_state()"
                />
                <!-- File input fields for PJ references and fillers -->
                <v-file-input
                @change="check_key_state()"
                  v-else-if="key === 'Référence de la pièce justificative (PJ)' || key === 'FILLER2' || key === 'FILLER3'"
                  :label="key"
                  v-model="dialogData[key]"
                  dense
                  variant="outlined"
                  class="green-border"
                  accept="application/pdf,image/*"
                />
                <!-- Readonly text fields for other keys -->
                <v-text-field
                  v-else
                  :label="key"
                  :model-value="value"
                  readonly
                  dense
                  variant="outlined"
                  style="opacity: .8;"
                />
              </v-col>
            </v-row>
          </v-container>

            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="addIt"   :disabled="!is_full" :color="is_full ? 'red' : 'gray'"  variant="flat" class="ml-2">Charger le formulaire?</v-btn>
            <v-btn @click="closeDialog" color="green" variant="flat" class="ml-2">Non</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>




      <v-tabs-window-item value="two">
        <button class="customize_btn" @click="onRowClick_atraiter_">
          <v-icon icon="mdi mdi-download-circle" size="24" />
          Génerer le '.txt'
        </button>
        <v-card title="LISTE DES DOSSIERS A TRAITER" flat>
          <template v-slot:text>
            <v-text-field v-model="search" label="Search" prepend-inner-icon="mdi-magnify" variant="outlined" hide-details single-line></v-text-field>
          </template>
          <v-data-table :headers="headers_a_traiter" :items="list_a_traiter_"   v-model="selectedItems_a_traiter"  item-value="Numero_pret" :search="search_a_traiter" fixed-header height="400px" item-key="id"  ></v-data-table>
        </v-card>
      </v-tabs-window-item>
    </v-tabs-window>


    <v-dialog v-model="dialog_a_traiter" width="auto">
      <v-card style=" padding: 10px 20px;">
        <v-card-title style=" font-size: 12px;">Confirmation</v-card-title>
        <v-card-text>
          Générer le '.txt' de ces éléments?
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
import { onMounted ,watch} from "vue";
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
    { title: '#', value: 'index', sortable: false },
    // { key: 'ID', title: 'ID' },
    // { key: 'ID.1', title: 'ID.1' },
    // { key: 'ErrorMessage', title: 'ErrorMessage' },

    { key: 'BeneficiaryName', title: 'BeneficiaryName' },
    { key: 'OrderingBank', title: 'OrderingBank' },
    { key: 'ChequeAmt', title: 'ChequeAmt' },
    { key: 'ChequeNumber', title: 'ChequeNumber' },
    { key: 'ChequeType', title: 'ChequeType' },
    { key: 'ProcessStatus', title: 'ProcessStatus' },
    { key: 'ProcessDate', title: 'ProcessDate' },
    { key: 'ValidationStatus', title: 'ValidationStatus' },
    { key: 'OrderingBranch', title: 'OrderingBranch' },
    { key: 'VoucherNumber', title: 'VoucherNumber' },
    { key: 'RecordType', title: 'RecordType' },
    { key: 'OrderingRib', title: 'OrderingRib' },
    { key: 'OrderingName', title: 'OrderingName' },
    { key: 'PaymentRef', title: 'PaymentRef' },
    { key: 'OrderingAddr', title: 'OrderingAddr' },
    { key: 'BeneficiaryBank', title: 'BeneficiaryBank' },
    { key: 'BeneficiaryBranch', title: 'BeneficiaryBranch' },
    { key: 'BeneficiaryRib', title: 'BeneficiaryRib' },
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
  { key: "id", title: "Id" },
  { key: "code_etablissement", title: "Code de l'établissement" },
  { key: "code_agence", title: "Code de l'Agence" },
  { key: "ordering_rib", title: "Ordering Rib" },
  { key: "identification_tiers", title: "Identification de(s) tiers" },
  { key: "identification_contrevenants", title: "Identification du(s) contrevenant(s)" },
  { key: "type_moyen_paiement", title: "Type du moyen de paiement" },
  { key: "numero_moyen_paiement", title: "Numéro du moyen de paiement" },
  { key: "montant_moyen_paiement", title: "Montant du moyen de paiement" },
  { key: "date_emission", title: "Date d'émission" },
  { key: "date_presentation", title: "Date de présentation" },
  { key: "date_echeance", title: "Date d'échéance" },
  { key: "identification_beneficiaire", title: "Identification du bénéficiaire" },
  { key: "nom_beneficiaire", title: "Nom du bénéficiaire" },
  { key: "nom_banque_presentateur", title: "Nom de la Banque présentateur" },
  { key: "motif_refus", title: "Motif du refus" },
  { key: "solde_compte_rejet", title: "Solde du compte au moment de rejet" },
  { key: "sens_solde", title: "Sens du solde" },
  { key: "reference_effet_impaye", title: "Référence de l'effet impayé" },
  { key: "reference_lettre_injonction", title: "Référence de la lettre d'injonction" },
  { key: "date_lettre_injonction", title: "Date d'établissement de la lettre d'injonction" },
  { key: "reference_envoi_lettre_injonction", title: "Référence envoi de la lettre d'injonction" },
  { key: "date_envoi_lettre_injonction", title: "Date d'envoi de la lettre d'injonction" },
  { key: "existence_pj", title: "Existence de la pièce justificative (PJ)" },
  { key: "date_pj", title: "Date de la pièce justificative" },
  { key: "reference_pj", title: "Référence de la pièce justificative (PJ)" },
  { key: "filler2", title: "Filler 2" },
  { key: "filler3", title: "Filler 3" },
  { key: "filler4", title: "Filler 4" },
  { key: "filler5", title: "Filler 5" },
  { key: "Creating_date", title: "Date de création" },
  { key: "group_of", title: "Group of" },
  { key: "Date_enreg", title: "Date d'enregistrement" },
  { key: "is_create", title: "Is create" }

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
let is_full=ref(true)
const selected=ref()
const dialogData=ref([])
const dialog = ref(false);
const dialog_a_traiter = ref(false);
const dialogTitle = ref('');
const dialogContent = ref('');
const selectedItems = ref([]); // <- Ici on récupère les items sélectionnés
const selectedItems_a_traiter = ref([]); // <- Ici on récupère les items sélectionnés
const selectedRow = ref(null);
const list_a_traiter_ = ref(null);
const data_temp=ref([])

   // ✅ Réagit à toute modification de dialogData
watch(dialogData, () => {
      check_key_state();
  }, { deep: true });


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
    const response = await api.get(`/api/get_liste_cdi`);

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

function check_type() {
  const parts = selected.value.split('-');
  const code = parts[6]; // index 6, si RecordType contient au moins 7 segments

  if (code === '30' || code === '40') {
    return 'Chèque rejeté';
  } else if (code === '10') {
    return 'Virement rejeté';
  }

  return 'Type inconnu';
}


// Classe de la ligne sélectionnée
const onRowClick = (event,item) => {
  const rowElement = event.target.closest('tr');
  selectedRow.value=item.item
  document.querySelectorAll('tr.red-row').forEach(row => {
    row.classList.remove('red-row');
  });
  if (rowElement) {
    rowElement.classList.add('red-row');
  }
  selected.value=item.item.ID
  openDialog('Creer le CDI?','Créez le GPP pour: '+ item.item.Numero_pret,item.item)
};

// Fonction pour ouvrir le dialogue avec des paramètres personnalisés
const openDialog = (title,content,data) => {
  dialogTitle.value = title;
  dialogContent.value = content;
  dialog.value = true;
  dialogData.value= transformDialogData(data)
};
const closeDialog = () => {
  dialog.value = false;
  dialog_a_traiter.value = false;
};
const addIt = async () => {
  closeDialog()
  usePopupStore().show_notification.status=true
  usePopupStore().show_notification.message='Effectué'
  usePopupStore().show_notification.ico='mdi mdi-check'

  let object_elt=
  {"Code de l'établissement":dialogData.value["Code de l'établissement"],
  "Code de l'Agence":dialogData.value["Code de l'Agence"],
  "OrderingRib":dialogData.value["OrderingRib"],
  "Identification de(s) tiers contrevenant(s)":dialogData.value["Identification de(s) tiers contrevenant(s)"],
  "Identification du 1er, 2è, … contrevenants mandataires signataires":dialogData.value["Identification du 1er, 2è, … contrevenants mandataires signataires"],
  "Type du moyen de paiement":dialogData.value["Type du moyen de paiement"],
  "Numéro du moyen de paiement":dialogData.value["Numéro du moyen de paiement"],
  "Montant du moyen de paiement":dialogData.value["Montant du moyen de paiement"],
  "Date d’émission":dialogData.value["Date d’émission"],
  "Date de présentation":dialogData.value["Date de présentation"],
  "Date d’échéance":dialogData.value["Date d’échéance"],
  "Identification du bénéficiaire":dialogData.value["Identification du bénéficiaire"],
  "Nom du bénéficiaire":dialogData.value["Nom du bénéficiaire"],
  "Nom de la Banque présentateur ":dialogData.value["Nom de la Banque présentateur "],
  "Motif du refus":dialogData.value["Motif du refus"],
  "Solde du compte au moment de rejet":dialogData.value["Solde du compte au moment de rejet"],
  "Sens du solde":dialogData.value["Sens du solde"],
  "Référence de l’effet impayé":dialogData.value["Référence de l’effet impayé"],
  "Référence de la lettre d’injonction (LI)":dialogData.value["Référence de la lettre d’injonction (LI)"],
  "Date d’établissement de la lettre d’injonction":dialogData.value["Date d’établissement de la lettre d’injonction"],
  "Référence envoi de la lettre d’injonction":dialogData.value["Référence envoi de la lettre d’injonction"],
  "Date d’envoi de la lettre d’injonction":dialogData.value["Date d’envoi de la lettre d’injonction"],
  "Existence de la pièce justificative (PJ)":dialogData.value["Existence de la pièce justificative (PJ)"],
  "Date de la pièce justificative":dialogData.value["Date de la pièce justificative"],
  "Référence de la pièce justificative (PJ)":dialogData.value["Référence de la pièce justificative (PJ)"].name,
  "FILLER2":dialogData.value["FILLER2"].name,
  "FILLER3":dialogData.value["FILLER3"].name,
  "FILLER4":dialogData.value["FILLER4"],
  "FILLER5":dialogData.value["FILLER5"]}

  // 2. Récupère les fichiers (de type File)
  let files = {
    "FILLER2": dialogData.value["FILLER2"], // fichier
    "FILLER3": dialogData.value["FILLER3"], // fichier
    "RéférencePJ": dialogData.value["Référence de la pièce justificative (PJ)"] // fichier
  };

  send_selected_credit(object_elt,files)
  // get_list_a_traiter()
};

function add_date(dateStr, daysToAdd) {
  if (!/^\d{8}$/.test(dateStr)) return ''; // vérifie le format YYYYMMDD

  const year = parseInt(dateStr.substring(0, 4));
  const month = parseInt(dateStr.substring(4, 6)) - 1; // Mois en JS : 0-11
  const day = parseInt(dateStr.substring(6, 8));

  const date = new Date(year, month, day);
  date.setDate(date.getDate() + daysToAdd);

  const dd = String(date.getDate()).padStart(2, '0');
  const mm = String(date.getMonth() + 1).padStart(2, '0'); // reviens à 1-12
  const yyyy = date.getFullYear();

  return `${dd}/${mm}/${yyyy}`;
}
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
const send_selected_credit = async (data, files) => {
  try {
    const formData = new FormData();

    // Ajouter les données (en JSON string)
    formData.append("row_data", JSON.stringify(data));

    // Ajouter les fichiers (seulement s’ils existent)
    if (files.FILLER2) formData.append("FILLER2", files.FILLER2);
    if (files.FILLER3) formData.append("FILLER3", files.FILLER3);
    if (files.RéférencePJ) formData.append("RéférencePJ", files.RéférencePJ);

    const response = await api.post('/api/insert_cdi_row', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    console.log("✅ Réponse de l'API :", response.data);
  } catch (error) {
    console.error("❌ Erreur lors de l'envoi du crédit sélectionné :", error);
  }
};
const loadAllEncours = async () => {
    await get_list_cdi(0, 100);
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
    headers.map(h => `${(row[h.key] ?? "").toString().replace(/"/g, '""')}"`).join(";")
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
function getCurrentDateYYYYMMDD() {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0'); // Mois de 1 à 12
  const day = String(today.getDate()).padStart(2, '0');
  return `${year}${month}${day}`;
}
const checkEmptyFields = () => {
  const keysToCheck = [
    "Référence de la pièce justificative (PJ)",
    "FILLER2",
    "FILLER3",
    "Référence de la lettre d’injonction (LI)",
    "Référence envoi de la lettre d’injonction"
  ];

  const emptyFields = keysToCheck.filter((key) => {
    const value = dialogData.value[key];
    return (
      !value ||
      (typeof value === 'string' && value.trim() === '') ||
      (value instanceof File && value.size === 0) ||
      (Array.isArray(value) && value.length === 0)
    );
  });

  if (emptyFields.length > 0) {
    return false;
  }
  return true;
};

const check_key_state =()=>{

  is_full.value= checkEmptyFields();
}

function transformDialogData(sourceData) {
  const mapping = {
    "BeneficiaryRib": "000"+sourceData.OrderingRib,
    "Code de l'établissement" : sourceData.ID.split("-")[2],
    "Code de l'Agence" :sourceData.ID.split("-")[3],
    "OrderingRib": '000'+sourceData.OrderingRib,
    "Identification de(s) tiers contrevenant(s)": "", // champ libre ou à mapper
    "Identification du 1er, 2è, … contrevenants mandataires signataires": "", // champ libre
    "Type du moyen de paiement": "CH", // à mapper si connu (ex: ChequeType)
    "Numéro du moyen de paiement" : sourceData.ChequeNumber,
    "Montant du moyen de paiement": sourceData.ChequeAmt,
    "Date d’émission": add_date(sourceData.ProcessDate,0) ,
    "Date de présentation": add_date(sourceData.DatePresented,0) ,
    "Date d’échéance":add_date(sourceData.ProcessDate,0),
    "Identification du bénéficiaire": '' ,
    "Nom du bénéficiaire": sourceData.BeneficiaryName,
    "Nom de la Banque présentateur ": sourceData.OrderingName,
    "Motif du refus": "", // pourrait être sourceData.RejectCode ou ErrorMessage ?
    "Qolde du compte au moment de rejet": "", // probablement sourceData.ProcessStatus ou autre
    "Solde du compte au moment de rejet": "", // champ libre
    "Sens du solde": "", // champ libre
    "Référence de l’effet impayé":"",
    "Référence de la lettre d’injonction (LI)":"",
    "Date d’établissement de la lettre d’injonction":add_date(getCurrentDateYYYYMMDD(),2),// ou OlbFtId selon contexte
    "Référence envoi de la lettre d’injonction":"",
    "Date d’envoi de la lettre d’injonction":add_date(getCurrentDateYYYYMMDD(),2),
    "Existence de la pièce justificative (PJ)":"Non",
    "Date de la pièce justificative":add_date(getCurrentDateYYYYMMDD(),2),// ou OlbFtId selon contexte
    "Référence de la pièce justificative (PJ)":"",
    "FILLER2":"",
    "FILLER3":"",
    "FILLER4":"",
    "FILLER5":""
  };

  // ordre final exact, y compris répétitions
 // ordre final exact, y compris répétitions et nouveaux champs
const finalOrder = [
  "BeneficiaryRib",
  "Code de l'établissement",
  "Code de l'Agence",
  "OrderingRib",
  "Identification de(s) tiers contrevenant(s)",
  "Identification du 1er, 2è, … contrevenants mandataires signataires",
  "Type du moyen de paiement",
  "Type du moyen de paiement",
  "Numéro du moyen de paiement",
  "Montant du moyen de paiement",
  "Date d’émission",
  "Date de présentation",
  "Date d’échéance",
  "Identification du bénéficiaire",
  "Nom du bénéficiaire",
  "Nom de la Banque présentateur ",
  "Motif du refus",
  "Qolde du compte au moment de rejet",
  "Solde du compte au moment de rejet",
  "Sens du solde",
  "Référence de l’effet impayé",
  "Référence de la lettre d’injonction (LI)",
  "Référence envoi de la lettre d’injonction",
  "Date d’établissement de la lettre d’injonction",
  "Date d’envoi de la lettre d’injonction",
  "Existence de la pièce justificative (PJ)",
  "Date de la pièce justificative",
  "Référence de la pièce justificative (PJ)",
  "FILLER2",
  "FILLER3",
  "FILLER4",
  "FILLER5"
];
  const transformed = {};
  for (const key of finalOrder) {
    transformed[key] = mapping[key] ?? "";
  }
  return transformed;
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
.green-border .v-input__control {
  border: none;
  border: 2px solid rgb(255, 255, 255) ;
  border-radius: 10px;
}

.green-border .v-input__control:focus-within {
  border: none;
  border-radius: 10px;

}

  </style>
