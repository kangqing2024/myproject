<template>
    <div class="user-info-container">
        <!-- 顶部导航栏 -->
        <nav class="navbar">
            <div class="logo">
                <v-icon icon="mdi-chart-timeline-variant" color="primary" size="x-large" />
                <span class="app-title">BPMN绘图助手</span>
            </div>
            <div class="nav-links">
                <router-link to="/home" class="nav-link">主页</router-link>
                <router-link to="/login" class="nav-link">退出登录</router-link>
            </div>
        </nav>

        <!-- 用户信息卡片 -->
        <div class="user-card">
            <div class="card-header">
                <h1 class="title">用户信息</h1>
                <div class="edit-toggle">
                    <v-btn @click="toggleEdit" :loading="isLoading" color="primary" outlined>
                        {{ isEditing ? '取消编辑' : '编辑信息' }}
                    </v-btn>
                </div>
            </div>

            <form @submit.prevent="saveUserInfo" class="user-form">
                <!-- 用户名 -->
                <div class="form-group">
                    <label for="username" class="form-label">用户名:</label>
                    <div class="input-container">
                        <v-icon icon="mdi-account" class="input-icon" />
                        <input type="text" id="username" v-model="username" :disabled="!isEditing" class="form-input"
                            placeholder="请输入用户名">
                    </div>
                </div>

                <!-- 邮箱 -->
                <div class="form-group">
                    <label for="email" class="form-label">邮箱:</label>
                    <div class="input-container">
                        <v-icon icon="mdi-email" class="input-icon" />
                        <input type="email" id="email" v-model="email" :disabled="!isEditing" class="form-input"
                            placeholder="请输入邮箱">
                    </div>
                </div>

                <!-- 手机号 -->
                <div class="form-group">
                    <label for="phone" class="form-label">手机号:</label>
                    <div class="input-container">
                        <v-icon icon="mdi-phone" class="input-icon" />
                        <input type="text" id="phone" v-model="phone" :disabled="!isEditing" class="form-input"
                            placeholder="请输入手机号">
                    </div>
                </div>

                <!-- 密码 -->
                <div class="button-container" >
                    <button type="submit" class="reset-button">
                        重置密码
                    </button>
                </div>

                <!-- 保存按钮 -->
                <div class="button-container" v-if="isEditing">
                    <button type="submit" class="save-button" :disabled="!isEditing">
                        保存修改
                    </button>
                </div>

                <!-- 注销账号按钮 -->
                <div class="button-container">
                    <button type="button" class="delete-button" @click="confirmDeleteAccount">
                        注销账号
                    </button>
                </div>
            </form>
        </div>


    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const username = ref('');
const email = ref('');
const phone = ref('');
const password = ref('');
const isEditing = ref(false);
const passwordVisible = ref(false);
const isLoading = ref(false);

// 返回主页
const goBackHome = () => {
    router.push('/home');
};

// 切换编辑状态
const toggleEdit = () => {
    isEditing.value = !isEditing.value;
};

// 重置密码
const resetPassword = () => {
    router.push({ name: 'forgot-password', query: { fromUserInfo: true } });
};

// 切换密码可见性
const togglePasswordVisibility = () => {
    passwordVisible.value = !passwordVisible.value;
};

// 保存用户信息
const saveUserInfo = async () => {
    isLoading.value = true;
    const userInfo = sessionStorage.getItem('user_info');

    if (userInfo) {
        try {
            const { id } = JSON.parse(userInfo);
            const payload = {
                id,
                username: username.value,
                email: email.value,
                phone: phone.value
            };

            const response = await axios.post('http://localhost:8000/api/update_user_info', payload);

            if (response.status === 200) {
                alert('用户信息保存成功');
                // 更新 sessionStorage 中的用户信息
                sessionStorage.setItem('user_info', JSON.stringify(response.data));
                // 更新前端显示的用户信息
                username.value = response.data.username;
                email.value = response.data.email;
                phone.value = response.data.phone_number;
                toggleEdit();
            } else {
                alert('保存用户信息失败，请稍后再试');
            }
        } catch (error) {
            console.error('Error updating user info:', error);
            alert('保存用户信息时出错，请稍后再试');
        } finally {
            isLoading.value = false;
        }
    }
};

