<template>
    <div class="conversation-card" :class="{ 'current-conversation': isCurrentConversation }"
        @mouseenter="hovered = true" @mouseleave="hovered = false"
        @click="loadMessagesToChat(conversation.conversation_id)">
        <!-- 对话图标 -->
        <div class="conversation-content">
            <div class="conversation-name">
                <span v-if="!isEditing" style="font-weight: bold; font-size: 1.1em;">{{ conversation.name || '未命名对话'
                    }}</span>
                <v-text-field v-else v-model="editedName" @keyup.enter="saveName(conversation.conversation_id)"
                    label="对话名称" outlined dense />
            </div>
            <div class="conversation-info">
                <span>最近修改时间: {{ formatDate(conversation.created_at) }}</span>
            </div>
            <div class="conversation-actions">
                <template v-if="!isEditing">
                    <v-btn @click.stop="toggleEdit" size="small" variant="text">
                        编辑对话名称
                    </v-btn>
                    <!-- 添加删除对话按钮 -->
                    <v-btn @click.stop="deleteConversation(conversation.conversation_id)" color="error" size="small"
                        variant="text">
                        删除对话
                    </v-btn>
                </template>
                <template v-else>
                    <v-btn @click.stop="saveName(conversation.conversation_id)" color="primary" size="small"
                        variant="text">
                        确认
                    </v-btn>
                    <v-btn @click.stop="cancelEdit" size="small" variant="text">
                        取消
                    </v-btn>
                </template>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    props: {
        conversation: {
            type: Object,
            required: true
        },
        isEditing: {
            type: Boolean,
            default: false
        },
        isCurrentConversation: {
            type: Boolean,
            default: false
        },
    },
    data() {
        return {
            hovered: false,
            editedName: this.conversation.name || '未命名对话'
        };
    },
    methods: {
        // 切换编辑状态
        toggleEdit() {
            this.$emit('toggle-edit');
            this.editedName = this.conversation.name || '未命名对话';
        },

        // 保存对话名称
        async saveName(conversationId) {
            console.log('Conversation item: save name', conversationId, this.editedName);
            try {
                const response = await fetch(`http://localhost:8000/update_conversation_name?conversation_id=${conversationId}&name=${this.editedName}`);
                if (response.ok) {
                    console.log('Conversation name updated successfully');
                    this.conversation.name = this.editedName; // 更新本地数据
                    // 触发事件通知其他组件对话名称已更新
                    this.$emit('update-conversation-name-chat', { id: conversationId, name: this.editedName });
                    this.$emit('toggle-edit');
                } else {
                    console.error('Failed to update conversation name');
                    throw new Error('Failed to update conversation name');
                }
            } catch (error) {
                console.error('Error updating conversation name:', error);
            }
        },
        // 处理从其他组件传递过来的对话名称更新事件
        handleUpdateConversationName(conversation) {
            console.log('Conversation item: handleUpdateConversationName:', conversation);
            if (conversation.id === this.conversation.conversation_id) {
                this.conversation.name = conversation.name;
                this.editedName = conversation.name;
            }
        },
        // 加载对话到聊天面板
        async loadMessagesToChat(conversationId) {
            try {
                const response = await fetch(`http://localhost:8000/get_messages?conversation_id=${conversationId}`);
                if (response.ok) {
                    const messages = await response.json();
                    const conversationName = this.conversation.name;
                    console.log('Conversation item: load messages to chat', conversationId, conversationName, messages);
                    this.$emit('load-messages-to-chat', conversationId, conversationName, messages);
                } else {
                    console.error('Failed to get messages for conversation', conversationId);
                }
            } catch (error) {
                console.error('Error getting messages for conversation', error);
            }
        },
        // 格式化日期
        formatDate(dateString) {
            const date = new Date(dateString);
            const options = {
                year: 'numeric',
                month: 'numeric',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: undefined // 不显示秒
            };
            return date.toLocaleString(undefined, options);
        },
        // 取消编辑
        cancelEdit() {
            this.$emit('toggle-edit');
        },

        // 更新对话
        deleteConversation(conversationId) {
            if (confirm('确定要删除这个对话吗？')) {
                this.$emit('delete-conversation', conversationId);
            }
        },
    }
};
</script>

<style scoped>
.conversation-card {
    border-top: 1px solid #d0d0d5;
    transition: background-color 0.3s ease;
}

.conversation-card:hover {
    background-color: rgba(0, 0, 0, 0.1);
    /* 鼠标悬停时颜色变深 */
}

.app-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
}

.current-conversation {
    background-color: rgba(0, 0, 0, 0.2);
    /* 颜色深些 */
}

.app-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 20px;
    background-color: #ffffff;
    border-bottom: 1px solid #e0e0e0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    z-index: 10;
    /* 确保导航栏不会收缩 */
    flex-shrink: 0;
}

.logo-section {
    display: flex;
    align-items: center;
    gap: 8px;
}

.app-title {
    font-size: 18px;
    font-weight: 600;
    color: #333;
}

.toolbar {
    display: flex;
    gap: 10px;
}

.toolbar-btn {
    text-transform: none;
    font-size: 14px;
    min-width: 0;
    padding: 0 12px;
}

.main-content {
    display: flex;
    /* 让主内容区域填充剩余空间 */
    flex: 1;
    overflow: hidden;
    position: relative;
}

.panel {
    transition: width 0.3s ease-in-out;
    overflow: hidden;
    position: relative;
    height: 100%;
    min-width: 0;
    /* 关键：允许面板宽度收缩到0 */
}

.panel-collapsed {
    pointer-events: none;
    width: 0 !important;
    /* 确保宽度强制为0 */
    padding: 0 !important;
    /* 移除内边距 */
    border: none !important;
    /* 移除边框 */
}

.history-panel {
    border-right: 1px solid #e0e0e0;
    background-color: #f9f9f9;
}

.chat-panel {
    background-color: #ffffff;
}

.canvas-panel {
    border-left: 1px solid #e0e0e0;
    background-color: #f9f9f9;
}

.conversation-actions {
    display: flex;
    gap: 10px;
    /* 添加按钮之间的间距 */
    margin-top: 10px;
    /* 添加与上方内容的间距 */
}

.custom-btn {
    border-radius: 4px;
    /* 添加圆角 */
    transition: background-color 0.3s ease;
    /* 添加过渡效果 */
}

.custom-btn:hover {
    background-color: rgba(0, 0, 0, 0.05);
    /* 悬停时背景颜色变浅 */
}

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
        border-right: none;
    }
}
</style>