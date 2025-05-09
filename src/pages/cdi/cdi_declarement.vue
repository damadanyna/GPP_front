<!-- src/pages/home.vue or src/components/home.vue -->
<template>

  <v-card style=" position: sticky; top: 13vh; z-index: 10; background-color: transparent; overflow: hidden;">
    <popup_view v-if="usePopupStore().show_notification.status"></popup_view>
        <button class="customize_btn" @click="onRowClick_atraiter_" >
          <v-icon icon="mdi mdi-plus" size="24" />
          Crréer le CDI
        </button>
        <v-card title="Liste des Déclaration" flat>
          <template v-slot:text>
            <v-text-field v-model="search" label="Search" prepend-inner-icon="mdi-magnify" variant="outlined" hide-details single-line></v-text-field>
          </template>
          <v-data-table :headers="headers" :items="list_encours" @click:row="onRowClick"  v-model="selectedItems"  item-value="Numero_pret" :search="search" fixed-header height="400px" item-key="id"  ></v-data-table>
        </v-card>

      <!-- Dialogue qui sera contrôlé par la fonction -->
      <v-dialog v-model="dialog" width="auto">
        <v-card style=" padding: 10px 20px;">
          <v-card-title style=" font-size: 12px;">{{ dialogTitle }}</v-card-title>
          <v-col width="1000px">
            {{ dialogContent.label }}
            <v-row class=" mt-10">
              <v-img
              @click="viewimg=true"
                v-for="item in dialogContent.image" :key="item"
                :src="'../../../API/uploads_files/declarations_files/'+item.img"
                class="align-end mx-2"
                gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
                height="100px"
                width="170px"
                cover
              >
                <span class="text-white text-sm pl-3">
                  {{item.label}}
                </span>
              </v-img>

            </v-row>
            </v-col>
          <v-card-actions>
            <div class=""   style=" display: flex; flex-direction: row; align-items: center;">
              <v-btn @click="extract_item()" color="red" variant="flat" class="ml-2">
                <v-icon start>mdi-folder-zip</v-icon>
                Fichier Zip
              </v-btn>
              <v-btn @click="closeDialog"  color="green" variant="flat" class="ml-2">Fermer</v-btn>

            </div>
          </v-card-actions>
        </v-card>
      </v-dialog>

    <!-- Dialogue qui sera contrôlé par la fonction -->
      <v-dialog v-model="dialog_a_traiter" width="850px">
        <v-card style=" padding: 10px 20px;">
          <v-card-title style=" font-size: 12px;">Formulaire des déclarations</v-card-title>
          <v-card-text>
            <v-form>
              <v-container>
            <v-row dense>
              <v-col
                v-for="(value, key) in dialogData"
                :key="key"
                cols="12"
                sm="6"
                md="4"
              >

                <!-- File input fields for PJ references and fillers -->
                <v-file-input
                    v-if="key === 'PJ AR' || key === 'PJ CNP' || key === 'PJ ANR'"
                    :label="key"
                    v-model="dialogData[key]"
                    variant="outlined"
                    class="green-border no-prepend-icon"
                    accept="application/pdf,image/*"
                    prepend-inner-icon="mdi-paperclip"
                  />
                <v-text-field
                  v-else-if="key === 'Date de création'"
                  v-model="dialogData[key]"
                  :label="key"
                  type="date"
                  dense
                  :max="today"
                  variant="outlined"
                />
              <v-text-field
                  v-else
                  :label="key"
                  v-model="dialogData[key]"
                  dense
                  variant="outlined"
                  style="opacity: .8;"
                />

                <v-text-field
                  v-else
                  :label="key"
                  v-model="dialogData[key]"
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
            <div class=""   style=" display: flex; flex-direction: row; align-items: center;">
              <v-btn @click="Create_It"   :disabled="!is_full" :color="is_full ? 'red' : 'gray'"  variant="flat" class="ml-2">Enregistrer ?</v-btn>
              <v-btn @click="closeDialog" color="green" variant="flat" class="ml-2">Non</v-btn>
              </div>
          </v-card-actions>
        </v-card>
      </v-dialog>


      <v-dialog v-model="viewimg" width="620px">
        <v-card class="  " flat style=" width: 40vw; display: flex; justify-content: center; align-items: center;" >
          <v-window v-model="window" show-arrows   style=" width: 100%; height: 100%;" >
          <v-window-item   v-for="item,i in dialogContent.image" :key="item"  style=" width: 100%; height: 100%;">

            <v-img
                :src="'../../../API/uploads_files/declarations_files/'+item.img"
                class="align-end"
                gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
                height="100vh"
                width="40vw"
                cover
              >
              </v-img>
            </v-window-item>
          </v-window>
        </v-card>
      </v-dialog>


      </v-card>


</template>

<script setup>
import api from "@/api/axios";
import { ref } from "vue";
import { onMounted,watch } from "vue";
import { getAllData } from '@/api/indexDB';
import { usePopupStore } from '../../stores/store'

