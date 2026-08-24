# MediaPipe Holistic Landmark Detection & Biometric Analytics Studio
**Course:** Digital Image Processing (Work_6)  
**Author:** Apisak Kongpakdee (Student ID: 6710301009)  
**Repository:** [Kong19565/IMG_Processing-Holistic_landmark](https://github.com/Kong19565/IMG_Processing-Holistic_landmark)

---

## 📌 1. บทนำและภาพรวมโครงการ (Project Overview)

โครงการนี้เป็นการศึกษาและพัฒนาระบบตรวจจับและวิเคราะห์จุดพิกัดร่างกายมนุษย์แบบองค์รวม (**MediaPipe Holistic Landmarker**) โดยใช้ **Google MediaPipe Tasks API** ล่าสุด ซึ่งรวมโมเดลประมวลผล 3 ส่วนหลักเข้าไว้ด้วยกันอย่างเป็นเอกภาพ ได้แก่:
1. **Face Mesh (478 Landmarks):** ตรวจจับโครงสร้างใบหน้า ตา คิ้ว ริมฝีปาก รวมถึงม่านตา (Iris refinement)
2. **Body Pose (33 Landmarks):** ตรวจจับจุดข้อต่อร่างกายหลัก ศีรษะ ไหล่ ศอก ข้อมือ สะโพก เข่า และข้อเท้า
3. **Left & Right Hands (21x2 = 42 Landmarks):** ตรวจจับจุดข้อนิ้วและฝ่ามือทั้งสองข้างอย่างละเอียด

**รวมจุดพิกัดทั้งหมด 543 Landmarks** แบบ Real-Time พร้อมระบบคำนวณชีวกลศาสตร์ (Biomechanical Joint Angles) และส่วนต่อประสานผู้ใช้แบบเว็บ (Flask Dark Web Dashboard)

---

## 🏛️ 2. สถาปัตยกรรมระบบ (System Architecture)

```
Work_6/
├── core/                           # แกนประมวลผลหลัก (Core Engine)
│   ├── __init__.py                 # Export คลาสสำคัญ
│   ├── model_manager.py            # ตรวจสอบและดาวน์โหลดโมเดล .task อัตโนมัติ
│   ├── holistic_detector.py        # Wrapper ของ MediaPipe Tasks HolisticLandmarker
│   ├── drawing_utils.py            # ระบบเรนเดอร์ภาพ Landmark แบบกำหนดเลเยอร์ได้
│   └── analytics.py                # ระบบคำนวณเวกเตอร์มุมข้อต่อและประเมินท่วงท่า
├── static/                         # เว็บแอสเซท (Frontend UI)
│   ├── css/style.css               # สไตล์ Modern Dark Glassmorphism
│   ├── js/app.js                   # ตัวควบคุม Client Controller (Stream / Telemetry)
│   └── uploads/                    # โฟลเดอร์เก็บไฟล์สื่อจากการอัปโหลด
├── templates/
│   └── index.html                  # หน้าแดชบอร์ด Single Page Application
├── sample_media/                   # สื่อตัวอย่างสำหรับการทดสอบ
│   ├── download_samples.py         # ตัวดาวน์โหลดและสร้างสื่อสังเคราะห์
│   ├── sample_pose1.jpg
│   ├── sample_pose2.jpg
│   ├── sample_pose3.jpg
│   └── sample_clip.mp4
├── tests/                          # ชุดการทดสอบระบบ (Unit & Integration Tests)
│   ├── test_core.py                # ทดสอบโมดูล Core และการคำนวณมุม
│   └── test_web.py                 # ทดสอบ Flask Web APIs
├── main_cli.py                     # ส่วนต่อประสานคำสั่ง (CLI Application)
├── app.py                          # เว็บเซิร์ฟเวอร์ (Flask Web Application)
├── requirements.txt                # รายการแพ็กเกจที่ต้องติดตั้ง
└── README.md                       # เอกสารคู่มือโครงการ
```

---

## 📐 3. ทฤษฎีและการคำนวณชีวกลศาสตร์ (Biomechanical Analytics)

### 3.1 การคำนวณมุมข้อต่อ 2D (Joint Angle Formula)
คำนวณมุมระหว่าง 3 จุดพิกัด $\vec{A}, \vec{B}, \vec{C}$ โดยให้จุด $\vec{B}$ เป็นจุดยอดมุม (Vertex) เช่น ข้อศอก หรือ ข้อเข่า:

$$\vec{u} = \vec{A} - \vec{B}, \quad \vec{v} = \vec{C} - \vec{B}$$

$$\theta = \arccos\left( \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|} \right) \times \frac{180^\circ}{\pi}$$

