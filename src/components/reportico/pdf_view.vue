
<template>
  <v-card class="pa-4" max-width="950" style="font-size: 12px; border-radius: 10px;" ref="pdfContent" theme="light">
    <div style="display: flex; width: 100%; justify-content: center; font-size: 27px;">
      <span>RCP Chèques</span>
    </div>
    <v-table dense  theme="light">
      <thead>
        <tr>
          <th>ftid</th>
          <th>processdate</th>
          <th>recordtype</th>
          <th>chequenumber</th>
          <th>orderingrib</th>
          <th>beneficiaryrib</th>
          <th>solde</th>
          <th>anomailie</th>
          <th>ANO</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(value, key) in documentData" :key="key">
          <td  style="color: #555;">{{ value.ftid }}</td>
          <td  style="color: #555;">{{ value.processdate }}</td>
          <td  style="color: #555;">{{ value.recordtype }}</td>
          <td  style="color: #555;">{{ value.chequenumber }}</td>
          <td  style="color: #555;">{{ value.orderingrib }}</td>
          <td  style="color: #555;">{{ value.beneficiaryrib }}</td>
          <td  style="color: #555;">{{ value.solde }}</td>
          <td  style="color: #555;">{{ value.anomailie }}</td>
          <td  style="color: #555;">{{ value.ANO }}</td>
        </tr>
      </tbody>
    </v-table>
    <div>
      <span style="font-size: 17px;">Total : {{ total(documentData) }}</span>
      <span style="font-size: 17px ;margin-left: 30px;">Ligne : {{ documentData.length}}</span>
    </div>

    <v-btn color="green" @click="downloadPDF" class="mt-4" style=" font-weight: bolder;">
      Télécharger PDF
    </v-btn>
  </v-card>
</template>

<script setup>
import { defineProps } from 'vue'
import { ref } from 'vue'
import html2pdf from 'html2pdf.js'

const pdfContent = ref(null)
const props = defineProps({
  documentData: {
    type: Object,
    required: true
  }
})

const total= (list_encours)=>{
    var total=0
    for (let index = 0; index < list_encours.length; index++) {
        const soldeStr = list_encours[index].solde.replace(/,/g, '');
        total += parseFloat(soldeStr);
    }
    total=total+' MGA'
    return formatSolde(total)
}

const formatSolde=(val)=>{
      if (!val) return '0,00';
        // Nettoyage : supprime les virgules et transforme en nombre
        const montant = parseFloat(val.toString().replace(/,/g, ''));
        if (isNaN(montant)) return '0,00';

          // Format FR avec espace insécable fine (U+202F)
          let formatted = montant.toLocaleString('fr-FR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
          });

        // Remplacer les espaces fines insécables par deux espaces
        formatted = formatted.replace(/\u202F/g, '.');

      return formatted;
  }

const downloadPDF = async () => {
  const original = pdfContent.value?.$el || pdfContent.value
  if (!original) return

  const clone = original.cloneNode(true)
  clone.style.height = 'auto'
  clone.style.overflow = 'visible'
  clone.style.width = 'auto'

  // Zoom-out global
  clone.style.transform = 'scale(0.8)'
  clone.style.transformOrigin = 'top left'
  clone.style.width = '125%'

  // Supprimer le bouton
  const downloadBtn = clone.querySelector('.v-btn')
  if (downloadBtn) downloadBtn.remove()

  const table = clone.querySelector('table')
  if (table) {
    table.style.width = '100%'
    table.style.tableLayout = 'auto'
    table.style.fontSize = '10px'

    // Réduction de la colonne "anomailie" (8e colonne)
    const ths = table.querySelectorAll('th')
    if (ths[7]) {
      ths[7].style.width = '200px'
      ths[7].style.maxWidth = '200px'
      ths[7].style.wordBreak = 'break-word'
    }else if (ths[1] || ths[2] || ths[3]) {
        ths[8].style.width = '40px'
        ths[8].style.maxWidth = '40px'
        ths[8].style.wordBreak = 'break-word'
      }

    // Appliquer à chaque cellule correspondante
    const rows = table.querySelectorAll('tr')
    rows.forEach(row => {
      const cells = row.querySelectorAll('td')
      if (cells[7]) {
        cells[7].style.width = '200px'
        cells[7].style.maxWidth = '200px'
        cells[7].style.wordBreak = 'break-word'
      }else if (cells[1] || cells[2] || cells[3]) {
        cells[8].style.width = '40px'
        cells[8].style.maxWidth = '40px'
        cells[8].style.wordBreak = 'break-word'
      }
    })

    table.querySelectorAll('th, td').forEach(cell => {
      cell.style.padding = '4px'
    })
  }

  // Forcer affichage colonnes masquées
  clone.querySelectorAll('[style*="display: none"]').forEach(el => {
    el.style.display = 'table-cell'
  })

  const container = document.createElement('div')
  container.style.position = 'fixed'
  container.style.top = '-9999px'
  container.appendChild(clone)
  document.body.appendChild(container)

  await new Promise(resolve => setTimeout(resolve, 500))

  const options = {
    margin: 0.5,
    filename: 'RCP_Cheques.pdf',
    image: { type: 'jpeg', quality: 1 },
    html2canvas: { scale: 4 },
    jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }
  }

  await html2pdf().set(options).from(clone).save()
  document.body.removeChild(container)
}


// Exemple d’accès :
console.log('Document reçu :', props.documentData)
</script>

<style scoped>
@media print {
  .no-scroll {
    height: auto !important;
    overflow: visible !important;
  }
}

</style>

