<template>
<v-app>
    <notification v-if="popupStore.showPopup" id="not_content"></notification>
    <v-navigation-drawer v-if="token && app" v-model="drawer" :rail="rail" permanent @click="rail = false" style=" z-index: 1">
        <v-list-item prepend-avatar="./assets/logo.png" title="GPP App" nav>
            <template v-slot:append>
                <v-btn icon="mdi-chevron-left" variant="text" @click.stop="rail = !rail"></v-btn>
            </template>
        </v-list-item>
        <v-divider></v-divider>

        <v-list density="compact" nav style=" margin-top: 50px;">
            <div v-for="item,i in listItems">
                <v-list-item :key="i" v-if="item.type==app || item.type=='all'" :prepend-icon="item.icon" :title="item.title" :value="item.value" :to="item.to" @click="item.to==''?logout():''"></v-list-item>
            </div>
        </v-list>
    </v-navigation-drawer>

    <v-main>
        <router-view style=" padding: 40px 20px;" />
    </v-main>
</v-app>
</template>

<script setup>
import {
    ref,
    onBeforeMount
} from 'vue';
import router from './router/index';
import notification from './components/notification.vue';
import {
    usePopupStore
} from './stores/store'
import Cookies from 'js-cookie' // <--- Ajouté

const token = Cookies.get('auth_token')
const app = Cookies.get('app')
onBeforeMount(() => {
    const token = Cookies.get('auth_token')
    const app = Cookies.get('app')
    if (!token || !app) {
        router.replace('/login');

    }
})

// onMounted(() => {
//     // router.replace('/dec_credit');
// });

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
        icon: 'mdi-receipt-text-clock-outline',
        title: 'Encours',
        value: 'Encours',
        to: '/' + Cookies.get('app') + '/cdi_import_file',
        type: 'cdi'
    },
    {
        icon: 'mdi-account-circle-outline',
        title: 'Account',
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
