<!-- src/pages/home.vue or src/components/home.vue -->
<template>
  <div>
    <h1>Historique de Déclarations</h1>
    <!-- Your home page content -->
    <v-card class="mx-auto">
  <v-list v-model:opened="open">
    <v-list-group
    v-for="(group, i) in [...list_final].reverse()"
      :key="i"
      :value="group.group"
    >

    <template v-slot:activator="{ props, isOpen }">
      <v-hover v-slot="{ isHovering, props: hoverProps }">
        <v-list-item
          v-bind="{ ...props, ...hoverProps }"
          prepend-icon="mdi-folder"
          :title="cut_string(group.label)"
        >
          <template #append>
            <!-- Icône de téléchargement visible au hover -->
            <v-icon @click="download(group.children,group.label)" v-if="isHovering" icon="mdi-arrow-down-bold-circle-outline" style=" color: #00E000;" class="mr-2" />

            <!-- Icône chevron dynamique -->
            <v-icon
              :icon="isOpen ? 'mdi-chevron-up' : 'mdi-chevron-down'"
              class="transition-transform"
              :class="isOpen ? 'rotate-180' : ''"
            />
          </template>
        </v-list-item>
      </v-hover>
    </template>



      <v-list-item>
        <table class="w-full text-sm border-collapse">
          <thead class="bg-gray-100">
            <tr>
              <th class="text-left px-4 py-2 border-b">Id</th>
              <th class="text-left px-4 py-2 border-b">Agence</th>
              <th class="text-left px-4 py-2 border-b">Compte</th>
              <th class="text-left px-4 py-2 border-b">Datech</th>
              <th class="text-left px-4 py-2 border-b">Datouv</th>
              <th class="text-left px-4 py-2 border-b">Nom et prénom</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(item, j) in group.children"
              :key="j"
              class="hover:bg-gray-50"
            >
              <td class="px-4 py-2 border-b">{{ item.Id }}</td>
              <td class="px-4 py-2 border-b">{{ item.Agence }}</td>
              <td class="px-4 py-2 border-b">{{ item.Compte }}</td>
              <td class="px-4 py-2 border-b">{{ item.Datech }}</td>
              <td class="px-4 py-2 border-b">{{ item.Datouv }}</td>
              <td class="px-4 py-2 border-b">{{ item.Nom }}</td>
            </tr>
          </tbody>
        </table>
      </v-list-item>
    </v-list-group>
  </v-list>
      <!-- Dialogue qui sera contrôlé par la fonction -->
      <v-dialog v-model="dialog_a_traiter" width="auto">
        <v-card style=" padding: 10px 20px;">
          <v-card-title style=" font-size: 12px;">Confirmation</v-card-title>
          <v-card-text>
            {{ dialogTitle }}
          </v-card-text>
          <v-card-actions>
            <div class=""   style=" display: flex; flex-direction: row; align-items: center;">
              <button @click="downloadCSVFromProxyData()" size="24" title="Annuler" style=" color: red  ; padding: 0px 7px; margin-left: 10px; border-radius: 25px;">Oui </button>
              <button @click="closeDialog" size="16" title="Charger le fichier" style=" background: green; padding: 0px 14px; margin-left: 10px; border-radius: 25px;">Non </button>
            </div>
          </v-card-actions>
        </v-card>
      </v-dialog>
</v-card>


  </div>
</template>

<script setup>

import api from "@/api/axios";
import { onMounted } from "vue";
import { ref } from "vue";
// Home component logic
const open = ref(['Users'])
// const  admins=ref( [
//     ['Management', 'mdi-account-multiple-outline'],
//     ['Settings', 'mdi-cog-outline']
// ])

