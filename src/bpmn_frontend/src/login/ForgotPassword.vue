<template>
    <div class="forgot-password-container">
        <!-- 背景装饰 -->
        <div class="bg-decoration top-right"></div>
        <div class="bg-decoration bottom-left"></div>

        <!-- 顶部导航 -->
        <nav class="app-nav">
            <div class="logo">
                <v-icon icon="mdi-chart-timeline-variant" color="primary" size="x-large" />
                <span class="app-title">BPMN绘图助手</span>
            </div>
        </nav>

        <!-- 主内容区 -->
        <div class="content-wrapper">
            <div class="forgot-password-card">
                <div class="card-header">
                    <h1>忘记密码</h1>
                    <p class="subtitle">请输入您的邮箱或手机号重置密码</p>
                </div>

                <!-- 步骤指示器 -->
                <div class="steps-indicator">
                    <div class="step active">
                        <div class="step-number">1</div>
                        <span class="step-label">验证账号</span>
                    </div>
                    <div class="step-line" :class="{ active: step >= 2 }"></div>
                    <div class="step" :class="{ active: step >= 2 }">
                        <div class="step-number">2</div>
                        <span class="step-label">验证码</span>
                    </div>
                    <div class="step-line" :class="{ active: step >= 3 }"></div>
                    <div class="step" :class="{ active: step >= 3 }">
                        <div class="step-number">3</div>
                        <span class="step-label">重置密码</span>
                    </div>
                </div>

                <!-- 表单容器 -->
                <div class="form-container">
                    <!-- 邮箱/手机号输入表单 -->
                    <div class="form-step" v-show="step === 1">
                        <div class="form-group">
                            <label for="account">邮箱或手机号:</label>
                            <div class="input-wrapper">
                                <v-icon icon="mdi-account" class="input-icon" />
                                <input type="text" id="account" v-model="account" placeholder="请输入邮箱或手机号">
                            </div>
                        </div>

                        <button type="button" @click="sendResetCode" class="primary-button">
                            发送重置验证码
                        </button>
                    </div>

                    <!-- 验证码输入表单 -->
                    <div class="form-step" v-show="step === 2">
                        <div class="form-group">
                            <label for="verification-code">验证码:</label>
                            <div class="input-wrapper">
                                <v-icon icon="mdi-numeric" class="input-icon" />
                                <input type="text" id="verification-code" v-model="verification_code"
                                    placeholder="请输入验证码">
                            </div>
                            <p class="hint">验证码已发送至 {{ account.value }}</p>
                        </div>

                        <button type="button" @click="verifyCode" class="primary-button"
                            :disabled="verification_code.length !== 6 || isVerifying">
                            {{ isVerifying ? '验证中...' : '验证' }}
                        </button>
                    </div>

                    <!-- 新密码输入表单 -->
                    <div class="form-step" v-show="step === 3">
                        <div class="form-group">
                            <label for="new-password">新密码:</label>
                            <div class="input-wrapper password-input">
                                <v-icon icon="mdi-lock" class="input-icon" />
                                <input :type="passwordVisible ? 'text' : 'password'" id="new-password"
                                    v-model="new_password" placeholder="请输入新密码">
                                <button type="button" @click="togglePasswordVisibility" class="toggle-button">
                                    <v-icon :icon="passwordVisible ? 'mdi-eye-off' : 'mdi-eye'" />
                                </button>
                            </div>
                            <p class="hint">密码至少 8 位，包含字母和数字</p>

                            <!-- 密码强度指示器 -->
                            <div class="password-strength">
                                <div class="strength-label">密码强度:</div>
                                <div class="strength-bar">
                                    <div class="strength-fill"
                                        :style="{ width: passwordStrengthWidth, backgroundColor: passwordStrengthColor }">
                                    </div>
                                </div>
                                <div class="strength-text" :class="passwordStrengthClass">{{ passwordStrengthText }}
                                </div>
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="confirm-password">确认密码:</label>
                            <div class="input-wrapper password-input">
                                <v-icon icon="mdi-lock-check" class="input-icon" />
                                <input :type="confirmPasswordVisible ? 'text' : 'password'" id="confirm-password"
                                    v-model="confirm_password" placeholder="请再次输入密码">
                                <button type="button" @click="toggleConfirmPasswordVisibility" class="toggle-button">
                                    <v-icon :icon="confirmPasswordVisible ? 'mdi-eye-off' : 'mdi-eye'" />
                                </button>
                            </div>
                        </div>

                        <button type="button" @click="resetPassword" class="primary-button"
                            :disabled="new_password.length === 0 || new_password !== confirm_password || !isPasswordValid()">
                            确认重置
                        </button>
                    </div>
                </div>

                <!-- 返回按钮 -->
                <div class="back-button">
                    <button type="button" @click="goBack">
                        <v-icon icon="mdi-arrow-left" /> 返回登录
                    </button>
                </div>
            </div>
        </div>


    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router';