// 获取用户信息
const fetchUserInfo = () => {
    const userInfo = sessionStorage.getItem('user_info');

    if (userInfo) {
        try {
            const { username: userUsername, email: userEmail, phone_number: userPhone, password: userPassword } = JSON.parse(userInfo);
            username.value = userUsername;
            email.value = userEmail;
            phone.value = userPhone;
            password.value = userPassword;
        } catch (error) {
            console.error('Error parsing user info:', error);
            alert('解析用户信息失败，请重新登录');
            router.push('/login');
        }
    } else {
        alert('用户未登录，请登录');
        router.push('/login');
    }

    // 检查密码重置标志
    const passwordResetSuccess = sessionStorage.getItem('passwordResetSuccess');
    if (passwordResetSuccess === 'true') {
        alert('密码已成功重置');
        // 清除标志
        sessionStorage.removeItem('passwordResetSuccess');
    }
};

// 确认注销账号
const confirmDeleteAccount = () => {
    const confirmResult = confirm('确定要注销账号吗？此操作不可恢复。');
    if (confirmResult) {
        deleteAccount();
    }
};

// 执行注销账号
const deleteAccount = async () => {
    const userInfo = sessionStorage.getItem('user_info');
    if (userInfo) {
        try {
            const { id } = JSON.parse(userInfo);
            const response = await axios.post('http://localhost:8000/api/delete_user', { id });
            if (response.status === 200) {
                alert('账号已成功注销');
                sessionStorage.removeItem('user_info');
                router.push('/');
            } else {
                alert('注销账号失败，请稍后再试');
            }
        } catch (error) {
            console.error('Error deleting user account:', error);
            alert('注销账号时出错，请稍后再试');
        }
    }
};


// 监听路由变化，当从密码重置页面返回时，刷新用户信息
const handleRouteChange = () => {
    const query = router.currentRoute.value.query;
    if (query.passwordReset === 'success') {
        alert('密码已成功重置');
        fetchUserInfo();
        // 清除查询参数
        router.replace({ path: router.currentRoute.value.path });
    }
};

onMounted(() => {
    fetchUserInfo();

    // 添加路由守卫，监听路由变化
    router.beforeEach((to, from, next) => {
        if (from.name === 'ForgotPassword' && to.name === 'UserInfo') {
            handleRouteChange();
        }
        next();
    });
});
</script>

<style scoped>
/* 全局样式 */
body {
    font-family: 'Roboto', sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f9fafb;
}

/* 导航栏样式 */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 40px;
    background-color: white;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
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

/* 用户信息卡片样式 */
.user-card {
    max-width: 600px;
    margin: 120px auto 40px;
    background-color: white;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    padding: 40px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 40px;
}

.title {
    font-size: 28px;
    font-weight: bold;
    color: #333;
    margin: 0;
}

.edit-toggle {
    display: flex;
    gap: 10px;
}

.user-form {
    display: flex;
    flex-direction: column;
    gap: 25px;
}

.form-group {
    margin-bottom: 15px;
}

.form-label {
    display: block;
    margin-bottom: 10px;
    font-size: 14px;
    font-weight: 500;
    color: #555;
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
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
}

.password-group {
    display: flex;
    gap: 15px;
    align-items: center;
}

.password-toggle {
    position: absolute;
    right: 15px;
    background: none;
    border: none;
    cursor: pointer;
    color: #999;
}

.reset-button {
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

.button-container {
    margin-top: 20px;
}

.save-button {
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

.save-button:hover {
    background-color: #0056b3;
}

.save-button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}

/* 底部样式 */
.footer {
    text-align: center;
    padding: 20px;
    color: #999;
    font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 640px) {
    .user-card {
        margin: 100px 20px 40px;
        padding: 30px;
    }

    .navbar {
        padding: 15px 20px;
    }

    .title {
        font-size: 24px;
    }

    .password-group {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .reset-button {
        min-width: auto;
    }
}
</style>