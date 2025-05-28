<template>
    <div class="login-container">
        <!-- 导航栏 -->
        <nav class="navbar">
            <div class="logo">
                <v-icon icon="mdi-chart-timeline-variant" color="primary" size="x-large" />
                <span class="app-title">BPMN绘图助手</span>
            </div>
            <div class="nav-links">
                <router-link to="/" class="nav-link">首页</router-link>
                <router-link to="/register" class="nav-link">注册</router-link>
            </div>
        </nav>

        <!-- 主内容区 -->
        <div class="content-wrapper">
            <div class="login-form-container">
                <div class="login-card">
                    <div class="card-header">
                        <h1 class="form-title">登录</h1>
                        <p class="form-subtitle">欢迎回来，请登录您的账户</p>
                    </div>

                    <form @submit.prevent="handleLogin" class="login-form">
                        <div class="form-group">
                            <label for="account" class="form-label">账号(邮箱或手机号):</label>
                            <div class="input-container">
                                <v-icon icon="mdi-account" class="input-icon" />
                                <input type="text" id="account" v-model="account" placeholder="请输入邮箱或手机号"
                                    class="form-input">
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="password" class="form-label">密码:</label>
                            <div class="input-container">
                                <v-icon icon="mdi-lock" class="input-icon" />
                                <input :type="passwordVisible ? 'text' : 'password'" id="password" v-model="password"
                                    class="form-input">
                                <button type="button" @click="togglePasswordVisibility" class="password-toggle">
                                    <v-icon :icon="passwordVisible ? 'mdi-eye-off' : 'mdi-eye'" />
                                </button>
                            </div>
                        </div>

                        <div class="remember-me">
                            <div>
                                <input type="checkbox" id="remember">
                                <label for="remember" class="remember-label">记住我</label>
                            </div>
                            <router-link :to="{ name: 'forgot-password', query: { fromLogin: true } }"
                                class="forgot-password">
                                忘记密码?
                            </router-link>
                        </div>

                        <button type="submit" class="login-button">
                            登录
                        </button>
                    </form>
                    <div class="register-prompt">
                        还没有账号?
                        <router-link to="/register" class="register-link">立即注册</router-link>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const account = ref('');
const password = ref('');
const passwordVisible = ref(false);
const router = useRouter();
const userId = ref(null);

// 验证是否为邮箱
const isEmail = (str) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(str);
};

// 验证是否为手机号
const isPhoneNumber = (str) => {
    const phoneRegex = /^[0-9]{11}$/; // 假设手机号为 11 位数字
    return phoneRegex.test(str);
};

// 切换密码可见性
const togglePasswordVisibility = () => {
    passwordVisible.value = !passwordVisible.value;
};

const handleLogin = async () => {
    if (!account.value) {
        alert('请输入账号');
        return;
    }
    let url = '';
    let data = {};
    if (isEmail(account.value)) {
        url = 'http://localhost:8000/api/login_by_email';
        data = { email: account.value, password: password.value };
    } else if (isPhoneNumber(account.value)) {
        url = 'http://localhost:8000/api/login_by_phone';
        data = { phone_number: account.value, password: password.value };
    } else {
        alert('请输入有效的邮箱或手机号');
        return;
    }
    try {
        const response = await axios.post(url, data);
        if (response.status === 200) {
            // 检查是否存在密码重置标志
            const { passwordReset } = router.currentRoute.value.query;
            if (passwordReset === 'success') {
                sessionStorage.setItem('passwordResetSuccess', 'true');
                // 清除查询参数
                router.replace({ name: 'Login' });
            }

            // alert('登录成功');
            console.log('Login-success'); // 输出登录结果
            const userInfo = {
                id: response.data.user_id,
                username: response.data.username,
                email: response.data.email,
                phone_number: response.data.phone_number,
                password: response.data.password
            };
            sessionStorage.setItem('user_info', JSON.stringify(userInfo));
            // console.log('Login-User info:', userInfo); // 输出用户信息
            userId.value = response.data.user_id; // 存储用户 ID    
            router.push('/home');
        } else {
            const errorMessage = response.data && response.data.detail ? response.data.detail : '未知错误';
            alert(`登录失败：${errorMessage}`);
        }
    } catch (error) {
        console.error('登录出错:', error);
        const errorMessage = error.response && error.response.data && error.response.data.detail
            ? error.response.data.detail
            : '登录出错，请稍后再试';
        alert(errorMessage);
    }
};

