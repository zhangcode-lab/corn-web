import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from ultralytics import YOLO

app = FastAPI(title="农作物病害检测 API")
# 允许浏览器跨域访问 —— 第 3 周前端联调必须靠它，不然报 CORS 错误
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
model = YOLO("yolov8n.pt")
CONF = 0.25
# ============================================================
# 核心逻辑
# ============================================================
def detect_image(image: Image.Image):
    """吃一张 PIL 图片，吐出 (检测结果列表, 宽, 高)"""
    results = model(image, conf=CONF, verbose=False)
    boxes = results[0].boxes
    h_img, w_img = results[0].orig_shape
    out = []
    for box in boxes:
        cls_id = int(box.cls.item())
        confidence = round(float(box.conf.item()), 2)
        # xywh 给的是【中心点 x, 中心点 y, 宽, 高】
        cx, cy, w, h = box.xywh[0].tolist()
        out.append({
            "name": model.names[cls_id],
            "confidence": confidence,
            # 前端要的是左上角，所以减掉半个宽高
            "x": int(cx - w / 2),
            "y": int(cy - h / 2),
            "w": int(w),
            "h": int(h),
        })
    return out, w_img, h_img
# ============================================================
# C. 两个接口
# ============================================================
@app.get("/")
def read_root():
    return {"message": "服务在跑，去 /docs 试试"}
@app.post("/api/detect")
async def api_detect(file: UploadFile = File(...)):
    # 1. 把上传的文件读进内存
    data = await file.read()
    # 2. 转成图片。如果传的不是图片，要给它一个友好的错误
    try:
        image = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="这不是一张能识别的图片")
    # 3. 推理
    detections, w_img, h_img = detect_image(image)
    # 4. 按前端约定的格式返回
    return {
        "filename": file.filename,
        "image_width": w_img,     # 第 3 周要用它把像素换算成百分比
        "image_height": h_img,
        "count": len(detections),
        "detections": detections,
    }