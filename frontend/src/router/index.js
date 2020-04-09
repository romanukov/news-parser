import Vue from 'vue';
import Router from 'vue-router';

import Messages from '@/pages/Messages';
import Login from '@/pages/Login';
import Feeds from '@/pages/Feeds';
import Settings from '@/pages/Settings';
import Profile from '@/pages/Profile';
import Sources from '@/pages/Sources';
import Root from '@/pages/Root';
import SharedMessage from '@/pages/SharedMessage';

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'Root',
      component: Root,
    },
    {
      path: '/messages/',
      name: 'Messages',
      component: Messages,
    },
    {
      path: '/login/',
      name: 'Login',
      component: Login,
    },
    {
      path: '/feeds/',
      name: 'Feeds',
      component: Feeds,
    },
    {
      path: '/settings/',
      name: 'Settings',
      component: Settings,
    },
    {
      path: '/profile/',
      name: 'Profile',
      component: Profile,
    },
    {
      path: '/sources/',
      name: 'Sources',
      component: Sources,
    },
    {
      path: '/shared/:id',
      name: 'Shared',
      component: SharedMessage,
    },
  ],
});
