<template>
  <v-app>
    <v-container color="blue">
    <p>  </p>
      <v-stepper vertical v-model="atStep">
        <v-stepper-step :complete="extensions.length>0" step="1">
          Choisir les extensions à utiliser
        </v-stepper-step>
        <v-stepper-content step="1">
          <v-card class="pa-4 ma-4">
            <v-form ref="form">
              <v-row>
                <v-col cols=6>
                  <p>Sélectionner les extensions au hasard si désiré: </p>
                </v-col>
                <v-col cols=2>
                  <v-text-field outlined dense :rules="rules" v-model.number="numRandom"></v-text-field>
                </v-col>
                <v-col>
                  <v-btn @click="getRandomExtensions">Go </v-btn>
                </v-col>
              </v-row>
            </v-form>
            <v-row>
              <v-col v-for="ext in extensionsList" :key="ext.name" cols="6" md="3" lg="3" xl="3">
                <v-checkbox v-model="extensions" :label="`${ext.name} (${ext.description})`" :value="ext.name" class="pa-0 ma-0"></v-checkbox>
              </v-col>
            </v-row>
          </v-card>
          <v-btn @click="atStep=2; cardsDistribution={}">
            Suivant
          </v-btn>
        </v-stepper-content>

        <v-stepper-step :complete="!!selection" step="2">
          Choisir la distribution des cartes
        </v-stepper-step>
        <v-stepper-content step="2">
          <v-card class="pa-4 ma-4">
            <v-radio-group v-model="selection">
              <v-radio label="Au hasard" value="random"></v-radio>
              <v-radio label="Choisir" value="select"></v-radio>
            </v-radio-group>
            <v-container v-if="selection == 'select'">
              <v-row>
                <v-col v-for="ext in extensions" :key="ext" cols="3">
                  <v-text-field v-model.number="cardsDistribution[ext]" :label="ext"></v-text-field>
                </v-col>
              </v-row>
            </v-container>
            <p v-if="selection == 'select' && sumCards != 10">
              Le total des cartes doit être 10.
            </p>
            <v-btn class="ma-2" v-if="(extensions.length > 0) && !(selection == 'select' && sumCards != 10)" @click="getRandomCards(); getSuggestions(); atStep=3">
              Suivant
            </v-btn>
            <v-btn class="ma-2" @click="atStep=1">
              Précédent
            </v-btn>
          </v-card>
        </v-stepper-content>

        <v-stepper-step step="3">
          Résultats
        </v-stepper-step>
        <v-stepper-content step="3">
          <v-card v-if="cards">
            <p v-if="extensions.includes('Alchimie')" class="pa-2">
              Puisque vous jouez avec l'extension <i>Alchimie</i>, vous devez ajouter la carte <b>Potion</b> au jeu.
            </p>
            <p v-if="extensions.includes('Prospérité')" class="pa-2">
              Puisque vous jouez avec l'extension <i>Prospérité</i>, vous pouvez ajouter les cartes <b>Platine</b> et <b>Colonie</b> au jeu.
            </p>
            <p v-if="extensions.includes('L\'Âge des ténèbres')" class="pa-2">
              Puisque vous jouez avec l'extension <i>L'Âge des ténèbres</i>, vous pouvez remplacer les cartes <b>Domaine</b> du départ par les cartes <b>Cabane</b>, <b>Nécropole</b> et <b>Domaine luxuriant</b>.
            </p>
            <v-tabs show-arrows>
              <v-tabs-slider></v-tabs-slider>
              <v-tab>
                <p>Aléatoire</p>
              </v-tab>
              <v-tab v-for="sugg in suggestions" :key="sugg['Combo']">
                <p>{{ sugg['Combo'] }}</p>
              </v-tab>
              <v-tab-item>
                <v-data-table dense :headers="headers" :items="cards" item-key="Card name" sort-by="Card name" group-by="Expansion" show-group-by hide-default-footer :items-per-page="25">
                  <template v-slot:item.Types="{ item }">
                    <p>{{ item.Types.join(', ') }}</p>
                  </template>
                </v-data-table>
              </v-tab-item>
              <v-tab-item v-for="sugg in suggestions" :key="sugg['Combo']">
                <v-data-table dense :headers="headers" :items="sugg['Cards']" item-key="Card name" sort-by="Card name" group-by="Expansion" show-group-by hide-default-footer :items-per-page="25">
                  <template v-slot:item.Types="{ item }">
                    <p>{{ item.Types.join(', ') }}</p>
                  </template>
                </v-data-table>
              </v-tab-item>
            </v-tabs>
          </v-card>
          <v-btn class="ma-2" @click="atStep=2">
            Précédent
          </v-btn>
        </v-stepper-content>
      </v-stepper>
    </v-container>
  </v-app>
