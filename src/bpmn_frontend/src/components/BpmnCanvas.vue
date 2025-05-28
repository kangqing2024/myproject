<template>
  <div class="bpmn-canvas-container">
    <div v-if="isCanvasVisible" id="canvas" class="canvas-wrapper" @dragover="handleDragOver"
      @dragleave="handleDragLeave" @drop="handleDrop" :class="{ 'drag-active': isDragging }">
      <div v-if="isDragging" class="drag-overlay">
        <v-icon icon="mdi-file-upload" size="64px" color="primary" class="mb-2"></v-icon>
        <p class="text-h6">释放以上传 BPMN 文件</p>
      </div>

      <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
        {{ snackbar.text }}
      </v-snackbar>
    </div>

    <input ref="fileInput" type="file" accept=".bpmn" style="display: none" @change="handleFileSelect">
  </div>
</template>

<script>
import BpmnModeler from 'bpmn-js/lib/Modeler';
import 'bpmn-js/dist/assets/diagram-js.css';
import initialDiagram from "../assets/initialDiagram.js";
import 'bpmn-js/dist/assets/bpmn-js.css';
import 'bpmn-js/dist/assets/bpmn-font/css/bpmn-embedded.css';

export default {
  name: 'BpmnCanvas',
  props: {
    bpmnXml: {
      type: String,
      default: ''
    },

  },
  data() {
    return {
      bpmnViewer: null,
      bpmnXml: '',
      snackbar: {
        show: false,
        text: '',
        color: 'success'
      },
      isCanvasVisible: true,
      isDragging: false,
      savedBpmnXml: '',
      process: null // 定义 process 变量
    };
  },

  mounted() {
    console.log('BpmnCanvas : Mounted hook started');
    this.$nextTick(() => {
      try {
        const canvasElement = document.getElementById('canvas');
        if (!canvasElement) {
          console.error('Canvas element not found');
          this.showSnackbar('画布元素未找到，无法初始化 BPMN 查看器', 'error');
          return;
        }
        console.log('BpmnCanvas : canvasElement:', canvasElement);
        this.bpmnViewer = new BpmnModeler({
          container: '#canvas',
        });
        console.log('BpmnCanvas : BPMN Viewer initialized successfully, bpmnViewer:', this.bpmnViewer);
        if (this.bpmnViewer) {
          if (this.bpmnXml) {
            this.importBpmnXml(this.bpmnXml);
          } else {
            this.loadInitialDiagram();
          }
        } else {
          console.error('BpmnViewer failed to initialize');
          this.showSnackbar('BPMN查看器初始化失败', 'error');
        }
      } catch (error) {
        console.error('Error initializing BpmnViewer:', error);
        this.showSnackbar('BPMN查看器初始化失败', 'error');
      }
    });
  },
  beforeUnmount() {
    if (this.bpmnViewer) {
      this.bpmnViewer.destroy();
    }
  },
  watch: {
    // bpmnXml: {
    //   handler(newXml) {
    //     if (newXml) {
    //       this.importBpmnXml(newXml);
    //       this.createBpmnJson();
    //     } else {
    //       this.loadInitialDiagram();
    //     }
    //   }
    // },
    isCanvasVisible: {
      handler(newValue) {
        if (!newValue) {
          this.saveCurrentDiagram();
        } else if (this.savedBpmnXml) {
          this.importBpmnXml(this.savedBpmnXml);
        }
      }
    }
  },
  methods: {
    async loadInitialDiagram() {
      try {
        console.log('BpmnCanvas: Starting to load initial diagram');
        console.log('BpmnCanvas: bpmnViewer:', this.bpmnViewer);
        if (this.bpmnViewer) {
          await this.bpmnViewer.importXML(initialDiagram);
          this.zoomToFit();
          console.log('Initial BPMN diagram loaded');
        } else {
          console.error('BpmnViewer is not initialized');
          this.showSnackbar('BPMN查看器未初始化，无法加载初始图表', 'error');
        }
      } catch (err) {
        console.error('Failed to load initial diagram:', err);
        this.showSnackbar('加载初始图表失败', 'error');
      }
    },

    async importBpmnXml(xmlContent) {
      try {
        console.log('BpmnCanvas: xmlContent:', xmlContent);
        console.log('BpmnCanvas: bpmnViewer:', this.bpmnViewer);
        if (typeof xmlContent === 'string' && this.bpmnViewer) {
          await this.bpmnViewer.importXML(xmlContent);
          this.zoomToFit();
          console.log('BPMN diagram imported successfully');
          this.bpmnXml = xmlContent;
          await this.createBpmnJson();
          this.showSnackbar('BPMN图表导入成功');
        } else {
          if (typeof xmlContent !== 'string') {
            console.error('Invalid BPMN XML content type. Expected string.');
            this.showSnackbar('导入失败，请检查文件格式', 'error');
          } else {
            console.error('BpmnViewer is not initialized');
            this.showSnackbar('BPMN查看器未初始化，无法导入图表', 'error');
          }
        }
      } catch (err) {
        console.error('Failed to import BPMN diagram:', err);
        this.showSnackbar('导入BPMN图表失败', 'error');
      }
    },

    zoomToFit() {
      setTimeout(() => {
        if (this.bpmnViewer) {
          this.bpmnViewer.get('canvas').zoom('fit-viewport');
        }
      }, 100);
    },

    async saveCurrentDiagram() {
      try {
        if (this.bpmnViewer) {
          const { xml } = await this.bpmnViewer.saveXML();
          this.savedBpmnXml = xml;
          console.log('Diagram saved successfully');
        } else {
          console.error('BpmnViewer is not initialized');
          this.showSnackbar('BPMN查看器未初始化，无法保存图表', 'error');
        }
      } catch (err) {
        console.error('Failed to save diagram:', err);
      }
    },

    showSnackbar(text, color = 'success') {
      this.snackbar = { show: true, text, color };
    },

    handleDragOver(event) {
      event.preventDefault();
      this.isDragging = true;
    },

    handleDragLeave() {
      this.isDragging = false;
    },

    async handleDrop(event) {
      event.preventDefault();
      this.isDragging = false;

      const file = event.dataTransfer.files[0];
      if (file && file.name.endsWith('.bpmn')) {
        const reader = new FileReader();
        reader.onload = async (e) => {
          const xmlContent = e.target.result;
          try {
            await this.importBpmnXml(xmlContent);
            this.bpmnXml = xmlContent;
            await this.createBpmnJson();
            this.showSnackbar('文件已成功导入');
          } catch (err) {
            console.error('Failed to import BPMN diagram:', err);
            this.showSnackbar('导入失败，请检查文件格式', 'error');
          }
        };
        reader.readAsText(file);
      }
    },

    async createBpmnJson() {
      try {
        console.log('Starting to create BPMN JSON. Current BPMN XML:', this.bpmnXml);
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
        this.showSnackbar('BPMN JSON 转换成功', 'success');

        // 触发自定义事件，传递 JSON 数据

        this.$emit('bpmn-json-received', this.process);
      } catch (error) {
        console.error('Error creating BPMN JSON:', error);
        this.showSnackbar('转换失败，请稍后再试', 'error');
      }
    },

    async handleBpmnXml(bpmnXmlValue) {
      console.log('BpmnCanvas: handleBpmnXml called with:', bpmnXmlValue);
      if (bpmnXmlValue === '') {
        if (this.bpmnViewer) {
          this.bpmnViewer.destroy();
        }

        this.bpmnViewer = new BpmnModeler({
          container: '#canvas',
        });
        return;
      }

      try {
        console.log('Starting to handle BPMN XML:', bpmnXmlValue);
        const layoutedXml = await this.processDiagram(bpmnXmlValue);
        if (!layoutedXml) {
          throw new Error('Failed to layout the BPMN diagram');
        }

        this.bpmnXml = layoutedXml;
        await this.importBpmnXml(layoutedXml);
        this.showSnackbar('图表布局优化完成');
      } catch (error) {
        console.error('Error handling BPMN XML:', error);
        this.showSnackbar('布局优化失败', 'error');
      }
    },

    async importFile(file) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const xmlContent = e.target.result;
        try {
          await this.importBpmnXml(xmlContent);
          this.bpmnXml = xmlContent;
          await this.createBpmnJson();
          this.showSnackbar('文件已成功导入');
        } catch (err) {
          console.error('Failed to import BPMN diagram:', err);
          this.showSnackbar('导入失败，请检查文件格式', 'error');
        }
      };
      reader.onerror = (e) => {
        console.error('Failed to read file:', e);
        this.showSnackbar('读取文件失败，请检查文件', 'error');
      };
      reader.readAsText(file);
    },

    async handleDrop(event) {
      event.preventDefault();
      this.isDragging = false;

      const file = event.dataTransfer.files[0];
      if (file && file.name.endsWith('.bpmn')) {
        await this.importFile(file);
      }
    },

    async handleFileSelect(event) {
      const file = event.target.files[0];
      if (file && file.name.endsWith('.bpmn')) {
        await this.importFile(file);
      }
    },
    async processDiagram(bpmnDiagram) {
      try {
        const response = await fetch('http://localhost:3001/process-bpmn', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ bpmnXml: bpmnDiagram })
        });

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const { layoutedXml } = await response.json();
        return layoutedXml;
      } catch (error) {
        console.error('Failed to process the diagram:', error);
        return null;
      }
    },

    async downloadBpmnFile(fileType = 'bpmn') {

      try {
        if (fileType === 'bpmn') {
          const { xml } = await this.bpmnViewer.saveXML();
          this.triggerDownload(xml, 'diagram.bpmn', 'text/xml');
        } else if (fileType === 'png') {
          const { svg } = await this.bpmnViewer.saveSVG();
          this.exportAsPNG(svg);
        }
      } catch (error) {
        console.error('Error downloading file:', error);
        this.showSnackbar('下载失败，请稍后再试', 'error');
      }
    },

    triggerDownload(content, filename, contentType) {
      const blob = new Blob([content], { type: contentType });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      window.URL.revokeObjectURL(url);
    },

    exportAsPNG(svgContent) {
      const img = new Image();
      img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgContent)));

      img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);

        canvas.toBlob((blob) => {
          this.triggerDownload(blob, 'diagram.png', 'image/png');
        }, 'image/png');
      };
    },

    openUploadDialog() {
      this.$refs.fileInput.click();
    },

    handleFileSelect(event) {
      const file = event.target.files[0];
      if (file && file.name.endsWith('.bpmn')) {
        const reader = new FileReader();
        reader.onload = async (e) => {
          const xmlContent = e.target.result;
          await this.handleBpmnXml(xmlContent);
        };
        reader.readAsText(file);
      }
    },

    closeCanvas() {
      this.isCanvasVisible = false;
      this.$emit('close-bpmn-canvas');
    },

    onUpload() {
      this.openUploadDialog();
    },
    onDownloadBpmn() {
      this.downloadBpmnFile('bpmn');
    },
    onDownloadPng() {
      this.downloadBpmnFile('png');
    }
  }
};
</script>

<style scoped>
.bpmn-canvas-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #f5f7fa;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: white;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  z-index: 10;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 8px;
}

.btn-hover {
  transition: all 0.2s ease;
}

.btn-hover:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.canvas-wrapper {
  flex: 1;
  margin: 16px;
  border-radius: 8px;
  background-color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  position: relative;
}

.drag-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 123, 255, 0.1);
  border: 2px dashed #007bff;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 20;
}

.drag-active {
  filter: brightness(0.98);
}

@media (max-width: 960px) {
  .toolbar {
    flex-direction: column;
    gap: 10px;
    padding: 10px;
  }

  .toolbar-left,
  .toolbar-right {
    width: 100%;
    justify-content: center;
  }

  .canvas-wrapper {
    margin: 8px;
  }
}
</style>