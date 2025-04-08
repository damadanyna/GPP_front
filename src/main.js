 import { registerPlugins } from '@/plugins'
import './index.css';
import { createPinia } from 'pinia'
import App from './App.vue'


// Composables
import { createApp } from 'vue'

// Initialize Pinia
const pinia = createPinia()
const app = createApp(App)

registerPlugins(app)

app.use(pinia)
app.mount('#app')
