<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <div class="app-header">
      <div class="logo-section">
        <v-icon icon="mdi-chart-timeline-variant" color="primary" size="24px" />
        <span class="app-title">BPMN绘图助手</span>
      </div>
      <div class="toolbar">
        <v-btn @click="toggleHistory" class="toolbar-btn">
          <v-icon icon="mdi-history" />
          <span v-if="showHistory">隐藏历史</span>
          <span v-else>显示历史</span>
        </v-btn>
        <v-btn @click="showCanvas ? closeBpmnCanvas() : showBpmnCanvas()" class="toolbar-btn">
          <v-icon icon="mdi-drawing" />
          <span v-if="showCanvas">隐藏画布</span>
          <span v-else>显示画布</span>
        </v-btn>
        <!-- 新增按钮 -->
        <v-tooltip text="上传BPMN文件" location="bottom">
          <template v-slot:activator="{ props }">
            <v-btn v-bind="props" @click="onUpload" icon="mdi-upload" variant="outlined" color="primary"
              class="toolbar-btn">
            </v-btn>
          </template>
        </v-tooltip>
        <v-tooltip text="下载BPMN文件" location="bottom">
          <template v-slot:activator="{ props }">
            <v-btn v-bind="props" @click="onDownloadBpmn" icon="mdi-download" variant="outlined" color="primary"
              class="toolbar-btn">
            </v-btn>
          </template>
        </v-tooltip>
        <v-tooltip text="保存为PNG图片" location="bottom">
          <template v-slot:activator="{ props }">
            <v-btn v-bind="props" @click="onDownloadPng" icon="mdi-image" variant="outlined" color="primary"
              class="toolbar-btn">
            </v-btn>
          </template>
        </v-tooltip>
        <v-btn @click="goToUserInfo" color="primary" class="toolbar-btn">查看用户信息</v-btn>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 历史对话面板 -->
      <div class="panel history-panel" :class="{ 'panel-collapsed': !showHistory }" :style="{ width: historyWidth }">
        <HistoryConversations ref="historyConversations" @save-name="handleSaveName" :isOpen="showHistory"
          @update-conversation-name-chat="handleUpdateConversationNameToChat" :conversations="conversations"
          :currentConversation="currentConversation" :loadMessagesToChat="loadMessagesToChat"
          :loadConversationsToHistory="loadConversationsToHistory" />
      </div>

      <!-- 聊天界面 -->
      <div class="panel chat-panel" :style="{ width: chatWidth }">
        <ChatInterface ref="chatInterface" @show-bpmn-canvas="showBpmnCanvas" @bpmn-xml-received="handleBpmnXmlReceived"
          @update-conversation-to-history="updateConversationToHistory" @save-name="handleSaveName"
          @update-conversation-name="handleUpdateConversationNameToHistory" :isDownloadReady="isDownloadReady"
          :loadMessagesToChat="loadMessagesToChat" :onBpmnXmlReceived="onBpmnXmlReceived" :onDownload="onDownload"
          :process="process" />

      </div>

      <!-- BPMN 画布 -->
      <div class="panel canvas-panel" :class="{ 'panel-collapsed': !showCanvas }" :style="{ width: canvasWidth }">
        <BpmnCanvas ref="bpmnCanvas" :isDownloadReady="isDownloadReady" :bpmnXml="bpmnXml" @bpmn-loaded="onBpmnLoaded"
          @show-bpmn-canvas="showBpmnCanvas" @bpmn-json-received="handleBpmnJsonReceived" @dragover.prevent
          @drop="handleDrop" />
      </div>
    </div>

    <!-- 通知提示 -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </div>
</template>

<script>
import ChatInterface from '../components/ChatInterface.vue';
import BpmnCanvas from '../components/BpmnCanvas.vue';
import HistoryConversations from '../components/HistoryConversations.vue';
import { useRouter } from 'vue-router';
import { ref, onMounted, onBeforeUnmount, watch, toRaw, nextTick } from 'vue';