const account = ref('');
const verification_code = ref('');
const new_password = ref('');
const confirm_password = ref('');
const showNewPasswordForm = ref(false);
const passwordVisible = ref(false);
const confirmPasswordVisible = ref(false);
const router = useRouter();
const route = useRoute();
const token = ref('');
const isVerifying = ref(false);
const step = ref(1); // 1:输入账号, 2:验证, 3:重置密码

// 从路由参数中获取来源页面标志
const fromLogin = ref(route.query.fromLogin === 'true');
const fromUserInfo = ref(route.query.fromUserInfo === 'true');

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

// 切换确认密码可见性
const toggleConfirmPasswordVisibility = () => {
    confirmPasswordVisible.value = !confirmPasswordVisible.value;
};

const sendResetCode = async () => {
    if (!account.value) {
        showToast('请输入邮箱或手机号', 'error');
        return;
    }
    let url = '';
    let data = {};
    if (isEmail(account.value)) {
        url = 'http://localhost:8000/api/send_email_reset_code';
        data = { email: account.value };
    } else if (isPhoneNumber(account.value)) {
        url = 'http://localhost:8000/api/send_phone_reset_code';
        data = { phone_number: account.value };
    } else {
        showToast('请输入有效的邮箱或手机号', 'error');
        return;
    }
    try {
        const response = await axios.post(url, data);
        if (response.status === 200) {
            showToast('重置验证码已发送，请检查您的邮箱或手机', 'success');
            step.value = 2; // 进入验证步骤
        } else {
            showToast(`发送重置验证码失败：${response.data.detail}`, 'error');
        }
    } catch (error) {
        console.error('发送重置验证码出错:', error);
        showToast('发送重置验证码出错，请稍后再试', 'error');
    }
};

const verifyCode = async () => {
    if (isVerifying.value) return;
    isVerifying.value = true;

    let url = '';
    let data = {};
    if (isEmail(account.value)) {
        url = 'http://localhost:8000/api/verify_email_reset_code';
        data = { email: account.value, verification_code: verification_code.value };
    } else if (isPhoneNumber(account.value)) {
        url = 'http://localhost:8000/api/verify_phone_reset_code';
        data = { phone_number: account.value, verification_code: verification_code.value };
    }
    try {
        const response = await axios.post(url, data);
        if (response.status === 200) {
            showToast('验证码验证成功', 'success');
            step.value = 3; // 进入重置密码步骤
            showNewPasswordForm.value = true;
            // 假设后端返回了一个临时令牌
            token.value = response.data.token;
        } else {
            showToast(`验证码验证失败：${response.data.detail}`, 'error');
        }
    } catch (error) {
        console.error('验证码验证出错:', error);
        showToast('验证码验证出错，请稍后再试', 'error');
    } finally {
        isVerifying.value = false;
    }
};

// 密码强度计算
const passwordStrength = computed(() => {
    if (!new_password.value) return 0;
    let strength = 0;
    if (new_password.value.length >= 8) strength += 25;
    if (/[A-Z]/.test(new_password.value)) strength += 25;
    if (/[0-9]/.test(new_password.value)) strength += 25;
    if (/[^A-Za-z0-9]/.test(new_password.value)) strength += 25;
    return strength;
});