const search = ref('');

let is_full=ref(false)
const today = new Date().toISOString().split("T")[0];
const dialogData = ref({
  "Numéro de dossier": "",
  "Date de création": "",
  "Champ vide 1": "",
  "PJ AR": "",
  "PJ CNP": "",
  "PJ ANR": "",
  "Champ vide 2": "",
  "Champ vide 3": "",
  "Champ vide 4": ""
});

const headers= [
  {
    align: 'start',
    key: 'Numero_pret',
    sortable: false,
  },
{ key: 'numero_dossier', title: 'numero_dossier' },
{ key: 'date_creation', title: 'date_creation' },
{ key: 'filler1', title: 'filler1' },
{ key: 'pj_ar', title: 'pj_ar' },
{ key: 'pj_cnp', title: 'pj_cnp' },
{ key: 'pj_anr', title: 'pj_anr' },
{ key: 'filler2', title: 'filler2' },
{ key: 'filler3', title: 'filler3' },
{ key: 'filler4', title: 'filler4' },
{ key: 'Date_enreg', title: 'Date_enreg' },

]

const header_model=[
{ key: 'numero_dossier', title: 'numero dossier' },
{ key: 'date_creation', title: 'date creation' },
{ key: 'filler1', title: 'filler1' },
{ key: 'pj_ar', title: 'pj ar' },
{ key: 'pj_cnp', title: 'pj cnp' },
{ key: 'pj_anr', title: 'pj anr' },
{ key: 'filler2', title: 'filler2' },
{ key: 'filler3', title: 'filler3' },
{ key: 'filler4', title: 'filler4' },

]
const data_model=ref({
  numero_dossier: "",
    date_creation:  "",
    filler1: "",
    filler2: "",
    filler3: "",
    filler4: "",
    pj_ar: "",
    pj_cnp:  "",
    pj_anr:  ""
})

const  list_encours=ref([])
const window= ref(0);
// Variables pour le dialogue
const dialog = ref(false);
const dialog_a_traiter = ref(false);
const dialogTitle = ref('');
const dialogContent = ref({
  label:'',
  image: []
});
const viewimg=ref(false)
const selectedItems = ref([]); // <- Ici on récupère les items sélectionnés
const selectedRow = ref(null);
const data_temp=ref([])


   // ✅ Réagit à toute modification de dialogData
watch(dialogData, () => {
    check_key_state();
}, { deep: true });


