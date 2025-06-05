<template>
  <div class="container_cdi">
    <v-card width="700px" height="400px" style="display: flex; flex-direction: column;" id="v-card">
      <v-card-title>CHARGEMENT DES DONNÉES</v-card-title>
      <v-row style="margin-top: 10px; height: 100%; padding-left: 20px;">
        <div  style="height: 80%; display: flex; align-items: center;">
          <v-progress-circular :model-value="usePopupStore().precentage" :rotate="180" :size="150" :width="15" color="pink">
            <span v-if="usePopupStore().precentage!=0">{{ usePopupStore().precentage }}</span>
            <span v-else> Chargement ...</span>
          </v-progress-circular>
        </div>
        <v-col>
          <div class="" style=" padding-right: 30px; ;">
            <div v-for="item,i in usePopupStore().cdi_list_stream" :key="i" style="   padding: 5px; display:  flex;   place-items: center;">
              <v-progress-circular v-if="usePopupStore().cdi_list_file_stream[i] && !usePopupStore().cdi_list_file_stream[i].success" :size="15" :width="5" color="green" indeterminate ></v-progress-circular>
              <span v-else-if="usePopupStore().cdi_list_file_stream[i] && usePopupStore().cdi_list_file_stream[i].success" style="padding: 15px; color: #53e053; font-size: 18px;" class="mdi mdi-check-circle" ></span>
              <v-progress-circular v-else  :size="15" :width="5" color="green"  ></v-progress-circular>
              <div v-if="usePopupStore().cdi_list_file_stream[i]"  style=" display: flex; flex-direction: column;">
                <span style=" font-size: 14px; color: white; ">{{item.title}}</span>
                <div style=" display: flex;">

                <span style=" font-size: 10px; color: gray; ">{{ usePopupStore().cdi_list_file_stream[i].task}}</span>
                <span style=" font-size: 10px; color: gray;margin-left: 10px; ">{{ usePopupStore().cdi_list_file_stream[i].row_count}}</span>
                <span v-if="usePopupStore().cdi_list_file_stream[i].total" style=" font-size: 10px; color: gray;margin-left: 10px; ">{{'/'+ usePopupStore().cdi_list_file_stream[i].total}}</span>
                </div>
              </div>
              <div v-else style=" display: flex; flex-direction: column;">
                <span  style=" font-size: 14px; color: gray; ">{{item.title}}</span>
                <span style=" font-size: 10px; color: gray; ">En attente ...</span>
              </div>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { usePopupStore } from '../../stores/store'

const interval = ref(null)
const value = ref(0)

onMounted(() => {
  interval.value = setInterval(() => {
    value.value = value.value === 100 ? 0 : value.value + 10
  }, 1000)
  console.log(usePopupStore().cdi_list_stream);

  console.log(usePopupStore().cdi_list_file_name_stream);


})

onBeforeUnmount(() => {
  if (interval.value) clearInterval(interval.value)
})
</script>

<style scoped>
.container_cdi {
  background-color: rgba(0, 0, 0, 0.5);
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1000;
  width: 100vw;
  height: 100vh;
  display: flex;
  place-items: center;
  justify-content: center;
}

.v-progress-circular {
  margin: 1rem;
}
</style>
