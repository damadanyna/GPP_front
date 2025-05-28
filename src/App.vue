<template>
<v-app >

    <notification v-if="popupStore.showPopup" id="not_content"></notification>
    <v-navigation-drawer  v-if="token && app" v-model="drawer" :rail="rail" permanent @click="rail = false" style=" z-index: 1">
        <v-list-item prepend-avatar="./assets/logo.png" title="SIPEM App"  nav>
            <template v-slot:append>
                <v-btn icon="mdi-chevron-left" variant="text" @click.stop="rail = !rail"></v-btn>

          <v-btn icon="mdi-theme-light-dark" @click="toggleTheme" variant="text" />
            </template>
        </v-list-item>
        <v-divider></v-divider>

        <v-list density="compact" nav style=" margin-top: 50px;">
            <div v-for="item,i in listItems">
                <v-list-item :key="i" v-if="item.type==app || item.type=='all'" :prepend-icon="item.icon" :title="item.title" :value="item.value" :to="item.to" @click="item.to==''?logout():''"></v-list-item>
            </div>

        </v-list>
    </v-navigation-drawer>

    <v-main >
        <router-view style=" padding: 40px 20px;" />
    </v-main>
</v-app>
</template>

<script setup>
import { useTheme } from 'vuetify'

const theme = useTheme()
const toggleTheme = () => {
  theme.global.name.value = theme.global.name.value === 'light' ? 'dark' : 'light'
}
import api from '@/api/axios'
import {
    ref,
    onBeforeMount,
    onMounted
} from 'vue';
import router from './router/index';
import notification from './components/notification.vue';
import {
    usePopupStore
} from './stores/store'
import Cookies from 'js-cookie' // <--- Ajouté

const token = Cookies.get('auth_token')
const app = Cookies.get('app')


const int_compense = async () => {
  try {
    // Sinon on fait l'appel à l’API
    const response = await api.get(`/api/int_compense`);
    console.log(response);
  } catch (error) {
    console.error("❌ Erreur lors de la récupération des fichiers:", error);
  }
};


onBeforeMount(() => {
    const token = Cookies.get('auth_token')
    const app = Cookies.get('app')
    if (!token || !app) {
        router.replace('/login');

    }
})


onMounted(() => {
  if (Cookies.get('app') == 'reportico') {
    // console.log("intialisation reportico");
    // int_compense()
  }

});

const drawer = ref(true);
const rail = ref(true);
const popupStore = usePopupStore()
// const show_popup = popupStore.showPopup
// const show_popup=ref();

const listItems = ref([{
        icon: 'mdi-cash-plus',
        title: 'Déclarations des Crédits',
        value: 'Declaration_credit',
        to: '/' + Cookies.get('app') + '/dec_credit',
        type: 'gpp'
    },
    {
        icon: 'mdi-cash-fast',
        title: 'Historique de Déclarations',
        value: 'Declaration_encours',
        to: '/' + Cookies.get('app') + '/dec_encours',
        type: 'gpp'
    },
    {
        icon: 'mdi-receipt-text-clock-outline',
        title: 'Encours',
        value: 'Encours',
        to: '/' + Cookies.get('app') + '/etat_encours',
        type: 'gpp'
    },
    {
        icon: ' mdi-clipboard-list-outline',
        title: 'Déclaration ANP',
      value: 'Déclaration ANP',
        to: '/' + Cookies.get('app') + '/list_cdi',
        type: 'cdi'
    },
    {
        icon: ' mdi-invoice-send-outline',
        title: 'Régularisation & non Reg',
        value: 'Régularisation & non Reg',
        to: '/' + Cookies.get('app') + '/cdi_declarement',
        type: 'cdi'
    },
    {
        icon: 'mdi-file-chart-outline',
        title: 'Importation Fichier',
        value: 'Importation Fichier',
        to: '/' + Cookies.get('app') + '/cdi_import_file',
        type: 'cdi'
    },
    {
        icon: 'mdi-file-table-box-multiple',
        title: 'Compensation',
        value: 'Compensation',
        to: '/' + Cookies.get('app') + '/compensation',
        type: 'reportico'
    },
    {
        icon: 'mdi-file-chart-outline',
        title: 'import fichier',
        value: 'Fichier',
        to: '/' + Cookies.get('app') + '/import_file',
        type: 'reportico'
    },
    {
        icon: 'mdi-account-circle-outline',
        title: 'Déconnecter',
        value: 'Utilisateur',
        to: '',
        type: 'all'
    },
])

const logout = () => {
    Cookies.remove('auth_token')
    window.location.reload(); // ou n'importe quelle route de redirection
}
</script>

<style>
#not_content {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 10;
    width: 100vw;
    height: 100vh;
    backdrop-filter: blur(3px);
    background: rgba(0, 0, 0, 0.329);
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>
