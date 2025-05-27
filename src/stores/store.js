// stores/usePopupStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePopupStore = defineStore('popup', () => {
  const showPopup = ref(false)
  const loadFile=ref(null);
  const list_a_traiter=ref([])
  const show_notification=ref({status:false,message:"null",ico:"null"})
  const user_access=ref([{
    name:"rgpp-onisoa",
    password:"123456",
    app:"gpp",
    url:'/gpp/dec_credit'
  },
  {
    name:"a",
    password:"a",
    app:"cdi",
    url:'/cdi/list_cdi'
  },
  {
    name:"d",
    password:"d",
    app:"reportico",
    url:'/reportico/compensation'
  },
])

  const togglePopup = () => {
    showPopup.value = !showPopup.value
  }

  return { showPopup, togglePopup,loadFile,show_notification,user_access,list_a_traiter}
})