const passwordStrengthText = computed(() => {
    if (passwordStrength.value === 0) return '未输入';
    if (passwordStrength.value < 25) return '弱';
    if (passwordStrength.value < 50) return '中';
    if (passwordStrength.value < 75) return '强';
    return '非常强';
});

const passwordStrengthColor = computed(() => {
    if (passwordStrength.value === 0) return '#E5E7EB';
    if (passwordStrength.value < 25) return '#EF4444';
    if (passwordStrength.value < 50) return '#F59E0B';
    if (passwordStrength.value < 75) return '#10B981';
    return '#10B981';
});

const passwordStrengthWidth = computed(() => `${passwordStrength.value}%`);

const passwordStrengthClass = computed(() => {
    if (passwordStrength.value === 0) return 'text-gray-500';
    if (passwordStrength.value < 25) return 'text-red-500';
    if (passwordStrength.value < 50) return 'text-yellow-500';
    if (passwordStrength.value < 75) return 'text-green-500';
    return 'text-green-600 font-bold';
});

// 密码强度验证
const isPasswordValid = () => {
    const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/; // 至少 8 位，包含字母和数字
    return passwordRegex.test(new_password.value) && new_password.value === confirm_password.value;
};

const resetPassword = async () => {
    if (!isPasswordValid()) {
        showToast('密码强度不足或两次输入的密码不一致，请重新输入', 'error');
        return;
    }
    let url = '';
    let data = {};
    if (isEmail(account.value)) {
        url = 'http://localhost:8000/api/reset_password_by_email';
        data = { email: account.value, new_password: new_password.value, token: token.value };
    } else if (isPhoneNumber(account.value)) {
        url = 'http://localhost:8000/api/reset_password_by_phone';
        data = { phone_number: account.value, new_password: new_password.value, token: token.value };
    }
    try {
        const response = await axios.post(url, data);
        if (response.status === 200) {
            showToast('密码重置成功', 'success');
            // 使用路由参数中的标志决定跳转位置
            if (fromLogin.value) {
                router.push({ name: 'login', query: { passwordReset: 'success' } });
            } else if (fromUserInfo.value) {
                router.push({ name: 'user-info', query: { passwordReset: 'success' } });
            } else {
                // 默认跳转到登录页
                router.push({ name: 'login', query: { passwordReset: 'success' } });
            }
        } else {
            showToast(`密码重置失败：${response.data.detail}`, 'error');
        }
    } catch (error) {
        console.error('密码重置出错:', error);
        showToast('密码重置出错，请稍后再试', 'error');
    }
};

const goBack = () => {
    router.go(-1);
};

// 简单的Toast提示
const showToast = (message, type = 'info') => {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
};

// 监听路由变化，更新来源标志
onMounted(() => {
    fromLogin.value = route.query.fromLogin === 'true';
    fromUserInfo.value = route.query.fromUserInfo === 'true';
});
</script>

<style scoped>
/* 基础样式 */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: 'Inter', sans-serif;
}

.forgot-password-container {
    position: relative;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
}

/* 背景装饰 */
.bg-decoration {
    position: absolute;
    width: 500px;
    height: 500px;
    border-radius: 50%;
    z-index: 0;
}

.top-right {
    top: -250px;
    right: -250px;
    background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
    opacity: 0.1;
}

.bottom-left {
    bottom: -250px;
    left: -250px;
    background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
    opacity: 0.1;
}

/* 导航栏 */
.app-nav {
    padding: 20px 40px;
    position: relative;
    z-index: 1;
}

.logo {
    display: flex;
    align-items: center;
}

.app-title {
    margin-left: 10px;
    font-size: 20px;
    font-weight: 700;
    color: #334155;
}

/* 内容区 */
.content-wrapper {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40px;
    position: relative;
    z-index: 1;
}

.forgot-password-card {
    background: white;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    width: 100%;
    max-width: 420px;
    padding: 40px;
    position: relative;
    transition: all 0.3s ease;
}