const get_encours = async (offset, limit) => {
  try {
    const response = await api.get(`/api/get_liste_declarement?offset=${offset}&limit=${limit}`);

    for (let index = 0; index < response.data.list_of_data.length; index++) {
      const element = response.data.list_of_data[index];
      data_temp.value.push (element);
      list_encours.value.push (element);
    }

  } catch (error) {
    console.error("❌ Erreur lors de la récupération des fichiers:", error);
  }
};
const checkEmptyFields = () => {
  const keysToCheck = [
  "Numéro de dossier",
  "Date de création",
  "PJ AR",
  "PJ CNP",
  "PJ ANR"
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

const extract_item = () => {
  setTimeout(() => {
    // 👉 Convertir l'objet en tableau si ce n'est pas déjà un tableau
    const dataToExport = Array.isArray(data_model.value)
      ? data_model.value
      : [data_model.value];  // enveloppe l'objet dans un tableau

    downloadTXTFromProxyData(dataToExport, header_model);
  }, 200);
};

// Classe de la ligne sélectionnée
const onRowClick = (event,item) => {
  const rowElement = event.target.closest('tr');

  selectedRow.value=item.item

  // Supprime la classe rouge de toutes les lignes (optionnel si tu veux une seule ligne en rouge)
  document.querySelectorAll('tr.red-row').forEach(row => {
    row.classList.remove('red-row');
  });

  // Ajoute la classe à la ligne cliquée
  if (rowElement) {
    rowElement.classList.add('red-row');
  }

  openDialog('Propriété',item.item)
};

// Fonction pour ouvrir le dialogue avec des paramètres personnalisés
const openDialog = (title , content) => {
  dialogContent.value.image=[]
  dialogTitle.value = title;

  dialogContent.value.label = 'N° de Dossier: '+content.numero_dossier;
  dialogContent.value.label = 'N° de Dossier: '+content.numero_dossier;
  dialogContent.value.image.push({img:content.pj_anr,label:'PJ ANR'});
  dialogContent.value.image.push({img:content.pj_ar,label:'PJ AR'});
  dialogContent.value.image.push({img:content.pj_cnp,label:'PJ CNP'});

  data_model.value={
    numero_dossier: content.numero_dossier,
    date_creation:  convertirDateFr(content.date_creation),
    filler1: content.filler1,
    filler2: content.filler2,
    filler3: content.filler3,
    filler4: content.filler4,
    pj_ar: content.pj_ar,
    pj_cnp:  content.pj_cnp,
    pj_anr:  content.pj_anr
  }

  console.log(data_model.value) ;

  dialog.value = true;


};
function convertirDateFr(dateStr) {
  if (!dateStr) return "";

  const [annee, mois, jour] = dateStr.split("-");
  return `${jour}/${mois}/${annee};`;
}
const closeDialog = () => {
  dialog.value = false;
  dialog_a_traiter.value = false;
};

const Create_It = async () => {
  // create_gpp_()
  closeDialog()
  setTimeout(() => {
    usePopupStore().show_notification.status=true
    usePopupStore().show_notification.message="Le donnée enregisté"
    usePopupStore().show_notification.ico='mdi mdi-check'
  }, 400);

  let row_to_send={
  "numero_dossier":dialogData.value["Numéro de dossier"],
  "date_creation":dialogData.value["Date de création"],
  "filler1":dialogData.value["Champ vide 1"],
  "filler2":dialogData.value["Champ vide 2"],
  "filler3":dialogData.value["Champ vide 3"],
  "filler4":dialogData.value["Champ vide 4"]
  }

  // 2. Récupère les fichiers (de type File)
let files = {
    "PJ_AR": dialogData.value["PJ AR"], // fichier
    "PJ_CNP": dialogData.value["PJ CNP"], // fichier
    "PJ_ANR": dialogData.value["PJ ANR"] // fichier
  };

  send_selected_credit(row_to_send,files)


};

const check_key_state =()=>{

  is_full.value= checkEmptyFields();
}

const send_selected_credit = async (data, files) => {

  try {
    let formData = new FormData();
    // Ajouter les données (en JSON string)
    formData.append("row_data", JSON.stringify(data));

    // Ajouter les fichiers (seulement s’ils existent)
    if (files.PJ_AR) formData.append("pj_ar", files.PJ_AR);
    if (files.PJ_CNP) formData.append("pj_cnp", files.PJ_CNP);
    if (files.PJ_ANR) formData.append("pj_anr", files.PJ_ANR);
    await api.post('/api/insert_declaration', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  } catch (error) {
    console.error("❌ Erreur lors de l'envoi du crédit sélectionné :", error);
  }
};
const loadAllEncours = async () => {
  const step = 100;
  for (let offset = 0; offset < 10; offset += step) {
    await get_encours(offset, step);
  }

  // await get_list_a_traiter();
};


const onRowClick_atraiter_=()=>{

  dialog_a_traiter.value = true;

};

onMounted(async ()=>{
  loadAllEncours();
  // get_list_a_traiter()
  const allData = await getAllData();
  list_encours.value = allData;
})
async function downloadTXTFromProxyData(proxyData, headers) {
  if (!proxyData || !headers || headers.length === 0) {
    console.warn("Aucune donnée à exporter.");
    return;
  }

  const dataArray = Array.isArray(proxyData) ? proxyData : [proxyData];

  // Génération uniquement des lignes, sans les titres
  const txtRows = dataArray.map(row =>
    headers.map(h => (row[h.key] ?? "")).join(";")
  );

  const txtContent = txtRows.join("\n");
  const blob = new Blob([txtContent], { type: "text/plain;charset=utf-8;" });

  // Générer un nom de fichier avec la date formatée
  const now = new Date();
  const formattedDate = now.toLocaleString("fr-FR", {
    day: "2-digit", month: "2-digit", year: "numeric",
    hour: "2-digit", minute: "2-digit", second: "2-digit"
  }).replace(/\D/g, ''); // Remplacer tout caractère non numérique
  const filename = `00132530-CNP-CH-00015-00001-2024-${formattedDate}.txt`;

  const formData = new FormData();
  formData.append("file", blob, filename);

  // Ajouter les autres objets à formData
  formData.append("pj_anr", dataArray[0].pj_anr);  // Ajouter le champ pj_anr
  formData.append("pj_ar", dataArray[0].pj_ar);    // Ajouter le champ pj_ar
  formData.append("pj_cnp", dataArray[0].pj_cnp);

  try {
    // Envoi du fichier au serveur pour compression
    const response = await api.post('/api/upload-and-compress', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      responseType: 'blob',  // Important : Spécifie que la réponse attendue est un blob
    });

    // Si la réponse est un fichier, on le télécharge
    const zipBlob = response.data;

    // Créer un lien pour télécharger le fichier compressé
    const url = URL.createObjectURL(zipBlob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `RGPP_${formattedDate}.zip`;
    a.click();

    // Libérer l'URL après téléchargement
    URL.revokeObjectURL(url);
  } catch (err) {
    console.error("Erreur upload + compression :", err);
  }
}






</script>

<style scoped>
tbody{
  color: gray;
}
.red-row {
  background-color: rgba(0, 255, 17, 0.265) !important;
  color: white; /* optionnel pour meilleure visibilité */
}
.customize_btn {
  position: absolute;
  top: 50px;
  right: 25px;
  z-index: 10;
  background: green ;
  padding: 4px 10px;
  border-radius: 20px;
}

  </style>
