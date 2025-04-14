<template>
  <div id="upload-container">
    <v-card class="upload-box" outlined>
      <!-- Icône Upload -->
      <v-icon size="48" class="upload-icon">mdi-cloud-upload</v-icon>

      <!-- Texte principal -->
      <p class="upload-text">Glissez le fihcer ici</p>

      <!-- Texte secondaire -->
      <p class="upload-subtext">ou choisissez localement</p>

      <!-- Bouton pour sélectionner un fichier -->
     <div class="" style=" display: flex; flex-direction: row; align-items: center;">
      <v-btn variant="outlined" class="upload-btn " @click="triggerFileInput" id="file_name" >
        {{ file_name }}
      </v-btn>
      <div class="" v-if="is_exist_file==true" style=" display: flex; flex-direction: row; align-items: center;">
        <v-icon @click="cancel" size="24" title="Annuler" style=" color: red  ; padding: 20px; margin-left: 10px; border-radius: 25px;">mdi-file-remove-outline </v-icon>
        <v-icon @click="uploadFile" size="16" title="Charger le fichier" style=" background: green; padding: 12px; margin-left: 10px; border-radius: 25px;"> mdi-check </v-icon>

      </div>
    </div>

      <!-- Input caché pour l'upload -->
      <input type="file" accept=".xlsx"  ref="fileInput" class="hidden-file-input" @change="handleFileUpload">
    </v-card>
    <v-dialog max-width="500">
      <template v-slot:activator="{ props: activatorProps }">
        <v-btn
        @click="showFiles"
        id="history"
          v-bind="activatorProps"
          icon=" mdi-history"
          variant="flat"
        ></v-btn>
      </template>

      <template v-slot:default="{ isActive }">
        <v-card title="Liste récente">
          <div style=" max-height: 400px;overflow-y: auto; " @click=" isActive.value = false">
            <div v-for="item,i in list_file" :key="i" @click="show_popup(item.file_name)" style=" display: flex; justify-content: center; width: 100%; font-size: 12px; ">
              <div class="" style=" width: 300px;">
                <div v-if=" item.used==true" style="color: green; border: 1px solid green; padding: 2px 10px; border-radius: 10px;margin: 2px;">
                  <span>{{resize_text( item.file_name,40) }}</span>
                  <v-icon size="20"> mdi-check</v-icon>
                </div>
                <div v-else style=" padding: 2px 10px; cursor: pointer; margin: 2px;">
                  <span>{{resize_text( item.file_name,40) }}</span>
                </div>
              </div>
            </div>
           </div>

          <v-card-actions>
            <v-spacer></v-spacer>

            <v-btn
              text="Fermer"
              @click="isActive.value = false"
            ></v-btn>
          </v-card-actions>
        </v-card>
      </template>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api/axios'
import { usePopupStore } from '../stores/store'

const fileInput = ref(null)
const files_data = ref(null)
const is_exist_file=ref(false)

// Fonction pour ouvrir la boîte de dialogue de sélection de fichiers
const triggerFileInput = () => {
  fileInput.value.click()
}
const list_file=ref([])

// Créer une variable réactive pour stocker le nom du fichier
const file_name = ref("Fichier Local du Système");
// Fonction pour gérer l'upload (facultatif)
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  const elt_=document.getElementById('file_name')

  if (file) {
    console.log('Fichier sélectionné :', file.name)
    files_data.value = event.target.files[0];

    file_name.value= file.name
    elt_.classList.add('file_loaded')
    is_exist_file.value=true
  }

}
const cancel=()=>{
  file_name.value= "Fichier Local du Système"
  const elt_=document.getElementById('file_name')
  // fileInput.value=null
  is_exist_file.value=false
  elt_.classList.remove('file_loaded')
  const files_data = document.querySelector('input[type="file"]');
  files_data.value = null;
  // console.log(files_data.value);
}
const resize_text = (text, size) => {
  if (typeof text !== 'string' || text === null) {
    return ''; // Si 'text' n'est pas une chaîne ou est null, on retourne une chaîne vide
  }

  if (text.length > size) {
    return text.substring(0, size - 3) + '...';
  }

  return text;
};

const uploadFile = () => {
  // console.log(files_data.value);

  const formData = new FormData();
  formData.append('file', files_data.value);

  api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  .then((response) => {
    console.log(response.data);

  })
  .catch((error) => {
    console.error(error);
  });
};


// Méthode pour afficher les fichiers
const showFiles = async () => {
  try {
    const response = await api.get('/api/show_files');
    console.log(response.data.files);
    list_file.value=response.data.files// Affichage des fichiers reçus
  } catch (error) {
    console.error("Erreur lors de la récupération des fichiers:", error); // Gestion des erreurs
  }
};

const show_popup=(file_name)=>{
  usePopupStore().togglePopup()
  console.log(usePopupStore().showPopup,file_name);
  usePopupStore().loadFile=file_name

}



</script>



<style scoped>
.file_loaded{
  background: green;
  color: white;
}
#list_{
  margin:71px 0px;
}
#separateur{
  height: 1px;
  margin-top: 20px;
  margin-bottom: 12px;
  background: gray;
}
#modal-content{
  display: flex;
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  backdrop-filter: blur(4px);
  background: rgba(0, 0, 0, 0.257);
  align-items: center;
  justify-content: center;
  z-index: 100;
}
#modal-list{
  display: flex;
  flex-direction: column;
  background: wheat;
  color: black ;
  padding: 10px 20px;
  border-radius: 5px;

}
#title{
  font-size: 19px;
  font-weight: bold;
  color: rgb(49, 49, 49);
}
#history{
  position: absolute;
  bottom: 80px;
  right: 80px;
  font-size: 20px;
}
#history:hover{
  cursor: pointer;
  color: white;
}
/* Conteneur principal centré */
#upload-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #222; /* Fond sombre */
}

/* Boîte d'upload */
.upload-box {
  width: 500px;
  height: 250px;
  background: #1e1e1e;
  border: 2px dashed #666;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  text-align: center;
  padding: 20px;
}

/* Icône Upload */
.upload-icon {
  color: #ccc;
  margin-bottom: 10px;
}

/* Texte principal */
.upload-text {
  font-size: 20px;
  font-weight: bold;
  margin: 0;
}

/* Texte secondaire */
.upload-subtext {
  font-size: 14px;
  color: #bbb;
  margin: 10px 0;
}

/* Bouton pour choisir un fichier */
.upload-btn {
  border-color: #fff;
  color: #fff;
}

/* Cacher l'input file */
.hidden-file-input {
  display: none;
}
</style>
