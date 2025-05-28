<template>
    <div class="register-container">
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
            <div class="register-card">
                <div class="card-header">
                    <h1>创建您的账户</h1>
                    <p class="subtitle">请填写以下信息完成注册</p>
                </div>

                <!-- 步骤指示器 -->
                <div class="steps-indicator">
                    <div class="step active">
                        <div class="step-number">1</div>
                        <span class="step-label">填写信息</span>
                    </div>
                    <div class="step-line" :class="{ active: step >= 2 }"></div>
                    <div class="step" :class="{ active: step >= 2 }">
                        <div class="step-number">2</div>
                        <span class="step-label">完成注册</span>
                    </div>
                </div>

                <!-- 表单容器 -->
                <div class="form-container">
                    <!-- 注册表单 -->
                    <div class="form-step" v-show="step === 1">
                        <div class="form-group">
                            <label for="username">用户名:</label>
                            <div class="input-wrapper">
                                <v-icon icon="mdi-account" class="input-icon" />
                                <input type="text" id="username" v-model="username" required placeholder="请设置您的用户名">
                                <span v-if="!isUsernameValid && username.length > 0"
                                    class="error-message">用户名不能包含特殊字符</span>
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="password">密码:</label>
                            <div class="input-wrapper password-input">
                                <v-icon icon="mdi-lock" class="input-icon" />
                                <input :type="passwordVisible ? 'text' : 'password'" id="password" v-model="password"
                                    required placeholder="请设置您的密码">
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
                            <label for="account">账号(邮箱或手机号):</label>
                            <div class="input-wrapper">
                                <v-icon :icon="isEmail(account) ? 'mdi-email' : 'mdi-phone'" class="input-icon" />
                                <input type="text" id="account" v-model="account" required placeholder="请输入邮箱或手机号">
                                <span v-if="!isAccountValid && account.length > 0"
                                    class="error-message">请输入有效的邮箱或手机号</span>
                            </div>
                        </div>

                        <div class="form-group">
                            <div class="flex-container">
                                <div class="input-wrapper flex-grow">
                                    <v-icon icon="mdi-shield-key" class="input-icon" />
                                    <input type="text" id="verification_code" v-model="verification_code" required
                                        placeholder="请输入验证码">
                                </div>
                                <button @click.prevent="sendVerificationCode" :disabled="isSendingCode || countdown > 0"
                                    class="primary-button">
                                    {{ countdown > 0 ? `${countdown}s后重试` : '获取验证码' }}
                                </button>
                            </div>
                        </div>

                        <button type="button" @click="register" class="primary-button" :disabled="!isFormValid">
                            完成注册
                        </button>
                    </div>
                </div>

                <!-- 已有账号提示 -->
                <div class="login-link">
                    已有账号? <router-link to="/login">立即登录</router-link>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const username = ref('');
const password = ref('');
const account = ref('');
const verification_code = ref('');
const isSendingCode = ref(false);
const countdown = ref(0);
const passwordVisible = ref(false);
const step = ref(1); // 1:填写信息, 2:完成注册

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

// 验证用户名是否有效（不包含特殊字符）
const isUsernameValid = computed(() => {
    const usernameRegex = /^[a-zA-Z0-9]+$/;
    return usernameRegex.test(username.value);
});

// 验证账号是否有效（邮箱或手机号）
const isAccountValid = computed(() => {
    return isEmail(account.value) || isPhoneNumber(account.value);
});

// 切换密码可见性
const togglePasswordVisibility = () => {
    passwordVisible.value = !passwordVisible.value;
};

// 获取密码强度
const passwordStrength = computed(() => {
    if (!password.value) return 0;
    let strength = 0;

    // 长度评分（最高 40%）
    strength += Math.min(password.value.length / 12 * 40, 40);

    // 字符多样性评分（最高 60%）
    const hasLower = /[a-z]/.test(password.value);
    const hasUpper = /[A-Z]/.test(password.value);
    const hasNumber = /[0-9]/.test(password.value);
    const hasSpecial = /[^A-Za-z0-9]/.test(password.value);
    const diversity = [hasLower, hasUpper, hasNumber, hasSpecial].filter(Boolean).length;
    strength += (diversity / 4) * 60;

    return Math.min(strength, 100);
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

// 表单有效性检查
const isFormValid = computed(() => {
    return username.value.length > 0 &&
        isUsernameValid.value &&
        password.value.length >= 8 &&
        passwordStrength.value >= 50 &&
        isAccountValid.value &&
        verification_code.value.length > 0;
});

const sendVerificationCode = async () => {
    if (!isAccountValid.value) {
        showToast('请输入有效的邮箱或手机号', 'error');
        return;
    }

    isSendingCode.value = true;
    countdown.value = 60;

    const intervalId = setInterval(() => {
        countdown.value--;
        if (countdown.value <= 0) {
            clearInterval(intervalId);
            isSendingCode.value = false;
        }
    }, 1000);

    let url = '';
    let data = {};
    if (isEmail(account.value)) {
        url = 'http://localhost:8000/api/send_email_verification_code';
        data = { email: account.value };
    } else if (isPhoneNumber(account.value)) {
        url = 'http://localhost:8000/api/send_phone_verification_code';
        data = { phone_number: account.value };
    }

    try {
        const response = await axios.post(url, data);
        showToast(response.data.message, 'success');
    } catch (error) {
        if (error.response) {
            showToast(`发送验证码失败: ${error.response.data.detail}`, 'error');
        } else {
            showToast(`发送验证码失败: ${error.message}`, 'error');
        }
        console.error('发送验证码出错:', error);
        isSendingCode.value = false;
        countdown.value = 0;
    }
};

// 显示通知
const showToast = (message, type = 'info') => {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
        toast.classList.add('fade-out');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
};

const register = async () => {
    if (!isFormValid.value) {
        showToast('请填写完整并符合要求的信息', 'error');
        return;
    }

    let url = '';
    let data = {};
    if (isEmail(account.value)) {
        url = 'http://localhost:8000/api/register_by_email';
        data = {
            username: username.value,
            password: password.value,
            email: account.value,
            verification_code: verification_code.value
        };
    } else if (isPhoneNumber(account.value)) {
        url = 'http://localhost:8000/api/register_by_phone';
        data = {
            username: username.value,
            password: password.value,
            phone_number: account.value,
            verification_code: verification_code.value
        };
    }

    try {
        const response = await axios.post(url, data);
        if (response.status === 200) {
            showToast('注册成功，请登录', 'success');
            // 延迟跳转，让用户有时间看到成功提示
            setTimeout(() => {
                router.push('/login');
            }, 1500);
        } else if (response.data.detail) {
            showToast(response.data.detail, 'error');
        } else {
            showToast('注册失败，请重试', 'error');
        }
    } catch (error) {
        console.error('注册出错:', error);
        showToast('注册出错，请稍后再试', 'error');
    }
};
</script>

<style scoped>
/* 基础样式 */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: 'Inter', sans-serif;
}

.register-container {
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

.register-card {
    background: white;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    width: 100%;
    max-width: 420px;
    padding: 40px;
    position: relative;
    transition: all 0.3s ease;
}

.register-card:hover {
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

/* 已有账号提示 */
.login-link {
    margin-top: 24px;
    text-align: center;
    color: #64748b;
    font-size: 14px;
}

.login-link a {
    color: #007bff;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s ease;
}

.login-link a:hover {
    color: #0056b3;
    text-decoration: underline;
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

/* 错误消息样式 */
.error-message {
    color: #ef4444;
    font-size: 12px;
    margin-top: 4px;
}

/* 响应式设计 */
@media (max-width: 500px) {
    .register-card {
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