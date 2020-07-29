<style>
  .row {
    margin-top: 15px;
    margin-bottom: 15px;
  }
  .sansserif{
    font-family: 'Franklin Gothic Medium', 'Arial Narrow', Arial, sans-serif;
  }
  table, th, td {
    border: 0px;
  }
  .th1, .td1 {
    border: 0px;
  }
  .tab {
    padding-left: 2em;
  }
  table#t01 {
    width: 75%;
    text-align: center;
    vertical-align: middle;
    margin: 20px;
  }
  div.attack-table td {
    padding: 5px;
  }
  div.attack-table tr:nth-child(odd) {
    background-color: #f2f2f2;
  }
  div.attack-table tr:hover {
    background-color: #dddddd;
  }
  .crit{
    animation:blinkingText 0.3s infinite;
  }
  @keyframes blinkingText{
      0%{ color: #000; }
     19%{ color: #000; }
     60%{ color: rgb(255, 0, 0); }
     99%{ color: rgb(255, 0, 0); }
    100%{ color: #000; }
  }
  #input-add-die-mod {
    width: 4em;
  }
</style>
<template>
  <!-- eslint-disable max-len -->
  <div>
    <b-container fluid class="mx-auto px-5">
      <b-row>
        <h1>Conjure Animals Helper</h1>
      </b-row>
      <b-row>
        <b-col class="mx-1">
          <b-row>
            <h2>Conjure a Pack</h2>
          </b-row>
          <b-row align-h="start">
            <b-form-select
              v-model="selectedAnimal"
              :options="options"
              class=w-50
            ></b-form-select>
          </b-row>
          <b-row>
            <b-form-spinbutton
              id="sb-vertical"
              v-model="numAnimals"
              class="w-auto"
            >
            </b-form-spinbutton>
            <label for="sb-vertical" class="w-25 ml-3 my-auto">How Many?</label>
            <b-form-checkbox
              id="checkbox-1"
              v-model="mightyStatus"
              name="checkbox-1"
              value=1
              unchecked-value=0
              class="my-auto"
            >
              Mighty Summoner
            </b-form-checkbox>
          </b-row>
          <b-row align-h="start">
            <b-button
              variant="outline-primary"
              class=w-75
              v-on:click="conjureAnimals"
            >Conjure Animals</b-button>
          </b-row>
          <b-row>
            <b-card-text v-html="animalText">
              {{ this.animalText }}
            </b-card-text>
          </b-row>
        </b-col>
        <b-col class="mx-1">
          <b-row>
            <h2>Attack an Enemy</h2>
          </b-row>
          <b-row>
            <b-form-checkbox
              id="checkbox-advantage"
              v-model="advantage"
              name="checkbox-advantage"
              value=1
              unchecked-value=0
              class="w-auto mr-5"
            >
              Advantage
            </b-form-checkbox>
            <b-form-checkbox
              id="checkbox-disadvantage"
              v-model="disadvantage"
              name="checkbox-disadvantage"
              value=1
              unchecked-value=0
              class="w-auto"
            >
              Disadvantage
            </b-form-checkbox>
          </b-row>
          <b-row>
            <b-form-spinbutton
              id="sb-enemyAC"
              v-model="enemyAC"
              class="w-auto mr-3"
            >
            </b-form-spinbutton>
            <label for="sb-enemyAC" class="w-25 my-auto">Target AC</label>
          </b-row>
          <b-row>
            <b-button
              v-b-modal.modal-add-dice
              class="w-auto mr-5"
            >
              Roll Additional Dice on Hit
            </b-button>
            <b-modal
              id="modal-add-dice"
              title="Additional On-hit Dice"
              size="md"
            >
              <b-row align-h="center">
                <b-form-select
                  v-model="addDieNum"
                  :options="addDieNumOptions"
                  class="w-auto mr-1"
                ></b-form-select>
                <label class="w-auto my-auto mr-1">d</label>
                <b-form-select
                  v-model="addDieMax"
                  :options="addDieMaxOptions"
                  class="w-auto mr-1"
                ></b-form-select>
                <label class="my-auto mr-1">+</label>
                <b-form-input
                  id="input-add-die-mod"
                  v-model="addDieMod"
                  type="number"
                ></b-form-input>
              </b-row>
              <b-row align-h="center">
                <b-form-radio-group
                  id="radio-add-dice"
                  v-model="addDieType"
                  :options="addDieTypeOptions"
                  button-variant="outline-dark"
                  buttons
                  name="radios-btn-default"
                ></b-form-radio-group>
              </b-row>
            </b-modal>
          </b-row>
          <b-row>
          </b-row>
          <b-row>
            <b-form-select
              v-model="selectedAttack"
              :options="attackOptions"
              class="w-50 mr-3"
            ></b-form-select>
            <b-button
              variant="outline-danger"
              class="w-auto"
              v-on:click="attack"
            >Attack</b-button>
          </b-row>
          <b-row>
            <b-card-text v-html="attackText">
              {{ this.attackText }}
            </b-card-text>
          </b-row>
        </b-col>
        <b-col class="mx-1">
          <b-row>
            <h2>Manage Hit Points</h2>
          </b-row>
          <b-row>
            <b-form-checkbox
              id="checkbox-aoe"
              v-model="checkAoe"
              name="checkbox-aoe"
              value=1
              unchecked-value=0
              class="my-auto mr-3"
            >
              AOE
            </b-form-checkbox>
            <b-form-spinbutton
              id="sb-hitpoints-mod"
              v-model="hitPointsMod"
              class="w-auto"
            >
            </b-form-spinbutton>
          </b-row>
          <b-row align-v="center">
            <b-button
              variant="danger"
              v-on:click="damage"
              class="w-auto mr-3"
            >Damage</b-button>
            <b-button
              variant="success"
              v-on:click="heal"
              class="w-auto mr-3"
            >Heal</b-button>
            <b-button
              variant="info"
              v-on:click="tempHP"
              class="w-auto"
            >Temp HP</b-button>
          </b-row>
          <b-row>
            <b-button
              variant="outline-dark"
              @click="clearSelected"
              class="w-50"
            >Reset Selection</b-button>
          </b-row>
          <b-table
            id="table-hit-points"
            ref="hitPointTable"
            striped
            hover
            primary-key="uuid"
            selectable="True"
            select-mode="multi"
            selected-variant="success"
            :items="hitPoints"
            :fields="fields"
            @row-selected="onRowSelected"
          ></b-table>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      selectedAnimal: 'wolf',
      options: [],
      numAnimals: 8,
      mightyStatus: 0,
      disadvantage: 0,
      advantage: 0,
      animalText: '',
      attackText: '',
      enemyAC: 12,
      addDieNum: '0',
      addDieNumOptions: [
        '0',
        '1',
        '2',
        '3',
        '4',
        '5',
      ],
      addDieMax: '20',
      addDieMaxOptions: [
        '4',
        '6',
        '8',
        '10',
        '12',
        '20',
      ],
      addDieMod: '0',
      addDieType: 'None',
      addDieTypeOptions: [
        'None',
        'Additional Damage',
        'Saving Throw',
      ],
      selectedAttack: '',
      attackOptions: [],
      checkAoe: 0,
      hitPointsMod: 0,
      fields: [
        { key: 'name' },
        { key: 'hitPoints' },
        { key: 'temporaryHP' },
      ],
      hitPoints: {},
      selected: [],
      pack: {},
    };
  },
  mounted() {
    if (localStorage.getItem('pack')) {
      try {
        this.pack = JSON.parse(localStorage.getItem('pack'));
      } catch (e) {
        localStorage.removeItem('pack');
      }
    }
    this.loadAnimals();
  },
  methods: {
    onRowSelected(items) {
      this.selected = items;
    },
    loadAnimals() {
      const path = 'http://sarulian.com:5000/animals';
      axios.get(path)
        .then((res) => {
          this.options = res.data;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
        });
    },
    conjureAnimals() {
      const path = 'http://sarulian.com:5000/';
      const toLoad = {
        name: this.selectedAnimal,
        numAnimals: this.numAnimals,
        mighty: this.mightyStatus,
      };
      this.attackText = '';
      axios.post(path, toLoad)
        .then((res) => {
          const parsed = JSON.stringify(res.data.animalInfo);
          localStorage.setItem('pack', parsed);
          this.animalText = res.data.animalText;
          this.attackOptions = res.data.attackNames;
          const firstAttack = this.attackOptions[0];
          this.selectedAttack = firstAttack;
          this.refreshHitpoints();
          // eslint-disable-next-line
          console.log(res.data);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
        });
    },
    attack() {
      const path = 'http://sarulian.com:5000/attack';
      const payload = {
        pack: JSON.parse(localStorage.getItem('pack')),
        attackInfo: {
          disadvantage: this.disadvantage,
          advantage: this.advantage,
          enemyAC: this.enemyAC,
          attackName: this.selectedAttack,
          addDieNum: this.addDieNum,
          addDieMax: this.addDieMax,
          addDieMod: this.addDieMod,
          addDieType: this.addDieType,
          selectedRows: this.selected,
        },
      };
      axios.post(path, payload)
        .then((res) => {
          this.attackText = res.data.attackText;
          // eslint-disable-next-line
          console.log(res.data);
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
        });
    },
    damage() {
      const path = 'http://sarulian.com:5000/hitpoints';
      const payload = {
        pack: JSON.parse(localStorage.getItem('pack')),
        damageInfo: {
          aoe: this.checkAoe,
          hitPointsMod: this.hitPointsMod,
          type: 'damage',
          selectedRows: this.selected,
        },
      };
      axios.post(path, payload)
        .then((res) => {
          this.hitPoints = res.data.hitPointList;
          const parsed = JSON.stringify(res.data.pack);
          localStorage.setItem('pack', parsed);
          this.refreshHitpoints();
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
        });
    },
    heal() {
      const path = 'http://sarulian.com:5000/hitpoints';
      const payload = {
        pack: JSON.parse(localStorage.getItem('pack')),
        damageInfo: {
          aoe: this.checkAoe,
          hitPointsMod: this.hitPointsMod,
          type: 'heal',
          selectedRows: this.selected,
        },
      };
      axios.post(path, payload)
        .then((res) => {
          this.hitPoints = res.data.hitPointList;
          const parsed = JSON.stringify(res.data.pack);
          localStorage.setItem('pack', parsed);
          this.refreshHitpoints();
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
        });
    },
    tempHP() {
      const path = 'http://sarulian.com:5000/hitpoints';
      const payload = {
        pack: JSON.parse(localStorage.getItem('pack')),
        damageInfo: {
          aoe: this.checkAoe,
          hitPointsMod: this.hitPointsMod,
          type: 'tempHP',
          selectedRows: this.selected,
        },
      };
      axios.post(path, payload)
        .then((res) => {
          this.hitPoints = res.data.hitPointList;
          const parsed = JSON.stringify(res.data.pack);
          localStorage.setItem('pack', parsed);
          this.refreshHitpoints();
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
        });
    },
    clearSelected() {
      this.$refs.hitPointTable.clearSelected();
    },
    refreshHitpoints() {
      const pack = JSON.parse(localStorage.getItem('pack'));
      this.hitPoints = [];
      const keys = Object.keys(pack);
      const values = Object.values(pack);
      for (let i = 0; i <= keys.length; i += 1) {
        this.hitPoints.push(
          {
            uuid: values[i].uuid,
            name: values[i].name,
            hitPoints: values[i].hit_points,
            temporaryHP: values[i].temporary_hit_points,
          },
        );
      }
    },
  },
};
</script>