.forgot-password-card:hover {
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
}

.card-header {
    text-align: center;
    margin-bottom: 30px;
}

.card-header h1 {
    font-size: 24px;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 10px;
}

.card-header .subtitle {
    font-size: 14px;
    color: #64748b;
}

/* 步骤指示器 */
.steps-indicator {
    display: flex;
    align-items: center;
    margin-bottom: 40px;
}

.step {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    position: relative;
}

.step-number {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: #e2e8f0;
    color: #64748b;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    margin-bottom: 8px;
    transition: all 0.3s ease;
}

.step-label {
    font-size: 12px;
    color: #94a3b8;
}

.step.active .step-number {
    background-color: #3b82f6;
    color: white;
}

.step.active .step-label {
    color: #3b82f6;
}

.step-line {
    flex: 1;
    height: 2px;
    background-color: #e2e8f0;
    position: relative;
}

.step-line.active::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    background-color: #3b82f6;
    animation: fillLine 0.5s ease forwards;
}

@keyframes fillLine {
    from {
        width: 0;
    }

    to {
        width: 100%;
    }
}

/* 表单样式 */
.form-container {
    transition: all 0.3s ease;
}

.form-step {
    animation: fadeIn 0.5s ease forwards;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.form-group {
    margin-bottom: 24px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-size: 14px;
    font-weight: 500;
    color: #475569;
}

.input-wrapper {
    position: relative;
}

.input-icon {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #94a3b8;
}

input {
    width: 100%;
    padding: 12px 12px 12px 40px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 14px;
    color: #1e293b;
    transition: all 0.3s ease;
}

input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.password-input .toggle-button {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    cursor: pointer;
    color: #94a3b8;
    transition: color 0.3s ease;
}

.password-input .toggle-button:hover {
    color: #3b82f6;
}

.hint {
    font-size: 12px;
    color: #94a3b8;
    margin-top: 6px;
}

/* 密码强度指示器 */
.password-strength {
    margin-top: 12px;
    display: flex;
    flex-direction: column;
}

.strength-label {
    font-size: 12px;
    color: #64748b;
    margin-bottom: 4px;
}

.strength-bar {
    height: 4px;
    border-radius: 2px;
    background-color: #e2e8f0;
    overflow: hidden;
}

.strength-fill {
    height: 100%;
    transition: all 0.3s ease;
}

.strength-text {
    font-size: 12px;
    margin-top: 4px;
    text-align: right;
}

/* 按钮样式 */
.primary-button {
    width: 100%;
    padding: 12px;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.primary-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3);
}

.primary-button:active {
    transform: translateY(0);
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
}

.primary-button:disabled {
    background: #e2e8f0;
    color: #94a3b8;
    cursor: not-allowed;
    box-shadow: none;
}

.back-button {
    margin-top: 24px;
    text-align: center;
}

.back-button button {
    background: none;
    border: none;
    color: #3b82f6;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.back-button button:hover {
    color: #2563eb;
    text-decoration: underline;
}

/* 页脚 */
.app-footer {
    padding: 20px;
    text-align: center;
    font-size: 12px;
    color: #94a3b8;
    position: relative;
    z-index: 1;
}

/* Toast 提示 */
.toast {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 20px;
    border-radius: 8px;
    color: white;
    font-size: 14px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    z-index: 100;
    opacity: 0;
    transform: translateY(-10px);
    transition: all 0.3s ease;
}

.toast.show {
    opacity: 1;
    transform: translateY(0);
}

.toast-success {
    background-color: #10b981;
}

.toast-error {
    background-color: #ef4444;
}

.toast-info {
    background-color: #3b82f6;
}

.toast.fade-out {
    opacity: 0;
    transform: translateY(-10px);
}

/* 响应式设计 */
@media (max-width: 500px) {
    .forgot-password-card {
        padding: 30px;
    }

    .steps-indicator {
        margin-bottom: 30px;
    }

    .step-label {
        display: none;
    }
}
</style>