export default {
  name: 'HomeView',
  components: {
    ChatInterface,
    BpmnCanvas,
    HistoryConversations
  },
  data() {
    return {
      bpmnXml: '',
      isLoadingConversation: false, // 添加标志
      process: {
        type: Object,
        default: null
      },
      conversation: {
        id: 1,
        name: '默认对话名称',
        // 其他属性
      },
      showCanvas: false,
      showHistory: true,
      snackbar: {
        show: false,
        text: '',
        color: 'success'
      },
      conversations: [],
      // 响应式面板宽度配置
      panelConfig: {
        history: {
          baseWidth: '300px',
          minWidth: '280px',
          maxWidth: '400px'
        },
        chat: {
          baseWidth: '40%',
          minWidth: '320px'
        },
        canvas: {
          baseWidth: '50%',
          minWidth: '400px'
        },
        currentConversation: null,
      },
      windowWidth: window.innerWidth
    };
  },
  setup() {
    const router = useRouter();
    const goToUserInfo = () => {
      router.push('/user-info');
    };
    return {
      goToUserInfo
    };
  },
  computed: {
    // 计算各面板宽度
    historyWidth() {
      if (this.windowWidth < 768) {
        return this.showHistory ? '100%' : '0';
      }
      return this.showHistory ? this.panelConfig.history.baseWidth : '0';
    },
    chatWidth() {
      if (this.windowWidth < 768) {
        return '100%';
      }

      let width = '100%';
      if (this.showHistory && this.showCanvas) {
        width = `calc(100% - ${this.panelConfig.history.baseWidth} - ${this.panelConfig.canvas.baseWidth})`;
      } else if (this.showHistory) {
        width = `calc(100% - ${this.panelConfig.history.baseWidth})`;
      } else if (this.showCanvas) {
        width = `calc(100% - ${this.panelConfig.canvas.baseWidth})`;
      }

      return width;
    },
    canvasWidth() {
      if (this.windowWidth < 768) {
        return this.showCanvas ? '100%' : '0';
      }
      return this.showCanvas ? this.panelConfig.canvas.baseWidth : '0';
    }
  },

  async created() {
    this.loadConversationsToHistory();
    // 添加窗口大小变化监听
    window.addEventListener('resize', this.handleResize);
  },

  beforeDestroy() {
    // 移除窗口大小变化监听
    window.removeEventListener('resize', this.handleResize);
  },

  watch: {
    bpmnXml: {
      handler(newXml) {
        if (newXml) {
          this.importBpmnXml(newXml);
        }
      }
    },
    showCanvas: {
      handler(newValue) {
        if (!newValue) {
          // 关闭画板时保存 BPMN XML 数据
          if (this.$refs.bpmnCanvas && this.$refs.bpmnCanvas.bpmnViewer) {
            this.$refs.bpmnCanvas.bpmnViewer.saveXML().then(({ xml }) => {
              this.savedBpmnXml = xml;
            });
          }
        } else {
          // 打开画板时恢复 BPMN XML 数据
          if (this.savedBpmnXml) {
            if (this.$refs.bpmnCanvas) {
              this.$refs.bpmnCanvas.importBpmnXml(this.savedBpmnXml);
            }
          }
        }
      },
      currentConversation: {
        immediate: false,
        handler(newValue, oldValue) {
          // 处理 currentConversation 更新逻辑
          if (newValue !== oldValue && !this.isLoadingConversation) {
            // 这里可以添加其他逻辑
          }
        }
      }
    },
  },

  methods: {
    handleBpmnJsonReceived(bpmnJson) {
      console.log('HomeView-BPMN JSON received:', bpmnJson);
      // 将 JSON 数据传递给 ChatInterface.vue
      this.$nextTick(() => {
        this.$refs.chatInterface.handleBpmnJson(bpmnJson);
      });
    },
    async handleBpmnXmlReceived(bpmnXml) {
      try {
        // 模拟异步操作
        await new Promise(resolve => setTimeout(resolve, 1000));
        console.log('HomeView-BPMN XML received:', bpmnXml);
        // 然后再加载 BPMN XML 到画板
        if (this.$refs.bpmnCanvas) {
          await this.$refs.bpmnCanvas.handleBpmnXml(bpmnXml);
        }
      } catch (error) {
        console.error('Error handling BPMN XML received:', error);
      }
    },

    showBpmnCanvas() {
      this.showCanvas = true;
      this.$nextTick(() => {
        // 重新加载 BPMN 图
        if (this.$refs.bpmnCanvas) {
          this.$refs.bpmnCanvas.handleBpmnXml(this.bpmnXml);
        }
      });
    },
    handleResize() {
      this.windowWidth = window.innerWidth;
    },
    async handleDrop(event) {
      event.preventDefault(); // Prevent the browser from default file handling
      if (event.dataTransfer.items) {
        for (let i = 0; i < event.dataTransfer.items.length; i++) {
          if (event.dataTransfer.items[i].kind === 'file') {
            const file = event.dataTransfer.items[i].getAsFile();

            if (file.name.endsWith('.bpmn')) {
              if (this.$refs.bpmnCanvas) {
                await this.$refs.bpmnCanvas.importFile(file);
              }
            }
          }
        }
      }
    },

    async loadMessagesToChat(conversationId, name, messages) {
      if (this.isLoadingConversation) return; // 如果正在加载对话，直接返回
      this.isLoadingConversation = true; // 设置标志为正在加载对话
      console.log('HomeView: loadMessagesToChat : ', conversationId, name, messages);
      await this.$nextTick(() => {
        if (this.$refs.chatInterface) {
          if (typeof this.$refs.chatInterface.loadMessagesToChat === 'function') {
            // 传递对话 ID、名称和消息给 ChatInterface 组件
            this.$refs.chatInterface.loadMessagesToChat(conversationId, name, messages);
          } else {
            console.error('loadMessagesToChat is not a function');
          }
        } else {
          console.error('ChatInterface ref is not available.');
        }
      });
      // 更新 currentConversation
      const conversation = this.conversations.find(con => con.id === conversationId);
      this.currentConversation = conversation;
      this.isLoadingConversation = false; // 加载对话完成，重置标志
    },
    async loadConversationsToHistory(messages) {
      // 处理加载对话到历史记录的逻辑
      const userInfo = sessionStorage.getItem('user_info');
      let user_id = null;
      if (userInfo) {
        try {
          const parsedUserInfo = JSON.parse(userInfo);
          if (parsedUserInfo.id) {
            user_id = parsedUserInfo.id;
            try {
              const response = await fetch(`http://localhost:8000/get_conversations?user_id=${user_id}`);
              if (response.ok) {
                this.conversations = await response.json();
                console.log('HomeView-Conversations successfully loaded');
              } else {
                console.error('Failed to get conversations');
              }
            } catch (error) {
              console.error('Error getting conversations:', error);
            }
          }
        } catch (error) {
          console.error('Error parsing user info:', error);
        }
      }
      console.log('HomeView: Load conversations to history', messages);
    },

    showSnackbar(text, color = 'success') {
      this.snackbar.text = text;
      this.snackbar.color = color;
      this.snackbar.show = true;
    },

    async handleBpmnXml(bpmnXmlValue) {
      this.bpmnXml = bpmnXmlValue;
      this.createBpmnJson();
    },

    setBpmnJson(value) {
      console.log('HomeView-BPMN JSON received:', value);
      this.process = value;
    },

    onBpmnLoaded(xmlContent) {
      this.bpmnXml = xmlContent;
      this.createBpmnJson();
    },

    async createBpmnJson() {
      try {
        const response = await fetch('http://localhost:8000/bpmn_to_json', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ bpmn_xml: this.bpmnXml })
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        this.process = await response.json();
        console.log('BPMN JSON created successfully:', this.process);
        this.showSnackbar('加载 BPMN 文件成功。', 'success');
      } catch (error) {
        console.error('Error creating BPMN JSON:', error);
        this.showSnackbar(
          '加载 BPMN 文件失败，请检查文件格式或联系管理员。',
          'error'
        );
      }
    },

    toggleHistory() {
      this.showHistory = !this.showHistory;
    },

    closeBpmnCanvas() {
      this.showCanvas = false;
    },
    // 新增方法调用 BpmnCanvas 的方法
    onUpload() {
      this.showBpmnCanvas();
      if (this.$refs.bpmnCanvas) {
        this.$refs.bpmnCanvas.onUpload();
      }
    },
    onDownloadBpmn() {
      if (this.$refs.bpmnCanvas) {
        this.$refs.bpmnCanvas.onDownloadBpmn();
      }
    },
    onDownloadPng() {
      if (this.$refs.bpmnCanvas) {
        this.$refs.bpmnCanvas.onDownloadPng();
      }
    },
    updateConversationToHistory(conversationId) {
      this.$refs.historyConversations.updateConversationToHistory(conversationId);
    },
    handleSaveName({ id, name }) {
      const conversation = this.conversations.find(con => con.id === id);
      if (conversation) {
        conversation.name = name; // 更新本地对话名称
        this.$refs.historyConversations.updateConversationToHistory(id); // 更新历史对话组件中的数据
      }
    },

    handleUpdateConversationNameToHistory(conversation) {
      console.log('HomeView-handleUpdateConversationNameToHistory:', conversation);
      if (this.$refs.historyConversations) {
        this.$refs.historyConversations.handleUpdateConversationName(conversation.id, conversation.name);
      }
    },
    handleUpdateConversationNameToChat(conversation) {
      console.log('HomeView-handleUpdateConversationNameToChat:', conversation);
      if (this.$refs.chatInterface) {
        this.$refs.chatInterface.handleUpdateConversationName(conversation);
      }
    },
    onBpmnXmlReceived(xmlContent) {
      this.bpmnXml = xmlContent;
      this.createBpmnJson();
    },
    onDownload(type) {
      if (this.$refs.bpmnCanvas) {
        this.$refs.bpmnCanvas.onDownload(type);
      }
    }
  }
};
</script>