### 3.2 การประเมินความเอียงของลำตัว (Torso Inclination)
คำนวณจากจุดกึ่งกลางสะโพก ($\text{Mid-Hip}$) ไปยังจุดกึ่งกลางไหล่ ($\text{Mid-Shoulder}$) เทียบกับแนวดิ่ง:

$$\Delta x = x_{\text{shoulder}} - x_{\text{hip}}, \quad \Delta y = -(y_{\text{shoulder}} - y_{\text{hip}})$$

$$\text{Tilt Angle} = \left|\arctan2(\Delta x, \Delta y)\right| \times \frac{180^\circ}{\pi}$$

---

## 🚀 4. การติดตั้งและเริ่มต้นใช้งาน (Installation & Setup)

### 4.1 ข้อกำหนดสภาพแวดล้อม
- Python 3.10, 3.11, หรือ 3.12
- เว็บแคม (สำหรับการทดสอบกล้องสด)

### 4.2 ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

---

## 💻 5. การใช้งานผ่าน Command-Line Interface (CLI)

### 5.1 ประมวลผลจากกล้องเว็บแคมสด (Live Webcam)
```bash
python main_cli.py --source webcam
```
*Hotkeys ขณะใช้งานกล้อง:*
- `F` : เปิด/ปิด เลเยอร์ Face Mesh
- `P` : เปิด/ปิด เลเยอร์ Body Pose
- `H` : เปิด/ปิด เลเยอร์ Hands
- `A` : เปิด/ปิด Biometrics HUD
- `S` : บันทึกภาพ Screenshot ลงโฟลเดอร์ `output/`
- `Q` หรือ `ESC` : ปิดโปรแกรม

### 5.2 ประมวลผลรูปภาพเดี่ยว
```bash
python main_cli.py --source sample_media/sample_pose1.jpg --output output/result.jpg --export-json
```

### 5.3 ประมวลผลไฟล์วิดีโอ
```bash
python main_cli.py --source sample_media/sample_clip.mp4 --output output/video_result.mp4
```

---

## 🌐 6. การใช้งานเว็บแอปพลิเคชัน (Flask Web Dashboard)

### 6.1 รันเซิร์ฟเวอร์
```bash
python app.py
```
เปิดเว็บเบราว์เซอร์และเข้าไปที่: `http://localhost:5000`

### 6.2 ฟีเจอร์บน Web Dashboard
- **Live Stream MJPEG Viewport:** รับชมภาพจากกล้องเว็บแคมพร้อม Overlay แบบ Real-time
- **Dynamic Layer Toggles:** สลับเปิด-ปิด Face Mesh, Pose Skeleton, Hands, และ Biometrics ได้ทันที
- **Drag-and-Drop Media Uploader:** รองรับการลากไฟล์รูปภาพหรือวิดีโอเพื่อวิเคราะห์และแสดงผลลัพธ์
- **Live Biometric Telemetry:** แถบเกจวัดมุมข้อศอก, ข้อเข่า, ความเอียงของลำตัว, และการตรวจจับท่าทางยกมือ
- **Landmark JSON Inspector:** ดูพิกัด Normalized Coordinates ของ Landmark แต่ละจุดแบบเรียลไทม์

---

## 🧪 7. การทดสอบระบบ (Automated Tests)

รันชุดทดสอบความถูกต้องของโมดูล Core และ Web APIs:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 🌿 8. ประวัติการพัฒนาและ Git Branching Strategy

โครงการนี้พัฒนาและแบ่งงานออกเป็น Feature Branches อย่างเป็นระบบ:
1. `feat/core-holistic-engine`: พัฒนา `core/` (Detector, Drawer, Analytics, Model Manager)
2. `feat/cli-local-eval`: พัฒนา `main_cli.py` และเตรียมตัวอย่างสื่อ `sample_media/`
3. `feat/flask-web-dashboard`: พัฒนา `app.py`, `templates/`, และ `static/`
4. `main`: ผสานรวมทุกฟีเจอร์และตรวจสอบความสมบูรณ์ขั้นสุดท้าย