<template>
  <div class=" bg-full-transp">
    <div >
      <div class=" popup-content">

        <v-icon size="18" style="margin-right: 7px;" class="upload-icon">{{usePopupStore().show_notification.ico }}</v-icon>
        {{ usePopupStore().show_notification.message }}

      </div>
    </div>
  </div>
</template>

<script setup>

import { onMounted } from 'vue';
import { usePopupStore } from '../stores/store'

onMounted(()=>{
  setTimeout(() => {
    usePopupStore().show_notification.status=false
  }, 1000);
})


</script >

<style>
.bg-full-transp{
 position: absolute;
 top: 0px;
 left: 0px;
 width: 100%;
 height: 100%;
 background: transparent;
 z-index: 100000000;
 justify-content: end;
 /* place-items: end; */
 display: flex;
 flex-direction: row;
 padding: 70px;
}
.popup-content{
  background: green;
  display: flex;
  padding: 10px 20px;
  border-radius: 10px;
  place-items: center;


  /* Animation ajoutée */
  animation: slideInFade 0.2s ease-out;
}
@keyframes slideInFade {
  0% {
    opacity: 0;
    transform: translateX(70px);
  }

  100% {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>
