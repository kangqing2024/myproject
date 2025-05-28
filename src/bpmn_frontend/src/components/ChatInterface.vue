<template>
  <div class="chat-interface">
    <div class="sticky-top">
      <div class="d-flex align-center justify-space-between pa-2 gap-4">
        <div class="d-flex align-center" @click="toggleEditName">
          <template v-if="!isEditingName">
            <span class="app-title">{{ conversationName }}</span>
          </template>
          <template v-else>
            <v-text-field v-model="editedName" @keyup.enter="saveName" @blur="saveName" label="对话名称" outlined dense
              :width="200" />
          </template>
        </div>
        <div class="d-flex align-center">
          <v-tooltip text="创建新对话" location="bottom">
            <template v-slot:activator="{ props }">
              <v-btn v-bind="props" @click="reset" :disabled="isLoading || messages.length === 0" icon="mdi-refresh"
                variant="text" size="medium" color="blue" class="mr-5">
              </v-btn>
            </template>
          </v-tooltip>

          <ModelPicker @select-model="setSelectedModel" />
        </div>
      </div>
    </div>

    <div class="message-container">
      <div v-if="messages.length > 0" class="message-list">
        <MessageCard v-for="(message, index) in messages" :key="index" :role="message.role" :content="message.content"
          @quote-code="onQuoteCode" />

        <v-alert v-if="isLoading" type="info" text="BPMN图生成中..." class="mb-5" />
      </div>

      <div v-if="messages.length === 0">
        <v-alert type="warning" text="目前可支持的元素：开始和结束事件，任务（用户、服务），网关（排他网关、并行网关），序列流" class="mb-3" />
        <v-alert type="info" text="欢迎来到BPMN绘图助手！我可以帮助你理解并创建BPMN流程哦。跟我说说你想绘制怎样的BPMN图吧！" class="mb-3" />
      </div>

      <v-alert v-if="hasError" type="error" text="好像发生了点小故障，请重新尝试对话吧。" class="mb-5 text-body-2" closable
        @click:close="hasError = false" />
    </div>

    <div class="input-area">
      <div class="input-wrapper">
        <v-textarea label="描述你的需求或提出你的建议" v-model="currentInput" :disabled="isLoading" :counter="10000" rows="4"
          @keydown="handleKeyDown" hide-details class="input-textarea" density="comfortable" variant="outlined"
          bg-color="white">
        </v-textarea>
        <v-btn @click="handleMessageSubmit" :disabled="isLoading || !currentInput.trim()" color="primary"
          class="send-button" icon="mdi-send" variant="text" size="small">
        </v-btn>
      </div>
    </div>

    <p class="text-caption text-center mt-2 mb-2">

    </p>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, toRaw, nextTick } from 'vue';
import ModelPicker from './ModelPicker.vue';
import MessageCard from './MessageCard.vue';
import Intent from '../enums/Intent';
import { useRouter } from 'vue-router';

// 确保所有变量在使用前已经声明和初始化
const props = defineProps({
  isDownloadReady: Boolean,
  loadMessagesToChat: Function,
  onBpmnXmlReceived: Function,
  onBpmnJsonReceived: Function,
  onDownload: Function,
  process: {
    type: Object,
    default: null
  },
});


const emit = defineEmits(['bpmn-xml-received', 'show-bpmn-canvas', 'close-bpmn-canvas', 'toggle-history', 'update-conversation-to-history']);

const isLoading = ref(false);
const messages = ref([]);
const currentInput = ref('');
const selectedModel = ref('');
const hasError = ref(false);
const historyIndex = ref(-1);
const userMessages = ref([]);
const isHistoryOpen = ref(false);
const conversations = ref([]);
const isLoggedIn = ref(false);
const tempMessages = ref([]);
const isCanvasVisible = ref(false);
const conversationName = ref('未命名对话');
const isEditingName = ref(false);
const editedName = ref('');
const currentConversation = ref(null);
const isFirstMessage = ref(true);
const isFirstSaveConversation = ref(true);
const conversationId = ref(null);
const userId = ref(null);

