<template>
  <div class="mb-3 mx-2">
    <v-card :style="{ backgroundColor: getBackgroundColor() }" class="text-black">
      <v-card-subtitle class="mt-2">
        <b>{{ roleDisplay }}</b>
      </v-card-subtitle>
      <v-card-text class="card-text">
        <!-- 渲染普通文本内容 -->
        <span v-html="formattedTextContent"></span>
        <!-- 渲染 JSON 代码内容 -->
        <div v-if="hasJsonContent" class="code-block">
          <div class="code-header">
            <v-tooltip :text="isCodeVisible ? '折叠代码' : '展开代码'" location="bottom">
              <template v-slot:activator="{ props }">
                <span v-bind="props" @click="toggleCodeVisibility">
                  {{ codeLanguage }}
                  <v-icon :icon="isCodeVisible ? 'mdi-chevron-down' : 'mdi-chevron-up'"></v-icon>
                </span>
              </template>
            </v-tooltip>
            <!-- 添加容器包裹复制和引用按钮 -->
            <div class="button-container">
              <v-tooltip :text="copyJsonText" location="bottom">
                <template v-slot:activator="{ props }">
                  <!-- 添加唯一类名 -->
                  <v-btn v-bind="props" @click="copyCode" :icon="copyJsonIcon" size="small" variant="text"
                    class="copy-code-btn"></v-btn>
                </template>
              </v-tooltip>
              <!-- 添加引用按钮 -->
              <v-tooltip text="引用JSON代码" location="bottom">
                <template v-slot:activator="{ props }">
                  <v-btn v-bind="props" @click="onQuoteCode" icon="mdi-format-quote-close-outline" size="small"
                    variant="text"></v-btn>
                </template>
              </v-tooltip>
            </div>
          </div>
          <pre v-if="isCodeVisible" class="json-pre"><code class="language-json">{{ formattedJsonContent }}</code></pre>
        </div>
        <!-- 添加复制和引用按钮到对话框右下角 -->
        <div class="bottom-button-container">
          <v-tooltip :text="copyAllContentText" location="bottom">
            <template v-slot:activator="{ props }">
              <v-btn v-bind="props" @click="copyWholeContent" :icon="copyAllIcon" size="small" variant="text"
                class="copy-all-btn"></v-btn>
            </template>
          </v-tooltip>
          <v-tooltip text="引用全部内容" location="bottom">
            <template v-slot:activator="{ props }">
              <v-btn v-bind="props" @click="quoteWholeContent" icon="mdi-format-quote-close-outline" size="small"
                variant="text"></v-btn>
            </template>
          </v-tooltip>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import hljs from 'highlight.js';
import ClipboardJS from 'clipboard';

export default {
  props: {
    role: String,
    content: String,
    jsonContent: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      clipboardCode: null,
      clipboardAll: null,
      isCodeVisible: true,
      codeLanguage: 'json',
      copyJsonText: '复制代码',
      copyAllContentText: '复制全部内容',
      copyJsonIcon: 'mdi-content-copy',
      copyAllIcon: 'mdi-content-copy',
      timer: null
    };
  },
  computed: {
    roleDisplay() {
      return this.role === 'user' ? '你' : 'BPMN绘图助手';
    },
    formattedTextContent() {
      return this.content
        .replace(/```json([\s\S]*?)```/g, '')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n- /g, '<br>• ')
        .replace(/\n/g, '<br>');
    },
    hasJsonContent() {
      return /```json([\s\S]*?)```/.test(this.content);
    },
    formattedJsonContent() {
      const match = this.content.match(/```json([\s\S]*?)```/);
      if (match) {
        try {
          const json = JSON.parse(match[1].trim());
          return JSON.stringify(json, null, 2);
        } catch (error) {
          return match[1].trim();
        }
      }
      return '';
    },
    plainJsonContent() {
      const match = this.content.match(/```json([\s\S]*?)```/);
      if (match) {
        try {
          const json = JSON.parse(match[1].trim());
          return JSON.stringify(json, null, 2);
        } catch (error) {
          return match[1].trim();
        }
      }
      return '';
    }
  },
  methods: {
    getBackgroundColor() {
      return this.role === 'user'
        ? 'rgba(0, 100, 255, 0.1)'
        : 'rgba(255, 0, 0, 0.1)';
    },
    copyCode() {
      if (!this.clipboardCode) {
        this.clipboardCode = new ClipboardJS(this.$el.querySelector('.copy-code-btn'), {
          text: () => this.plainJsonContent
        });
        this.clipboardCode.on('success', (e) => {
          this.copyJsonText = '已复制';
          this.copyJsonIcon = 'mdi-check';
          if (this.timer) {
            clearTimeout(this.timer);
          }
          this.timer = setTimeout(() => {
            this.copyJsonText = '复制代码';
            this.copyJsonIcon = 'mdi-content-copy';
          }, 2000);
          e.clearSelection();
        });
        this.clipboardCode.on('error', (e) => {
          console.error('复制代码失败', e);
        });
      }
      this.clipboardCode.onClick({ currentTarget: this.$el.querySelector('.copy-code-btn') });
    },
    toggleCodeVisibility() {
      this.isCodeVisible = !this.isCodeVisible;
    },
    onQuoteCode() {
      if (this.hasJsonContent) {
        this.$emit('quote-code', this.plainJsonContent);
      }
    },
    copyWholeContent() {
      if (!this.clipboardAll) {
        this.clipboardAll = new ClipboardJS(this.$el.querySelector('.copy-all-btn'), {
          text: () => this.content
        });
        this.clipboardAll.on('success', (e) => {
          this.copyAllContentText = '已复制';
          this.copyAllIcon = 'mdi-check';
          if (this.timer) {
            clearTimeout(this.timer);
          }
          this.timer = setTimeout(() => {
            this.copyAllContentText = '复制全部内容';
            this.copyAllIcon = 'mdi-content-copy';
          }, 2000);
          e.clearSelection();
        });
        this.clipboardAll.on('error', (e) => {
          console.error('复制全部内容失败', e);
        });
      }
      this.clipboardAll.onClick({ currentTarget: this.$el.querySelector('.copy-all-btn') });
    },
    quoteWholeContent() {
      this.$emit('quote-code', this.content);
    }
  },
  mounted() {
    const jsonCodeBlocks = this.$el.querySelectorAll('.language-json');
    jsonCodeBlocks.forEach((block) => {
      hljs.highlightElement(block);
    });

    this.clipboardCode = new ClipboardJS(this.$el.querySelector('.copy-code-btn'), {
      text: () => this.plainJsonContent
    });
  },
  beforeDestroy() {
    if (this.clipboardCode) {
      this.clipboardCode.destroy();
    }
    if (this.clipboardAll) {
      this.clipboardAll.destroy();
    }
    if (this.timer) {
      clearTimeout(this.timer);
    }
  },
};
</script>

<style scoped>
.card-text {
  padding: 5px 15px 10px;
}

.code-block {
  margin-top: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f4f4f4;
  padding: 5px 10px;
  cursor: pointer;
}

.button-container {
  display: flex;
}

.code-header v-btn {
  margin-left: 10px;
}

.json-pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  font-family: 'Courier New', Courier, monospace;
  padding: 10px;
  background-color: #f9f9f9;
}

.bottom-button-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 5px;
}

.bottom-button-container v-btn {
  margin-left: 10px;
}
</style>