<style scoped>
/* 整体容器 */
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  margin: 0;
  padding: 0;
  overflow: hidden;
  box-sizing: border-box;
}

/* 顶部导航栏 */
.app-header {
  height: 60px;
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background-color: #ffffff;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  z-index: 100;
  /* 确保导航栏在最顶层 */
  position: relative;
}

/* 导航栏 logo 部分 */
.logo-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 应用标题 */
.app-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

/* 工具栏 */
.toolbar {
  display: flex;
  gap: 10px;
}

/* 工具栏按钮 */
.toolbar-btn {
  text-transform: none;
  font-size: 14px;
  min-width: 0;
  padding: 0 12px;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  height: calc(100vh - 60px);
  min-height: calc(100vh - 60px);
  /* 双重保障 */
  display: flex;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
}

/* 面板通用样式 */
.panel {
  transition: width 0.3s ease-in-out;
  overflow: hidden;
  position: relative;
  height: 100%;
  /* 填充主内容区域高度 */
  min-width: 0;
  /* 允许面板宽度收缩到0 */
}

/* 折叠面板样式 */
.panel-collapsed {
  pointer-events: none;
  width: 0 !important;
  /* 确保宽度强制为0 */
  padding: 0 !important;
  /* 移除内边距 */
  border: none !important;
  /* 移除边框 */
}

/* 历史对话面板 */
.history-panel {
  border-right: 1px solid #e0e0e0;
  background-color: #f9f9f9;
  z-index: 2;
}

/* 聊天界面面板 */
.chat-panel {
  background-color: #ffffff;
  z-index: 1;
}

/* BPMN 画布面板 */
.canvas-panel {
  border-left: 1px solid #e0e0e0;
  background-color: #f9f9f9;
  z-index: 2;
}

/* 小屏幕响应式样式 */
@media (max-width: 768px) {
  .panel {
    transition: transform 0.3s ease-in-out, width 0.3s ease-in-out;
    transform: translateX(0);
  }

  .panel-collapsed {
    transform: translateX(-100%);
    width: 0 !important;
  }

  .history-panel {
    z-index: 6;
  }

  .canvas-panel {
    z-index: 6;
  }
}
</style>