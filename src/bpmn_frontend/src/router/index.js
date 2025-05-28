import { createRouter, createWebHistory } from 'vue-router';
import WelcomeView from '../views/WelcomeView.vue';
import HomeView from '../views/HomeView.vue';
import Login from '../login/Login.vue';
import Register from '../login/Register.vue';
import ForgotPassword from '../login/ForgotPassword.vue';
import UserInfo from '../views/UserInfo.vue'; // 引入用户信息组件

const routes = [
    {
        path: '/',
        name: 'welcome',
        component: WelcomeView
    },
    {
        path: '/login',
        name: 'login',
        component: Login
    },
    {
        path: '/register',
        name: 'register',
        component: Register
    },
    {
        path: '/home',
        name: 'home',
        component: HomeView
    },
    {
        path: '/forgot-password',
        name: 'forgot-password',
        component: ForgotPassword
    },
    {
        path: '/user-info',
        name: 'user-info',
        component: UserInfo
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

export default router;