const goToRegister = () => {
    router.push('/register');
};
</script>

<style scoped>
/* 全局样式 */
body {
    font-family: 'Roboto', sans-serif;
    margin: 0;
    padding: 0;
}

/* 导航栏样式 */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 40px;
    background-color: white;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 100;
}

.logo {
    display: flex;
    align-items: center;
}

.app-title {
    margin-left: 10px;
    font-size: 20px;
    font-weight: bold;
    color: #333;
}

.nav-links {
    display: flex;
    gap: 20px;
}

.nav-link {
    text-decoration: none;
    color: #333;
    font-weight: 500;
    transition: color 0.3s ease;
}

.nav-link:hover {
    color: #007bff;
}

/* 主内容区样式 */
.content-wrapper {
    display: flex;
    height: 100vh;
    padding-top: 80px;
}

.login-form-container {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40px;
}

.login-card {
    background-color: white;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 450px;
    padding: 40px;
}

.card-header {
    text-align: center;
    margin-bottom: 40px;
}

.form-title {
    font-size: 28px;
    font-weight: bold;
    color: #333;
    margin-bottom: 10px;
}

.form-subtitle {
    font-size: 16px;
    color: #666;
}

.form-group {
    margin-bottom: 25px;
}

.form-label {
    display: block;
    margin-bottom: 8px;
    font-size: 14px;
    font-weight: 500;
    color: #333;
}

.input-container {
    position: relative;
    display: flex;
    align-items: center;
}

.input-icon {
    position: absolute;
    left: 15px;
    color: #999;
}

.form-input {
    width: 100%;
    padding: 14px 14px 14px 45px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 16px;
    color: #333;
    transition: border-color 0.3s ease;
}

.form-input:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.2);
}

.password-toggle {
    position: absolute;
    right: 15px;
    background: none;
    border: none;
    cursor: pointer;
    color: #999;
}

.remember-me {
    display: flex;
    justify-content: space-between;
    margin-bottom: 30px;
}


.remember-label {
    font-size: 14px;
    color: #666;
}

.forgot-password {
    font-size: 14px;
    color: #007bff;
    text-decoration: none;
    align-items: end;
    transition: color 0.3s ease;
}

.forgot-password:hover {
    color: #0056b3;
}

.login-button {
    width: 100%;
    padding: 16px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.login-button:hover {
    background-color: #0056b3;
}

.social-login {
    margin-top: 40px;
}

.divider {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
}

.divider::before,
.divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background-color: #eee;
}

.divider span {
    margin: 0 15px;
    font-size: 14px;
    color: #999;
}

.social-buttons {
    display: flex;
    justify-content: center;
    gap: 15px;
}

.social-button {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background-color: #f5f5f5;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.social-button:hover {
    background-color: #e5e5e5;
}

.register-prompt {
    text-align: center;
    margin-top: 30px;
    font-size: 14px;
    color: #666;
}

.register-link {
    color: #007bff;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s ease;
}

.register-link:hover {
    color: #0056b3;
}

/* 右侧插图区域 */
.illustration-container {
    flex: 1;
    background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
}

.illustration-content {
    max-width: 400px;
    text-align: center;
}

.illustration-title {
    font-size: 32px;
    font-weight: bold;
    margin-bottom: 20px;
}

.illustration-text {
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 40px;
}

.features {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.feature-item {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}

/* 响应式设计 */
@media (max-width: 992px) {
    .illustration-container {
        display: none;
    }
}

@media (max-width: 576px) {
    .login-card {
        padding: 30px;
    }

    .navbar {
        padding: 15px 20px;
    }

    .app-title {
        font-size: 18px;
    }
}
</style>