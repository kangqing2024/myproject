<template>
  <v-select class="model-picker" placeholder="Select model" density="compact" :items="availableModels"
    :modelValue="selectedModel" @update:modelValue="onModelChange" hide-details :list-props="{ density: 'compact' }"
    no-data-text="Please provide API keys" variant="outlined"></v-select>
</template>

<script>
const Models = Object.freeze({
  GPT_4O_MINI: 'gpt-4o-mini',
  GPT_4O: 'gpt-4o',
  O3_MINI: 'o3-mini',
  HAIKU_3_5: 'claude-3-5-haiku-20241022',
  SONNET_3_7: 'claude-3-7-sonnet-20250219',
  GEMINI_2_PRO: 'gemini/gemini-2.0-pro-exp-02-05',
  GEMINI_2_FLASH: 'gemini/gemini-2.0-flash-001',
  LLAMA_3_3_70B:
    'fireworks_ai/accounts/fireworks/models/llama-v3p3-70b-instruct',
  QWEN_2_5_72B: 'fireworks_ai/accounts/fireworks/models/qwen2p5-72b-instruct',
  DEEPSEEK_V3: 'fireworks_ai/accounts/fireworks/models/deepseek-v3',
  DEEPSEEK_R1: 'fireworks_ai/accounts/fireworks/models/deepseek-r1',
});

const Providers = Object.freeze({
  OPENAI: 'openai',
  ANTHROPIC: 'anthropic',
  GOOGLE: 'google',
  FIREWORKS_AI: 'fireworks_ai',
});

export default {
  name: 'ModelPicker',
  data() {
    return {
      selectedModel: '',
      models: [
        {
          value: Models.GPT_4O_MINI,
          title: 'GPT-4o mini',
          provider: Providers.OPENAI,
        },
        { value: Models.GPT_4O, title: 'GPT-4o', provider: Providers.OPENAI },
        {
          value: Models.O3_MINI,
          title: 'o3-mini',
          provider: Providers.OPENAI,
        },
        {
          value: Models.HAIKU_3_5,
          title: 'Claude 3.5 Haiku',
          provider: Providers.ANTHROPIC,
        },
        {
          value: Models.SONNET_3_7,
          title: 'Claude 3.7 Sonnet',
          provider: Providers.ANTHROPIC,
        },
        {
          value: Models.GEMINI_2_FLASH,
          title: 'Gemini 2.0 Flash',
          provider: Providers.GOOGLE,
        },
        {
          value: Models.GEMINI_2_PRO,
          title: 'Gemini 2.0 Pro',
          provider: Providers.GOOGLE,
        },
        {
          value: Models.LLAMA_3_3_70B,
          title: 'Llama 3.3 70B',
          provider: Providers.FIREWORKS_AI,
        },
        {
          value: Models.QWEN_2_5_72B,
          title: 'Qwen 2.5 72B',
          provider: Providers.FIREWORKS_AI,
        },
        {
          value: Models.DEEPSEEK_V3,
          title: 'Deepseek V3',
          provider: Providers.FIREWORKS_AI,
        },
        {
          value: Models.DEEPSEEK_R1,
          title: 'Deepseek R1',
          provider: Providers.FIREWORKS_AI,
        },
      ],
      availableProviders: [],
    };
  },
  computed: {
    availableModels() {
      return this.models.filter((model) =>
        this.availableProviders.includes(model.provider)
      );
    },
  },
  methods: {
    onModelChange(model) {
      console.log('Model changed:', model); // 添加日志
      this.selectedModel = model;
      this.$emit('select-model', model);
    },
    async fetchAvailableProviders() {
      try {
        const response = await fetch(
          'http://localhost:8000/available_providers',
          {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        this.availableProviders = Object.keys(data).filter(
          (provider) => data[provider]
        );

        if (this.availableProviders.includes(Providers.OPENAI)) {
          this.onModelChange(Models.GPT_4O);
        } else if (this.availableProviders.includes(Providers.ANTHROPIC)) {
          this.onModelChange(Models.SONNET_3_7);
        } else if (this.availableProviders.includes(Providers.GOOGLE)) {
          this.onModelChange(Models.GEMINI_2_PRO);
        } else if (this.availableProviders.includes(Providers.FIREWORKS_AI)) {
          this.onModelChange(Models.LLAMA_3_3_70B);
        }
      } catch (error) {
        console.error('Error fetching available providers', error);
      }
    },
  },
  mounted() {
    this.fetchAvailableProviders();
  },
};
</script>

<style scoped>
.model-picker {
  width: 200px;
}
</style>