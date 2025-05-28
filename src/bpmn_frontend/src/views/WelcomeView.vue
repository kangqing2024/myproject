<template>
    <div class="welcome-page">
        <!-- 背景装饰 -->
        <div class="bg-decoration top-left"></div>
        <div class="bg-decoration bottom-right"></div>
        <div class="bg-decoration center"></div>

        <!-- 顶部导航 -->
        <nav class="app-nav">
            <div class="logo">
                <v-icon icon="mdi-chart-timeline-variant" color="primary" size="24px" />
                <span class="app-title">BPMN绘图助手</span>
            </div>
            <div class="nav-links">
                <router-link to="/login" class="nav-link">登录</router-link>
                <router-link to="/register" class="nav-link">注册</router-link>
            </div>
        </nav>

        <!-- 内容容器 -->
        <div class="content-container">
            <div class="hero-section">
                <v-icon icon="mdi-chart-timeline-variant" color="primary" size="96px" class="mb-6"></v-icon>
                <h1 class="title">BPMN绘图助手</h1>
                <p class="subtitle">专业的业务流程建模工具</p>
                <p class="description">
                    通过直观的拖放界面，快速创建、编辑和共享符合BPMN 2.0标准的业务流程图。
                    无论是业务分析师、开发人员还是项目经理，都能从中受益。
                </p>
            </div>

            <div class="features-container">
                <div class="feature">
                    <v-icon icon="mdi-pencil-ruler" color="primary" size="36px"></v-icon>
                    <h3>直观的拖放编辑</h3>
                    <p>通过简单的拖放操作创建专业的BPMN流程图，无需复杂培训。</p>
                </div>
                <div class="feature">
                    <v-icon icon="mdi-shape" color="primary" size="36px"></v-icon>
                    <h3>丰富的元素库</h3>
                    <p>包含所有BPMN 2.0标准元素，满足各种业务场景的建模需求。</p>
                </div>
                <div class="feature">
                    <v-icon icon="mdi-cloud-sync" color="primary" size="36px"></v-icon>
                    <h3>AI辅助生成</h3>
                    <p>利用AI技术自动生成流程图，提升工作效率。</p>
                </div>
            </div>

            <div class="button-container">
                <v-btn @click="goToLogin" color="primary" class="login-button" elevation="4">
                    登录
                </v-btn>
                <v-btn @click="goToHome" color="secondary" class="guest-button" elevation="4">
                    游客快速访问
                </v-btn>
            </div>
        </div>


    </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

// 跳转到登录界面
const goToLogin = () => {
    router.push('/login');
};

// 游客访问主页
const goToHome = () => {
    router.push('/home');
};
</script>

<style scoped>
.welcome-page {
    position: relative;
    display: flex;
    flex-direction: column;
    height: 100vh;
    text-align: center;
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
    overflow: hidden;
}

.bg-decoration {
    position: absolute;
    width: 500px;
    height: 500px;
    border-radius: 50%;
    filter: blur(80px);
    z-index: 0;
}

.top-left {
    top: -250px;
    left: -250px;
    background: rgba(0, 123, 255, 0.15);
}

.bottom-right {
    bottom: -250px;
    right: -250px;
    background: rgba(72, 187, 120, 0.15);
}

.center {
    top: 30%;
    right: -100px;
    width: 300px;
    height: 300px;
    background: rgba(139, 92, 246, 0.1);
}

.app-nav {
    padding: 20px 40px;
    position: relative;
    z-index: 1;
    display: flex;
    justify-content: space-between;
    align-items: center;
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

.nav-links {
    display: flex;
    gap: 20px;
}

.nav-link {
    text-decoration: none;
    color: #334155;
    font-weight: 500;
    transition: color 0.3s ease;
}

.nav-link:hover {
    color: #007bff;
}

.content-container {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 900px;
    margin: auto;
    padding: 40px;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.hero-section {
    margin-bottom: 60px;
}

.title {
    font-size: 36px;
    font-weight: 700;
    color: #334155;
    margin-bottom: 16px;
}

.subtitle {
    font-size: 18px;
    color: #64748b;
    max-width: 600px;
    margin: 0 auto 24px;
}

.description {
    font-size: 16px;
    color: #64748b;
    max-width: 700px;
    margin: 0 auto;
    line-height: 1.6;
}

.features-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 30px;
    margin-bottom: 60px;
    width: 100%;
}

.feature {
    background-color: white;
    border-radius: 16px;
    padding: 30px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
    transition: transform 0.3s ease;
    height: 100%;
}

.feature:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.feature h3 {
    font-size: 20px;
    font-weight: 600;
    color: #334155;
    margin: 16px 0;
}

.feature p {
    color: #64748b;
    line-height: 1.5;
}

.button-container {
    display: flex;
    justify-content: center;
    gap: 24px;
}

.login-button,
.guest-button {
    min-width: 180px;
    font-size: 16px;
    font-weight: 500;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.login-button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.login-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3);
}

.guest-button {
    background: linear-gradient(135deg, #56c3bf 0%, #4faca9 100%);
    color: #334155;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.guest-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3);
}

.app-footer {
    padding: 20px;
    text-align: center;
    font-size: 14px;
    color: #94a3b8;
    position: relative;
    z-index: 1;
}

@media (max-width: 768px) {
    .features-container {
        grid-template-columns: 1fr;
        gap: 20px;
    }

    .title {
        font-size: 28px;
    }

    .subtitle {
        font-size: 16px;
    }

    .description {
        font-size: 14px;
    }

    .button-container {
        flex-direction: column;
        gap: 16px;
        align-items: center;
        width: 100%;
    }

    .login-button,
    .guest-button {
        width: 100%;
    }

    .app-nav {
        padding: 20px;
    }
}
</style>