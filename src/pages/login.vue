<template>
  <v-container fluid class="login-page">
    <v-row no-gutters>
      <!-- Illustration Section -->
      <v-col cols="12" md="6" class="left-section">
        <v-img src="@/assets/Login.png" class="illustration" cover></v-img>
      </v-col>

      <!-- Login Form Section -->
      <v-col cols="12" md="6" class="right-section d-flex align-center justify-center">
        <v-card class="login-card pa-8">
          <h2 class="text-center mb-4">Bonjour, Bienvenue!</h2>
          <p class="text-center text-subtitle-1 mb-6">Se connecter à votre compte</p>

          <v-form @submit.prevent="login">
            <v-text-field
              v-model="matricule"
              label="Code d'immatriculation"
              type="matricule"
              prepend-inner-icon="mdi-account-outline"
              class="mb-4"
              required
            />
            <v-text-field
              v-model="password"
              label="Mot de passe"
              type="password"
              prepend-inner-icon="mdi-lock-outline"
              class="mb-2"
              required
            />

            <div class="text-right mb-4">
              <a href="#" class="forgot-password">Mot de passe oublié?</a>
            </div>

            <v-btn type="submit" block class="mb-2 primary_green">Se Connecter</v-btn>
            <v-btn variant="outlined" block>S'INSCRIRE</v-btn>

            <div class="text-center mt-6">
              <p class="mb-2">Ou se connecter avec</p>
              <div class="social-icons d-flex justify-center">
                <v-icon class="mx-2" color="#3b5998">mdi-facebook</v-icon>
                <v-icon class="mx-2" color="#db4437">mdi-google</v-icon>
                <v-icon class="mx-2" color="#0077b5">mdi-linkedin</v-icon>
              </div>
            </div>
          </v-form>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import Cookies from 'js-cookie'
import { usePopupStore } from '../stores/store'

const matricule = ref('')
const password = ref('')

const login = () => {
  // usePopupStore().user_access.name
  // Simuler un appel d'API
  // console.log('Logging in with:', matricule.value, password.value)

  // console.log( usePopupStore().user_access.name);
  // console.log( usePopupStore().user_access.password);

  const users = usePopupStore().user_access


  for (const user of users) {
      if (matricule.value === user.name && password.value === user.password) {
        // Simuler la réception d'un token et le stockage dans les cookies
        Cookies.set('auth_token', 'token_123', { expires: 7 })
        // Lecture du token
        const token = Cookies.get('auth_token')
        console.log('Token lu depuis le cookie :', token)
        window.location.replace('/dashboard')
        return // pour sortir de la fonction après connexion
      }
    }

  // window.location.reload()


  // Redirection ou autre logique ici
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  place-items: center;
}

.left-section {
  display: flex;
  align-items: center;
  justify-content: center;
}

.illustration {
  width: 80%;
  max-width: 400px;
}

.login-card {
  width: 500px;
  box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.1);
  border-radius: 16px;
}

.forgot-password {
  font-size: 0.9rem;
  color: #a3ff9d;
  text-decoration: none;
}

.primary_green {
  background: #399e32;
  color: white;
}

.forgot-password:hover {
  text-decoration: underline;
}

.social-icons v-icon {
  font-size: 30px;
  cursor: pointer;
}
</style>
