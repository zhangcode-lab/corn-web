<template>
  <div class="box">
    <h1>玉米病害检测系统</h1>
    <button @click="startDetect">开始检测</button>
    <button @click="reset">重置</button>
    <p v-if="status === '检测中'">⏳ 正在调用 YOLO 模型分析，请稍候...</p>
    <div v-if="status === '成功'" class="result">
      <p>识别结果：叶锈病（置信度：{{ confidence }}%）</p>
      <p>点击次数：{{ clickCount }}</p>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue';
let status = ref('等待'); // 检测状态
let confidence = ref(0); // 置信度
let clickCount = ref(0); // 点击次数
const startDetect = () => {
  status.value = '检测中';
  clickCount.value++;
  // 模拟调用 YOLO 模型进行检测
  setTimeout(() => {
    confidence.value = 96.5; // 模拟置信度
    status.value = '成功';
  }, 1500); // 模拟延迟 
};
const reset = () => {
  status.value = '等待';
  confidence.value = 0;
}
</script>
<style scoped>
.box { text-align: center; margin-top: 50px; font-family: sans-serif; }
button { padding: 10px 20px; margin: 0 10px; background: #42b983; color: white; border: none; border-radius: 5px; cursor: pointer; }
button:hover { background: #3aa876; }
.result { margin-top: 20px; padding: 20px; background: #e8f5e9; border-radius: 8px; display: inline-block; }
</style>