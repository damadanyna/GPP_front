/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com
 */

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Composables
import { createVuetify } from 'vuetify'

export default createVuetify({
  theme: {
    defaultTheme: 'dark', // tu peux le changer en 'light' si besoin
    themes: {
      light: {
        dark: false,
        colors: {
          background: '#FFFFFF',
          background_box: '#FAFAFA',
          surface: '#FFFFFF',
          primary: '#222222',
          secondary: '#22DD33',
          accent: '#82B1FF',
          darkGray: '#DDDDDD',
          icon: '#222222',
          error: '#FF5252',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FB8C00',
        },
      },
      dark: {
        dark: true,
        colors: {
          background_box: '#1E1E1E',
          background: '#121212',
          surface: '#1E1E1E',
          secondary: '#55DD66',
          primary: '#FFFFFF',
          icon: '#FFFFFF',
          accent: '#FF4081',
          darkGray: '#82B1FF',
          error: '#FF5252',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FB8C00',
        },
      },
    },
  },
})