const dialogTitle = ref('');
const dialog = ref(false);
const dialog_a_traiter = ref(false);
const list_donne=ref([])
const list_final=ref([])
const selectedItems=ref([]);
const header_model=[  { key: "Id", title: "Id" },
  { key: "Agence", title: "Agence" },
  { key: "Agec", title: "Agec" },
  { key: "Compte", title: "Compte" },
  { key: "Nom", title: "Nom" },
  { key: "Classt", title: "Classt" },
  { key: "Codape", title: "Codape" },
  { key: "Mntcaht", title: "Mntcaht" },
  { key: "Cli_n_a", title: "Cli_n_a" },
  { key: "Nature", title: "Nature" },
  { key: "Typecredit", title: "Typecredit" },
  { key: "Montant", title: "Montant" },
  { key: "Datech", title: "Datech" },
  { key: "Rang", title: "Rang" },
  { key: "Taux", title: "Taux" },
  { key: "Datouv", title: "Datouv" },
  { key: "Genre", title: "Genre" },
  { key: "Date_enreg", title: "Date_enreg" }
]

const openDialog = (title ) => {
  dialogTitle.value = title;
  dialog.value = true;
};

const closeDialog = () => {
  dialog.value = false;
  dialog_a_traiter.value = false;
};
const get_list_a_traiter = async ( ) => {
  try {

    // Sinon on fait l'appel à l’API
    const response = await api.get(`/api/get_liste_faites`);

    list_donne.value = response.data.list_of_data;
    list_donne.value = list_donne.value.map(item => {
      // Créer une copie de l'objet pour ne pas modifier l'original
        const newItem = { ...item };
        // Formater Datech si elle existe
        if (newItem.Datech) {
          const date = new Date(newItem.Datech);
          newItem.Datech = date.getDate().toString().padStart(2, '0') + '.' +
                              (date.getMonth() + 1).toString().padStart(2, '0') + '.' +
                              date.getFullYear();
        }
        // Formater Datouv si elle existe
        if (newItem.Datouv) {
          const date = new Date(newItem.Datouv);
          newItem.Datouv = date.getDate().toString().padStart(2, '0') + '.' +
                          (date.getMonth() + 1).toString().padStart(2, '0') + '.' +
                          date.getFullYear();
        }

        return newItem;
      });

      list_final.value = groupArray(list_donne.value)
      console.log(list_final.value);

    // console.log('📡 Données récupérées depuis API et stockées localement',list_donne.value);
  } catch (error) {
    console.error("❌ Erreur lors de la récupération des fichiers:", error);
  }
};

const groupArray = (data) => {
  const groupedMap = {}

  // Grouper les objets selon la valeur de 'group_of'
  for (const item of data) {
    const group = item.Group_of
    if (!groupedMap[group]) {
      groupedMap[group] = []
    }
    groupedMap[group].push(item)
  }

  // Construire la liste finale avec la structure demandée
  const result = Object.entries(groupedMap).map(([group, children]) => ({
    group: group,
    label: children[0].Creating_date,
    children: children
  }))

  return result
}

const cut_string = (string) => {
  // if (string.length > 20) {
    return string.substring(0, string.length -3) ;

}
const download = (data,title) => {
  openDialog("Télécharger le GPP pour:  "+ title)
  selectedItems.value=data
  dialog_a_traiter.value = true;
  // downloadCSVFromProxyData(data,header_model);
}


function downloadCSVFromProxyData() {
  closeDialog();
  const dataArray = Array.from(selectedItems.value);

  const csvHeaders = header_model.map(h => h.title).join(";");
  const csvRows = dataArray.map(row =>
  header_model.map(h => `"${(row[h.key] ?? "").toString().replace(/"/g, '""')}"`).join(";")
  );

  const csvContent = [csvHeaders, ...csvRows].join("\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");

  // 👉 Générer la date et l'heure au format voulu
  const now = new Date();
  const day = String(now.getDate()).padStart(2, '0');
  const month = String(now.getMonth() + 1).padStart(2, '0'); // janvier = 0
  const year = now.getFullYear();
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');

  const formattedDate = `${day}${month}${year}${hours}${minutes}${seconds}`;

  // 👉 Utiliser cette date comme nom de fichier
  link.href = URL.createObjectURL(blob);
  link.setAttribute("download", `RGPP_${formattedDate}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}


onMounted(()=>{
  get_list_a_traiter();
  // Regrouper les objets par leur valeur group_of

})
</script>