const router = useRouter();




const setSelectedModel = (model) => {
  console.log('Type of selected model:', typeof model);
  selectedModel.value = model;
  console.log('Model selected:', selectedModel.value);
};

// 生成对话名称的方法
const generateConversationName = async (messageHistory, process) => {
  try {
    // 准备请求数据
    const payload = {
      message_history: messageHistory.map(item => ({ content: item.content, role: item.role })),
      process: process || null,
      model: selectedModel.value
    };

    // 发送 POST 请求到后端 API
    const response = await fetch('http://localhost:8000/generate_conversation_name', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    // 检查响应状态
    if (response.ok) {
      const data = await response.json();
      return data.conversation_name;
    } else {
      const errorData = await response.json();
      console.error('Failed to generate conversation name:', errorData);
      return null;
    }
  } catch (error) {
    console.error('Error generating conversation name:', error);
    return null;
  }
};

const loadMessagesToChat = (newConversationId, newConversationName, messagesToLoad) => {
  console.log('ChatInterface: Loading messages to chat:', newConversationId, newConversationName, messagesToLoad);
  // 更新 conversationId
  conversationId.value = newConversationId;
  // 更新 conversationName
  conversationName.value = newConversationName;
  // 使用扩展运算符来更新 messages 数组
  messages.value = [];
  messages.value = [...messages.value, ...messagesToLoad];
  console.log('messages:', messages.value);
  currentInput.value = '';
  console.log('currentInput:', currentInput.value);
  historyIndex.value = -1;
  console.log('historyIndex:', historyIndex.value);
  userMessages.value = [];
  console.log('userMessages:', userMessages.value);
  nextTick(() => {
    scrollToBottom();
  });
};




const restoreTempConversation = (userId) => {
  const storedTempMessages = localStorage.getItem('tempMessages');
  if (storedTempMessages) {
    const tempConversation = {
      conversation_id: null,
      created_at: new Date().toISOString(),
      messages: JSON.parse(storedTempMessages)
    };
    conversations.value.push(tempConversation);
    saveTempConversationToServer(userId);
    localStorage.removeItem('tempMessages');
    console.log('Temp conversation restored');
  }
};

const restoreLocalTempMessages = () => {
  const storedTempMessages = localStorage.getItem('tempMessages');
  if (storedTempMessages) {
    tempMessages.value = JSON.parse(storedTempMessages);
    messages.value = [...tempMessages.value];
    console.log('Temp conversation restored');
  }
};


const saveConversation = async (messages, name = "未命名对话") => {
  if (!isLoggedIn.value) {
    console.error('User not logged in, cannot save conversation');
    showSnackbar('请先登录', 'error');
    return false;
  }
  try {
    // 过滤掉无效的消息
    const validMessages = messages.filter(message => message.content && message.role);
    const payload = {
      user_id: userId.value,
      messages: validMessages,
      name: name
    };
    console.log('Saving conversation with payload:', payload);
    const response = await fetch('http://localhost:8000/save_conversation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      const data = await response.json();
      console.log('ChatInterface-saveConversation: Conversation saved successfully:', data);
      conversationId.value = data.conversation_id;
      emit('update-conversation-to-history', conversationId.value);
      showSnackbar('对话已保存', 'success');
      return true;
    } else {
      const errorData = await response.json();
      console.error('Failed to save conversation:', errorData.detail);
      showSnackbar(`保存对话失败: ${errorData.detail}`, 'error');
      return false;
    }
  } catch (error) {
    console.error('Error saving conversation:', error);
    showSnackbar('保存对话时发生错误，请稍后再试', 'error');
    return false;
  }
};
const saveMessages = async (conversationId, messages) => {
  console.log('Saving messages to conversation:', conversationId, messages);
  try {
    // 检查 messages 是否为响应式对象
    const actualMessages = messages.value ? messages.value : messages;

    // 检查 actualMessages 是否为数组且不为空
    if (!Array.isArray(actualMessages) || actualMessages.length === 0) {
      console.error('Invalid messages data:', actualMessages);
      showSnackbar('无效的消息数据，请检查', 'error');
      return;
    }

    const payload = {
      conversation_id: conversationId, // 直接使用 conversationId，因为它可能不是响应式对象
      messages: [actualMessages[actualMessages.length - 1].content],
      role: [actualMessages[actualMessages.length - 1].role]
    };

    const response = await fetch('http://localhost:8000/save_messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      console.log('Messages saved successfully');
    } else {
      const errorData = await response.json();
      console.error('Failed to save messages:', errorData.detail);
      showSnackbar(`保存消息失败: ${errorData.detail}`, 'error');
    }
  } catch (error) {
    console.error('Error saving messages:', error);
    showSnackbar('保存消息时发生错误，请稍后再试', 'error');
  }
};
const onBpmnXmlReceived = (bpmnXml) => {
  emit('bpmn-xml-received', bpmnXml);
  processBpmnXml(bpmnXml);
};

const processBpmnXml = async (bpmnXml) => {
  try {
    const response = await fetch('http://localhost:3001/process-bpmn', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bpmnXml: bpmnXml }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Processed BPMN data:', data);
  } catch (error) {
    console.error('Error processing BPMN XML:', error);
    hasError.value = true;
    showSnackbar('处理BPMN XML时发生错误', 'error');
  }
};

const handleKeyDown = (event) => {
  if (event.shiftKey && event.key === 'Enter') {
    event.preventDefault();
    const cursorPosition = event.target.selectionStart;
    const textBeforeCursor = currentInput.value.slice(0, cursorPosition);
    const textAfterCursor = currentInput.value.slice(cursorPosition);
    currentInput.value = textBeforeCursor + '\n' + textAfterCursor;

    nextTick(() => {
      event.target.selectionStart = event.target.selectionEnd = cursorPosition + 1;
    });
  } else if (event.key === 'Enter') {
    event.preventDefault();
    handleMessageSubmit();
  } else if (event.key === 'ArrowUp') {
    event.preventDefault();
    if (currentInput.value === '') {
      if (userMessages.value.length === 0) {
        userMessages.value = messages.value.filter(message => message.role === 'user').map(message => message.content);
      }
      if (historyIndex.value < userMessages.value.length - 1) {
        historyIndex.value++;
        currentInput.value = userMessages.value[userMessages.value.length - 1 - historyIndex.value];
      }
    }
  } else if (event.key === 'ArrowDown') {
    event.preventDefault();
    if (currentInput.value !== '' && historyIndex.value > 0) {
      historyIndex.value--;
      currentInput.value = userMessages.value[userMessages.value.length - 1 - historyIndex.value];
    } else if (currentInput.value !== '' && historyIndex.value === 0) {
      currentInput.value = '';
      historyIndex.value = -1;
    }
  }
};

const onQuoteCode = (jsonCode) => {
  currentInput.value = jsonCode;
};

const scrollToBottom = () => {
  const messageContainer = document.querySelector('.message-container');
  if (messageContainer) {
    messageContainer.scrollTop = messageContainer.scrollHeight;
  }
};



const handleMessageSubmit = async () => {
  console.log('Submitting message:', currentInput.value);
  if (!currentInput.value.trim()) {
    showSnackbar('请输入消息内容', 'warning');
    return;
  }

  if (!selectedModel.value) {
    showSnackbar('请先选择一个模型！', 'warning');
    return;
  }

  if (currentInput.value.length > 999999) {
    showSnackbar('消息太长，请简短一些', 'warning');
    return;
  }

  // 修改：使用 props.process 确保使用从父组件传递过来的 process 数据
  console.log('process data1:', props.process);
  // Clear any previous errors
  hasError.value = false;
  console.log('hasError:', hasError.value)
  messages.value.push({ content: currentInput.value, role: 'user' });
  console.log('messages:', messages.value);
  currentInput.value = '';
  console.log('currentInput:', currentInput.value);
  historyIndex.value = -1;
  console.log('historyIndex:', historyIndex.value);
  userMessages.value = [];
  console.log('userMessages:', userMessages.value);

  if (isLoggedIn.value) {
    if (!conversationId.value) {
      // 新对话，调用 saveConversation
      const saved = await saveConversation(messages.value, conversationName.value);
      if (saved) {
        console.log('ChatInterface-handleMessageSubmit: Conversation saved successfully');
      } else {
        showSnackbar('保存对话失败，请稍后再试', 'error');
      }
    } else {
      // 已有 conversationId，调用 saveMessages
      const saveResult = await saveMessages(conversationId.value, [messages.value[messages.value.length - 1]]);
      if (saveResult) {
        console.log('ChatInterface-handleMessageSubmit: user Message saved successfully');
      } else {
        showSnackbar('保存assistant消息失败，请稍后再试', 'error');
      }
    }
  } else {
    tempMessages.value.push({ content: currentInput.value, role: 'user' });
    localStorage.setItem('tempMessages', JSON.stringify(tempMessages.value));
    console.log('ChatInterface: Temp conversation saved');
  }

  nextTick(() => {
    scrollToBottom();
  });

  // 修改：使用 props.process 确保使用从父组件传递过来的 process 数据
  console.log('process data2:', props.process);
  const intent = await determineIntent();

  switch (intent) {
    case Intent.TALK:
      await talk(props.process, selectedModel.value, false);
      nextTick(() => {
        scrollToBottom();
      });
      break;
    case Intent.MODIFY:
      isLoading.value = true;
      emit('show-bpmn-canvas');
      const result = await modify(props.process, selectedModel.value);
      if (result.bpmnXml && result.bpmnJson) {
        console.log('ChatInterface: BPMN XML:', result.bpmnXml);
        console.log('ChatInterface: BPMN JSON:', result.bpmnJson);

        // 将 BPMN XML 数据传递给父组件
        emit('bpmn-xml-received', result.bpmnXml);

        isLoading.value = false;
        await talk(result.bpmnJson, selectedModel.value, true);
        nextTick(() => {
          scrollToBottom();
        });

      } else {
        console.error('Failed to get valid BPMN data from modify request.');
      }
      break;
    default:
      console.error('Unknown intent:', intent);
  }
};


const handleBpmnJson = async (bpmnJson) => {
  // 假设 selectedModel 已经正确设置
  if (!selectedModel.value) {
    showSnackbar('请先选择一个模型！', 'warning');
    return;
  }

  // 调用 talk 方法
  await talk(bpmnJson, selectedModel.value, true);
  nextTick(() => {
    scrollToBottom();
  });
};




const determineIntent = async () => {
  try {
    const payload = {
      message_history: toRaw(messages.value),
      model: selectedModel.value,
    };
    console.log('determine_intent payload:', payload);
    const response = await fetch('http://localhost:8000/determine_intent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    console.log('determine_intent response:', data);
    if (!Object.values(Intent).includes(data.intent)) {
      throw new Error(`Unknown intent: ${data.intent}`);
    }

    return data.intent;
  } catch (error) {
    console.error('Error determining intent:', error);
    hasError.value = true;
    throw error;
  }
};

const talk = async (process, selectedModel, needsToBeFinalComment) => {
  if (!process) {
    console.error('Process data is not provided in talk method.');
    hasError.value = true;
    showSnackbar('Process 数据未提供，请检查', 'error');
    return;
  }
  try {
    // 确保 message_history 是正确的格式
    const validMessageHistory = toRaw(messages.value).map(message => {
      if (!message.content || !message.role) {
        console.error('Invalid message in message_history:', message);
        return null;
      }
      return message;
    }).filter(message => message !== null);

    // 确保 process 是列表
    let validProcess = process;
    if (process && !Array.isArray(process)) {
      console.error('Process data is not a list, trying to convert:', process);
      validProcess = [];
    }

    const payload = {
      message_history: validMessageHistory,
      process: validProcess,
      model: selectedModel,
      needs_to_be_final_comment: needsToBeFinalComment,
    };

    const response = await fetch('http://localhost:8000/talk', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error(`HTTP error! Status: ${response.status}, Error data:`, errorData);
      hasError.value = true;
      throw new Error(`Server error: ${JSON.stringify(errorData.detail)}`);
    }

    // 处理流式响应
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');

    const updateOrAddLastMessage = (newText) => {
      if (
        messages.value.length > 0 &&
        messages.value[messages.value.length - 1].role === 'assistant'
      ) {
        const lastMessage = messages.value[messages.value.length - 1];
        lastMessage.content = (lastMessage.content || '') + newText;
      } else {
        messages.value.push({ content: newText, role: 'assistant' });
      }
    };

    const processText = async ({ done, value }) => {
      if (done) {
        console.log('Stream complete');

        // 流式响应结束后保存消息
        if (conversationId.value) {
          await saveMessages(conversationId.value, [messages.value[messages.value.length - 1]]);
        } else {
          showSnackbar('对话 ID 无效，无法保存消息', 'error');
        }

        // 首次生成对话名称
        // if (isFirstMessage.value) {
        //   console.log('First message, generating conversation name');
        //   const generatedName = await generateConversationName(messages.value, null);
        //   if (generatedName) {
        //     conversationName.value = generatedName;
        //     console.log('Generated conversation name:', conversationName.value);
        //   }
        //   isFirstMessage.value = false;
        // }

        return;
      }

      const replyMessage = decoder.decode(value, { stream: true });
      updateOrAddLastMessage(replyMessage);
      return reader.read().then(processText);
    };
    await reader.read().then(processText);

  } catch (error) {
    console.error('Error responding to user query:', error);
    hasError.value = true;
    throw error;
  }
};


const modify = async (process, selectedModel) => {
  try {
    // 确保 process 是列表
    let validProcess = process;
    if (process && !Array.isArray(process)) {
      console.error('Process data is not a list, trying to convert:', process);
      // 这里可以根据实际情况进行转换，暂时设为空列表
      validProcess = [];
    }

    // 确保 model 是字符串类型
    let modelValue = typeof selectedModel === 'object' && selectedModel.value ? selectedModel.value : selectedModel;
    if (typeof modelValue !== 'string') {
      console.error('Model data is not a string, trying to convert:', modelValue);
      modelValue = String(modelValue);
    }

    const payload = {
      message_history: toRaw(messages.value),
      process: validProcess,
      model: modelValue
    };
    console.log('modify process data:', validProcess);
    const response = await fetch('http://localhost:8000/modify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    console.log('modify response:', response);

    if (!response.ok) {
      const errorData = await response.json();
      console.error(`HTTP error! Status: ${response.status}, Error data:`, errorData);
      isLoading.value = false;
      hasError.value = true;
      throw new Error(`Server error: ${JSON.stringify(errorData.detail)}`);
    }

    const data = await response.json();
    console.log('Modified BPMN data:', data);

    return {
      bpmnXml: data.bpmn_xml,
      bpmnJson: data.bpmn_json
    };
  } catch (error) {
    console.error('Error modifying BPMN:', error);
    isLoading.value = false;
    hasError.value = true;
    return { bpmnXml: null, bpmnJson: null }; // 返回默认值，避免解构赋值错误
  }
};

const toggleHistory = () => {
  // 原代码逻辑
};

const showSnackbar = (text, color = 'success') => {
  console.log(`[${color}] ${text}`);
  // 这里可以添加一个全局的通知组件
};


const toggleEditName = () => {
  isEditingName.value = true;
  if (isEditingName.value) {
    editedName.value = conversationName.value;
  }
};

// 保存对话名称
const saveName = async () => {
  console.log('chatinterface-saveName: Conversation ID:', conversationId.value, 'New name:', editedName.value);
  if (!conversationId.value) {
    conversationName.value = editedName.value;
    return;
  } else {
    try {
      const encodedName = encodeURIComponent(editedName.value);
      const validConversationId = String(conversationId.value);
      const response = await fetch(`http://localhost:8000/update_conversation_name?conversation_id=${validConversationId}&name=${encodedName}`);
      if (response.ok) {
        console.log('Conversation name updated successfully');
        conversationName.value = editedName.value;
        isEditingName.value = false;
        // 触发事件通知父组件对话名称已更新
        emit('update-conversation-name', { id: conversationId.value, name: conversationName.value });
      } else {
        console.error('Failed to update conversation name');
        throw new Error('Failed to update conversation name');
      }
    } catch (error) {
      console.error('Error updating conversation name:', error);
    }
  }
};
// 处理从其他组件传递过来的对话名称更新事件
const handleUpdateConversationName = (conversation) => {
  console.log('chatinterface-handleUpdateConversationName: Conversation:', conversation);
  if (conversation.id === conversationId.value) {
    conversationName.value = conversation.name;
  }
};

const reset = () => {
  messages.value = [];
  currentInput.value = '';
  historyIndex.value = -1;
  userMessages.value = [];
  conversationName.value = '未命名对话';
  isFirstMessage.value = true;
  conversationId.value = null;
  isEditingName.value = false;
  editedName.value = '';
};

onMounted(() => {
  //获取用户id
  const userInfo = JSON.parse(sessionStorage.getItem('user_info'));
  if (userInfo) {
    isLoggedIn.value = true;
    userId.value = userInfo.id;
  }
  window.addEventListener('beforeunload', beforeUnloadHandler);
});

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', beforeUnloadHandler);
});


const saveTempConversationToServer = async (userId) => {
  const storedTempMessages = localStorage.getItem('tempMessages');
  saveConversation(JSON.parse(storedTempMessages), '临时对话');
  saveMessages(conversationId.value, JSON.parse(storedTempMessages));
  localStorage.removeItem('tempMessages');
  console.log('Temp conversation saved to server');
};

const beforeUnloadHandler = (event) => {
  if (!isLoggedIn.value && tempMessages.value.length > 0) {
    const confirmation = confirm('你有未保存的对话，是否登录/注册保存这些对话？');
    if (confirmation) {
      router.push('/login');
      event.preventDefault();
      // 登录成功后保存临时对话
      const userInfo = JSON.parse(sessionStorage.getItem('user_info'));
      if (userInfo) {
        saveTempConversationToServer(userInfo.id);
      }
    } else {
      tempMessages.value = [];
      localStorage.removeItem('tempMessages');
    }
  }
};

defineExpose({
  loadMessagesToChat,
  onBpmnXmlReceived,
  handleBpmnJson,
  handleUpdateConversationName,
});
</script>



<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500&display=swap');

.chat-interface {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  /* 调整高度，减去导航栏的高度 */
  max-width: 600px;
  margin: 0 auto;
  position: relative;
  /* 添加相对定位 */
  z-index: 1;
  /* 调整 z-index，确保在合适的层级 */
}

.sticky-top {
  position: sticky;
  top: 0;
  background-color: white;
  z-index: 1;
  padding: 4px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}

.message-container {
  flex-grow: 1;
  overflow-y: auto;
  padding: 16px;
}

.message-list {
  display: flex;
  flex-direction: column;
}

.input-area {
  position: sticky;
  bottom: 0;
  background-color: white;
  z-index: 2;
  /* 确保发送按钮在其他元素之上 */
}
</style>