</template>

<script>
import axios from "axios";

export default {
  name: "Home",
  data() {
    return {
      extensionsList: [
        { name: "Dominion", description: "Jeu de base" },
        { name: "L'Intrigue", description: "Extension de base" },
        { name: "Rivages", description: "Durée" },
        { name: "L'Âge des ténèbres", description: "Écarter" },
        { name: "L'Arrière-pays", description: "Effet à l'achat" },
        { name: "Abondance", description: "Variété" },
        { name: "Alchimie", description: "Potions" },
        { name: "Prospérité", description: "Argent" }
      ],
      rules: [
        value => [1,2,3,4,5,6,7,8].includes(value) || 'Nombre entier entre 1 et 8'
      ],
      extensions: [],
      cardsDistribution: {},
      selection: 'random',
      cards: null,
      numRandom: 2,
      atStep: 1,
      suggestions: null,
      headers: [
        { text: 'Nom', value: 'Card name', groupable: false },
        { text: 'Extension', value: 'Expansion' },
        { text: 'Types', value: 'Types', groupable: false },
        { text: 'Coût', value: 'Money cost', groupable: false },
        { text: 'Potions', value: 'Potion cost', groupable: false },
        { text: 'Raison', value: 'Type', groupable: false }
      ]
    };
  },
  computed: {
    sumCards() {
      var sum = 0
      for (var property in this.cardsDistribution) {
        sum += this.cardsDistribution[property]
      }
      return sum
    }
  },
  mounted: function() {
    axios
      .get(process.env.VUE_APP_API_URL + 'wakeup')
      .then(response => (console.log(response.data)))
      .catch(console.error)
  },
  methods: {
    getRandomCards() {
      var parameters
      if (this.selection == 'select') {
        parameters = { extensions: this.extensions, distribution: this.cardsDistribution }
      } else {
        parameters = { extensions: this.extensions }
      }
      axios
        .get(process.env.VUE_APP_API_URL + 'random_cards', { params: parameters })
        .then(response => (this.cards = response.data))
        .catch(console.error)
    },
    getRandomExtensions() {
      if (this.$refs.form.validate()) {
        var extensionsSample = this.getRandomSample(this.extensionsList, this.numRandom)
        console.log(extensionsSample[0].name)
        this.extensions = []
        for (let i = 0; (i < extensionsSample.length); i++) {
          this.extensions.push(extensionsSample[i].name)
        }
      }
    },
    getRandom(length) {
      return Math.floor(Math.random()*(length));
    },
    getRandomSample(arr, size) {
      var array = [...arr]
      var length = array.length;
      for(var i = size; i--;) {
        var index = this.getRandom(length);
        var temp = array[index];
        array[index] = array[i];
        array[i] = temp;
      }
      return array.slice(0, size);
    },
    getSuggestions() {
      axios
        .get(process.env.VUE_APP_API_URL + 'suggestions', { params: { extensions: this.extensions } })
        .then(response => (this.suggestions = response.data))
        .catch(console.error)
    }
  }
};
</script>
