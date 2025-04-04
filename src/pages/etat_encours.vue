<template>
  <div id="upload-container">
    <v-card class="upload-box" outlined>
      <!-- Icône Upload -->
      <v-icon size="48" class="upload-icon">mdi-cloud-upload</v-icon>

      <!-- Texte principal -->
      <p class="upload-text">Drag and Drop Here</p>

      <!-- Texte secondaire -->
      <p class="upload-subtext">or choose locally</p>

      <!-- Bouton pour sélectionner un fichier -->
      <v-btn variant="outlined" class="upload-btn" @click="triggerFileInput">
        Local Filesystem
      </v-btn>

      <!-- Input caché pour l'upload -->
      <input type="file" ref="fileInput" class="hidden-file-input" @change="handleFileUpload">
    </v-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const fileInput = ref(null)

// Fonction pour ouvrir la boîte de dialogue de sélection de fichiers
const triggerFileInput = () => {
  fileInput.value.click()
}

// Fonction pour gérer l'upload (facultatif)
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    console.log('Fichier sélectionné :', file.name)
  }
}
</script>

<style scoped>
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
