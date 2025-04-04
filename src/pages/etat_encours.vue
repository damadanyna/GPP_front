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
      <v-btn variant="outlined" class="upload-btn" @click="triggerFileInput">
        Fichier Local du Système
      </v-btn>

      <!-- Input caché pour l'upload -->
      <input type="file" accept=".xlsx"  ref="fileInput" class="hidden-file-input" @change="handleFileUpload">
    </v-card>
    <v-dialog max-width="500">
      <template v-slot:activator="{ props: activatorProps }">
        <v-btn
        id="history"
          v-bind="activatorProps"
          icon=" mdi-history"
          variant="flat"
        ></v-btn>
      </template>

      <template v-slot:default="{ isActive }">
        <v-card title="Liste récente">
          <div style=" max-height: 400px;overflow-y: auto; ">
            <div v-for="item,i in list_file" :key="i" style="   display: flex; justify-content: center; width: 100%; ">
              <div class="" style=" width: 300px;">
                <div v-if=" item.used==true" style="color: green; border: 1px solid green; padding: 2px 10px; border-radius: 10px;margin: 2px;">
                  <span>{{ item.label }}</span>
                  <v-icon size="20"> mdi-check</v-icon>
                </div>
                <div v-else style=" padding: 2px 10px; cursor: pointer; margin: 2px;">
                  <span>{{ item.label }}</span>
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

const fileInput = ref(null)

// Fonction pour ouvrir la boîte de dialogue de sélection de fichiers
const triggerFileInput = () => {
  fileInput.value.click()
}
const list_file=ref([
  {
  label:"Etat des encours 2025-03-16",
  used:false
  },{
  label:"Etat des encours 2025-03-20",
  used:true
  },{
  label:"Etat des encours 2025-03-23",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },{
  label:"Etat des encours 2025-03-27",
  used:false
  },
])

// Fonction pour gérer l'upload (facultatif)
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    console.log('Fichier sélectionné :', file.name)
  }
}
</script>



<style scoped>
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
