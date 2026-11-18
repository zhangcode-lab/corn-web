from ultralytics import YOLO
model=YOLO("yolov8n.pt")
result=model("test.jpg",conf=0.5)
#print(result[0].boxes)
result[0].save(filename="result.jpg")
#print("已保存result.jpg")

#----下面是提取数据的代码----

#1.准备一个空列表，用来装最后的字典
output_list=[]

#2.拿到所有的框
boxes=result[0].boxes

#遍历每一个框
for box in boxes:

#提取类别名称（转为整数）
	class_id=int(box.cls.item())

#提取类别名称（通过result[0]names字典去查）
	class_name=result[0].names[class_id]

#提取置信度（转为浮点数，并保留两位小数）
	confidence=round(box.conf.item(),2)

#提取左上角坐标和宽高（xywh格式）
	#x,y,w,h=box.xywh[0].tolist()
	cx,cy,w,h=box.xywh[0].tolist()
	x,y=cx-w/2,cy-h/2
#组装成字典
	item_dict={
		"name":class_name,
		"confidence":confidence,
		"x":int(x),
		"y":int(y),
		"w":int(w),
		"h":int(h),
		"conf_percent":int(confidence*100)
	}

#塞进大列表里
	output_list.append(item_dict)

#最后打印这个列表
print(output_list)

#检测
h_img,w_img=result[0].orig_shape
print("图片高",h_img,"宽",w_img)
for d in output_list:
	if d["x"]+d["w"]>w_img or d["y"]+d["h"]>h_img:
		print("!超出图片范围:",d)
