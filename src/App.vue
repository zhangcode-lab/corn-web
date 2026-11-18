<script setup>
// ==========================================================
// 这是一个"最小可懂版本"
// 目标：用最少的代码，完成「上传图 → 点按钮 → 出现假红框」
// 每一行你都要能说出它在干嘛。说不出的地方，问我。
// 注意：这里故意不用 Element Plus，全部用原生 HTML
// ==========================================================

import { ref, computed } from 'vue'
import axios from 'axios'   
console.log('======= 页面打开了 =======');
// ---------- 第 1 块：状态（就是几个"盒子"）----------

// photoUrl：当前图片在浏览器里的临时地址。没选图时是 null
const photoUrl = ref(null)
// fileName：文件名，只用来显示给用户看
const fileName = ref('')
// loading：是否正在检测。改它会自动改变按钮文字
const loading = ref(false)
// boxes：检测框列表。一开始是空数组 = 一个框都不画
const boxes = ref([])
const fileobj = ref(null)
const confValue = ref(0.25)  // 置信度阈值，默认 0.25
// ---------- 第 2 块：假数据 ----------
// 真实情况：这些数据由第 2 周的 Python 后端算出来返回
// 现在先写死，目的是先验证「前端能不能把框画出来」
// x / y / w / h 都是百分比，相对于图片自己算
const FAKE_RESULT = [
  { name: '叶锈病', confidence: 0.95, x: 78, y: 28, w: 26, h: 22 },
  { name: '叶斑病', confidence: 0.78, x: 58, y: 55, w: 18, h: 16 }
]

// ---------- 第 3 块：动作（用户点了才跑的函数）----------

// 用户选了文件就进这里
function onFileChange(event) {
  const file = event.target.files[0]
  if (!file) return

  fileName.value = file.name
  // URL.createObjectURL 把本地文件变成一个浏览器能显示的地址
  photoUrl.value = URL.createObjectURL(file)
  console.log('图片地址是：',photoUrl.value);// 换图了，把上次的框清掉
  boxes.value = []
  fileobj.value = file
}

// 用户点了"开始检测"就进这里

async function startDetect() {
  if (!photoUrl.value || !fileobj.value) return
console.log('按钮被点了，当前状态：',loading.value,'框的数量：',boxes.value.length);
  loading.value = true
  boxes.value = []
  const form = new FormData()  
          // 把图片打包成 FormData
  form.append('file', fileobj.value)// 这里的 'file' 是后端接收的字段名，fileobj.value 是用户选的文件对象
try{
  const res =await axios.post('http://127.0.0.1:8000/api/detect?conf='+confValue.value,form)// 发送 POST 请求到后端，传图片过去
  console.log('后端返回了：',res.status);
  const data = res.data
  boxes.value = data.detections.map((d) => ({
    name: d.name,
    confidence: d.confidence,
    x: (d.x/data.image_width)*100,
    y: (d.y/data.image_height)*100,
    w: (d.w/data.image_width)*100,
    h: (d.h/data.image_height)*100,
  }))
}catch(e){
  alert('请求失败：'+e.message)
}finally{
  loading.value = false
}
}

// ---------- 第 4 块：派生数据（算出来的，不是手动改的）----------

// 把 box 的百分比数字，翻译成 CSS 能用的样式
function boxStyle(box) {
  return {
    left: box.x + '%',
    top: box.y + '%',
    width: box.w + '%',
    height: box.h + '%'
  }
}

// 有结果了吗？有就显示列表，没有就显示提示
const hasResult = computed(() => boxes.value.length > 0)
</script>

<template>
  <div class="page">
    <h1>病害检测系统</h1>

    <div class="main">
      <!-- ===== 左栏：图片 + 检测 ===== -->
      <div class="panel">
        <label class="upload">
          选择图片
          <input type="file" accept="image/*" @change="onFileChange" hidden />
        </label>
        <p class="hint">{{ fileName || '还没有选择图片' }}</p>

        <!-- stage 是个"照片框"，红框都画在它里面 -->
        <div class="stage">
          <!-- v-if：photoUrl 有值才显示图片 -->
          <img v-if="photoUrl" :src="photoUrl" class="photo" alt="待检测图片" />
          <div v-else class="empty">图片会显示在这里</div>

          <!-- v-for：boxes 里有几个对象，就画几个框 -->
          <div v-for="(box, i) in boxes" :key="i" class="box" :style="boxStyle(box)">
            <span class="tag">{{ box.name }} {{ (box.confidence * 100).toFixed(0) }}%</span>
          </div>
        </div>

        <!-- :disabled 的意思是：这两个条件有一个成立，按钮就点不动 -->
        <button class="btn" :disabled="!photoUrl || loading" @click="startDetect">
          {{ loading ? '检测中...' : '开始检测' }}
        </button>
        <div style="margin-top: 12px">
          <label>置信度阈值：{{ confValue.toFixed(2) }}</label>
          <input type="range" min="0.05" max="0.95" step="0.05" v-model.number="confValue" style="width: 100%" />
        </div>
      </div>

      <!-- ===== 右栏：结果列表 ===== -->
      <div class="panel">
        <h2>检测结果</h2>
        <p v-if="!hasResult" class="hint">点击"开始检测"后显示</p>
        <ul v-else class="list">
          <li v-for="(box, i) in boxes" :key="i">
            <b>{{ box.name }}</b>
            <span>置信度 {{ (box.confidence * 100).toFixed(0) }}%</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px 16px 40px;
  font-family: system-ui, -apple-system, 'Microsoft YaHei', sans-serif;
  color: #222;
}
h1 {
  font-size: 22px;
  margin: 0 0 20px;
}
h2 {
  font-size: 16px;
  margin: 0 0 12px;
}
.main {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  flex-wrap: wrap;
}
.panel {
  flex: 1 1 320px;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
}

/* 上传按钮其实就是个漂亮的 label */
.upload {
  display: inline-block;
  padding: 8px 16px;
  background: #1677ff;
  color: #fff;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}
.upload:hover {
  background: #0e5fd8;
}

.hint {
  font-size: 13px;
  color: #888;
  margin: 8px 0 12px;
  word-break: break-all;
}

/* 关键：stage 用 relative，里面的红框用 absolute 就能跟着它定位 */
.stage {
  position: relative;
  display: inline-block;
  max-width: 100%;
  min-height: 180px;
  vertical-align: top;
  border: 1px dashed #ddd;
  border-radius: 6px;
  overflow: visible;
}
.photo {
  display: block;
  max-width: 100%;
  border-radius: 6px;
}
.empty {
  width: 320px;
  height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #bbb;
  font-size: 13px;
}

/* 红框本体：位置和大小全靠 inline style 里的百分比 */
.box {
  position: absolute;
  border: 2px solid #ff4d4f;
  box-sizing: border-box;
  pointer-events: none;
}
.tag {
  position: absolute;
  top: 0;
  left: 0;
  transform: translateY(-100%);
  background: #ff4d4f;
  color: #fff;
  font-size: 12px;
  line-height: 1.6;
  padding: 0 4px;
  white-space: nowrap;
  border-radius: 2px 2px 0 0;
}

.btn {
  display: block;
  margin-top: 16px;
  width: 100%;
  padding: 10px;
  font-size: 15px;
  border: none;
  border-radius: 6px;
  background: #1677ff;
  color: #fff;
  cursor: pointer;
}
.btn:disabled {
  background: #bfbfbf;
  cursor: not-allowed;
}

.list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.list li {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}
.list li:last-child {
  border-bottom: none;
}
.list span {
  color: #888;
}
</style>