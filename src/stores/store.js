// stores/usePopupStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePopupStore = defineStore('popup', () => {
  const showPopup = ref(false)
  const loadFile=ref(null);
  const show_notification=ref({status:false,message:"null",ico:"null"})

  const togglePopup = () => {
    showPopup.value = !showPopup.value
  }

  return { showPopup, togglePopup,loadFile,show_notification }
})
