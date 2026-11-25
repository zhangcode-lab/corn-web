# 农作物叶片检测系统
一个前后端分离的目标检测 Web 应用：**上传图片 → 后端 YOLOv8 推理 → 前端在原图上叠加检测框**，并支持置信度阈值实时调节。
**在线演示**：http://43.139.31.155
> ⚠️ **关于模型权重**：当前使用的是 YOLOv8n 官方 COCO 预训练权重（80 类通用物体），目的是打通端到端链路。**病害专用模型正在用玉米叶片数据集训练中**，所以现阶段传一张叶片图，结果可能为空或误检——这是权重的问题，不是链路的问题。详见下方「已知不足」。
---
## 技术栈
| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite（`<script setup>`，纯 JS 无 TypeScript） |
| 后端 | Python 3 + FastAPI + Uvicorn |
| 模型 | Ultralytics YOLOv8n（CPU 推理） |
| 部署 | Ubuntu 22.04 + Nginx（静态托管 + 反向代理）+ 宝塔面板 |
---
## 架构
```
浏览器
  │  ① GET  /             → Nginx 返回 Vue 打包后的静态文件
  │  ② POST /api/detect   → Nginx 反向代理到 127.0.0.1:8000
  ▼
Nginx (:80)                        /www/wwwroot/crop-ai/web
  ├── /            → 静态文件
  └── /api/*       → proxy_pass http://127.0.0.1:8000
                          ▼
                     FastAPI (uvicorn, 127.0.0.1:8000)
                          ▼
                     YOLOv8n 推理
```
后端**只监听 127.0.0.1**，不直接暴露公网；外部只能看到 80 端口。这样换服务器、加缓存、限流都在 Nginx 层做，后端不需要改。
---
## 接口
```
POST /api/detect?conf=0.25
Content-Type: multipart/form-data
file: <图片文件>
conf: 置信度阈值（可选，默认 0.25）
```
**响应**
```json
{
  "filename": "test.jpg",
  "image_width": 1202,
  "image_height": 676,
  "count": 2,
  "detections": [
    { "name": "person", "confidence": 0.67, "x": 480, "y": 89, "w": 323, "h": 412 }
  ]
}
```
`x / y` 为**左上角**坐标，单位为原图像素。返回 `image_width / image_height` 是为了让前端能做归一化。
接口文档（本地启动后）：`http://127.0.0.1:8000/docs`
---
## 几个实现上的关键点
### 1. 中心点 → 左上角
YOLO 输出的 `xywh` 是 **中心点 + 宽高**，而前端用 `position: absolute` 画框需要 **左上角 + 宽高**：
```python
left = cx - w / 2
top  = cy - h / 2
```
如果直接把 `cx, cy` 当左上角用，框会整体偏右下半个宽高。
### 2. 像素 → 百分比
后端返回像素坐标，前端按百分比定位，这样图片随窗口缩放时，框会跟着缩放而不会错位：
```js
x: (d.x / data.image_width) * 100,
y: (d.y / data.image_height) * 100
```
### 3. 同一份代码适配本地与线上
前端所有请求都写**相对路径** `/api/...`，不写死域名：
- 本地开发：Vite `server.proxy` 把 `/api` 转发到 `http://127.0.0.1:8000`
- 线上部署：Nginx `location /api` 做同样的事
两个环境不需要改任何代码。
### 4. 置信度阈值
阈值通过 query 参数透传到后端，直接改变推理时的 `conf`。界面上拖动滑块即可观察**误检（false positive）与漏检（false negative）的权衡**：
- 阈值调高 → 只保留高置信框，误检少、漏检多
- 阈值调低 → 框变多，漏检少、误检多
---
## 本地运行
前置：Node 18+、Python 3.10+
**前端**
```bash
npm install
npm run dev          # http://localhost:5173
```
**后端**
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
# 接口文档 http://127.0.0.1:8000/docs
```
> `yolov8n.pt`（约 6 MB）未纳入仓库，首次运行会自动从 Ultralytics 下载。国内网络不通时，可手动下载后放入 `backend/` 目录。
---
## 部署
服务器：Ubuntu 22.04 / 2 核 2G / 无 GPU。
**1. 前端**
```bash
npm run build
# 把 dist/ 里的内容上传到 /www/wwwroot/crop-ai/web/
```
**2. 后端常驻**
```bash
cd /www/wwwroot/crop-ai/backend
nohup python3 -m uvicorn app:app --host 127.0.0.1 --port 8000 > app.log 2>&1 &
```
**3. Nginx 反向代理**
站点根目录指向 `web/`，另加：
```nginx
location /api {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```
**资源占用**：模型加载后常驻内存约 600–900 MB。用 `free -h` 看 `Swap used` 是否为 0，可以判断内存是否吃紧。
---
## 已知不足
说实话，这个项目还不够完整：
- **模型权重不是病害专用模型**——当前用 COCO 预训练权重，只用于验证链路
- 没有数据库，检测记录不落库，刷新即丢
- 没有登录、没有限流，任何人都能调用
- 没有自动化测试
- 服务器无 GPU，推理在 CPU 上完成，速度和并发都受限
---
## 后续计划
- [ ] 用玉米叶片数据集微调 YOLO，替换为病害专用权重
- [ ] 检测记录入库（SQLite → MySQL），加历史查询
- [ ] JWT 登录 + 单用户每日限额
- [ ] 基于检测结果生成防治建议（SSE 流式输出）
---
## 目录结构
```
corn-web/
├── src/
│   ├── App.vue          主页面：上传、画框、结果列表、阈值滑块
│   └── main.js
├── backend/
│   ├── app.py           FastAPI：POST /api/detect
│   ├── detect.py        命令行推理脚本（调试用）
│   └── requirements.txt
├── docs/                接口与效果截图
├── index.html
├── vite.config.js       含 /api 开发代理配置
└── package.json
```
---
## 开发记录
2026/10/29 起，共 8 次提交。主要节点：
| 日期 | 内容 |
|---|---|
| 11/14 | 前端界面搭建，假数据画框 |
| 11/18 | 前端接入真实接口，坐标改为百分比换算 |
| 11/18 | 后端并入仓库，Git 忽略大文件 |
| 11/18 | 新增置信度阈值滑块 |
| 11/22 | 部署上线，公网可访问 |
