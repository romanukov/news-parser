import Vue from 'vue'
import Router from 'vue-router'
import AuthLayout from "./layouts/auth";
import Login from './pages/auth/login'

Vue.use(Router)

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'home',
    },
    {
      path: '/auth/',
      name: 'auth',
      component: AuthLayout,
      children: [
        {
          path: 'login/',
          component: Login,
          name: 'login'
        }
      ]
    },
  ]
})
