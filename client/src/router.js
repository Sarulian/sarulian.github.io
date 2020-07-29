import Vue from 'vue';
import VueRouter from 'vue-router';
import Ping from './components/Ping.vue';
import Helper from './components/Helper.vue';

Vue.use(VueRouter);

export default new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/ping',
      name: 'Ping',
      component: Ping,
    },
    {
      path: '/',
      name: 'Helper',
      component: Helper,
    },
  ],
});
