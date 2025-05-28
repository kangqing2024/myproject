<template>
    <div class="history-conversations-container">
        <!-- 历史对话标题 -->
        <h2>历史对话</h2>
        <!-- 历史对话卡片容器，添加滚动条 -->
        <div class="conversation-cards-container">
            <!-- 使用 transition-group 组件添加过渡效果 -->
            <transition-group name="conversation-card-transition" tag="div">
                <ConversationItem ref="conversationItem" v-for="(conversation, index) in sortedConversations"
                    :key="conversation.id" :conversation="conversation" :isEditing="isEditing[index]"
                    @toggle-edit="toggleEdit(index)" @save-name="saveName($event, index)"
                    @update-conversation-name-chat="handleUpdateConversationNametoChat($event, index)"
                    @load-messages-to-chat="loadMessagesToChat"
                    @load-conversations-to-History="loadConversationsToHistory($event)"
                    @update-conversation="updateConversation($event, index)"
                    @delete-conversation="deleteConversation($event, index)"
                    :isCurrentConversation="conversation === currentConversation" />
            </transition-group>
        </div>
    </div>
</template>

<script>
import ConversationItem from './ConversationItem.vue';

export default {
    components: {
        ConversationItem
    },
    props: {
        isOpen: Boolean,
        conversations: Array,
        currentConversation: Object,
        loadMessagesToChat: {
            type: Function,
            default: () => { }
        },
        loadConversationsToHistory: {
            type: Function,
            default: () => { }
        }
    },
    data() {
        return {
            isEditing: [],
            editedName: []
        };
    },
    computed: {
        sortedConversations() {
            const validConversations = this.conversations.filter(conversation => {
                return conversation;
            });
            const sorted = validConversations.slice().sort((a, b) => {
                return new Date(b.created_at) - new Date(a.created_at);
            });
            sorted.forEach(conversation => {
                console.log('Conversation object:', conversation);
            });
            console.log('Sorted conversations:', sorted); // 输出排序结果
            return sorted;
        }
    },
    methods: {

        closeHistory() {
            this.$emit('close');
        },
        toggleEdit(index) {
            this.isEditing[index] = !this.isEditing[index];
        },
        loadMessagesToChat(conversationId, name, messages) {
            console.log('History conversation :Loading messages for conversation:', conversationId, name, messages);
            if (conversationId) {
                // 调用父组件传递的 loadMessagesToChat 方法，同时传递对话 ID、名称和消息
                this.$props.loadMessagesToChat(conversationId, name, messages);
            } else {
                console.error('Conversation not found with ID:', conversationId);
            }
        },
        loadConversationsToHistory(messages) {
            console.log('History conversation :Loaded messages:', messages);
            // 调用父组件传递的 loadConversationsToHistory 方法
            this.$props.loadConversationsToHistory(messages);
        },
        updateConversation(conversation, index) {
            this.conversations[index] = conversation;
        },
        updateConversationToHistory(conversationId) {
            // 根据 conversationId 获取最新的对话信息
            this.loadConversationsToHistory().then(() => {
                const newConversation = this.conversations.find(con => con.id === conversationId);
                if (newConversation) {
                    // 更新 conversations 数组
                    const index = this.conversations.findIndex(con => con.id === conversationId);
                    if (index !== -1) {
                        this.conversations.splice(index, 1, newConversation);
                    } else {
                        this.conversations.push(newConversation);
                    }
                }
            });
        },
        handleUpdateConversationName(conversationId, name) {
            console.log('History conversation :handleUpdateConversationName:', conversationId, name);
            const index = this.conversations.findIndex(con => con.id === conversationId);
            if (index !== -1) {
                this.conversations[index].name = name; // 更新本地数据
            }
        },
        handleUpdateConversationNametoChat(event, index) {
            console.log('History conversation :handleUpdateConversationNametoChat:', event);
            const { id, name } = event;
            const conversation = this.conversations.find(con => con.id === id);
            if (conversation) {
                conversation.name = name; // 更新本地数据
                this.editedName[index] = name; // 更新本地数据
                this.$emit('update-conversation-name-chat', event); // 转发给父组件 
                this.$forceUpdate(); // 强制重新渲染组件
            }
        },
        saveName(event, index) {
            const { id, name } = event;
            const conversation = this.conversations.find(con => con.id === id);
            if (conversation) {
                conversation.name = name; // 更新本地数据
            }
        },
        showSnackbar(text, color = 'success') {
            // 这里可以添加一个全局的通知组件
            console.log(`[${color}] ${text}`);
        },
        async deleteConversation(conversationId, index) {
            console.log('Deleting conversation with ID:', conversationId, 'at index:', index);
            if (index < 0 || index >= this.conversations.length) {
                console.error('Invalid index for deletion:', index);
                this.showSnackbar('删除对话时索引无效', 'error');
                return;
            }
            try {
                const response = await fetch(`http://localhost:8000/delete_conversation?conversation_id=${conversationId}`, {
                    method: 'DELETE'
                });
                if (response.ok) {
                    console.log('Conversation deleted successfully');
                    // 直接在原数组上删除元素
                    this.conversations.splice(index, 1);
                    alert('对话已删除');
                    this.showSnackbar('对话已删除', 'success');
                } else {
                    console.error('Failed to delete conversation');
                    throw new Error('Failed to delete conversation');
                }
            } catch (error) {
                console.error('Error deleting conversation:', error);
                alert('删除对话失败');
                this.showSnackbar('删除对话失败', 'error');
            }
        },

    },
};
</script>

<style scoped>
.history-conversations-container {
    position: relative;
    width: 100%;
    left: 0;
    max-width: 300px;
    height: calc(100vh - 60px);
    background-color: white;
    box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
    padding: 20px;
    z-index: 1;
    display: flex;
    flex-direction: column;
}

.app-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.5rem;
    font-weight: 500;
    letter-spacing: 0.5px;
    background: linear-gradient(45deg, var(--v-primary-base), #666);
    margin-bottom: 0;
}

.conversation-cards-container {
    flex-grow: 1;
    overflow-y: auto;
    margin-top: 10px;
}

.conversation-card {
    margin-bottom: 20px;
}

.v-btn {
    margin-right: 5px;
}


/* 过渡效果样式 */
.history-conversations-container .conversation-card-transition-enter-active,
.history-conversations-container .conversation-card-transition-leave-active {
    transition: all 0.3s ease;
}

.history-conversations-container .conversation-card-transition-enter,
.history-conversations-container .conversation-card-transition-leave-to {
    opacity: 0;
    transform: translateY(-20px);
}
</style>