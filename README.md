# Branch: `feat/core-holistic-engine`
**Course:** Digital Image Processing (Work_6)  
**Repository:** [Kong19565/IMG_Processing-Holistic_landmark](https://github.com/Kong19565/IMG_Processing-Holistic_landmark)

---

## 👥 ผู้รับผิดชอบใน Branch นี้ (Responsible Members)

| รหัสนักศึกษา | ชื่อ-นามสกุล (TH) | Name-Surname (EN) | หน้าที่และความรับผิดชอบใน Branch นี้ |
| :---: | :--- | :--- | :--- |
| **6710301007** | นาย ดรัณภพ พิทักษ์กิจไพศาล | Darunpop Pitakkitpaisarn | - ศึกษา Google MediaPipe Tasks API สถาปัตยกรรม HolisticLandmarker<br>- พัฒนาโมดูลดาวน์โหลดและจัดการโมเดล `.task` (`core/model_manager.py`)<br>- พัฒนาระบบคำนวณชีวกลศาสตร์และมุมข้อต่อ 2D/3D (`core/analytics.py`) |
| **6710301009** | นาย อภิสักก์ คงภักดี | Apisak Kongphakdee | - พัฒนา Wrapper ประมวลผลภาพ `HolisticDetector` (`core/holistic_detector.py`) รองรับ Image, Video, Live Stream<br>- พัฒนาระบบ Custom Drawer แสดงผล Face (478 pts), Pose (33 pts), Hands (42 pts) (`core/drawing_utils.py`)<br>- ออกแบบและเขียนชุดทดสอบ Unit Tests (`tests/test_core.py`) |

---

## 🎯 วัตถุประสงค์และขอบเขตงานของ Branch (`feat/core-holistic-engine`)
1. **Model Management (`core/model_manager.py`):**
   - ตรวจสอบไฟล์โมเดล `holistic_landmarker.task` หากไม่พบจะทำการดาวน์โหลดจาก Google Storage อัตโนมัติ
2. **Holistic Detection Engine (`core/holistic_detector.py`):**
   - พัฒนาคลาสหลักที่เชื่อมต่อกับ MediaPipe Tasks Vision
   - รองรับโหมดประมวลผลทั้งแบบภาพเดี่ยว (Image), วิดีโอต่อเนื่อง (Video with timestamps), และสตรีมสด (Live Stream async callback)
   - แปลงข้อมูลผลลัพธ์เป็น JSON Dictionary สำหรับส่งต่อ API
3. **Custom Drawing Utilities (`core/drawing_utils.py`):**
   - เรนเดอร์เส้นเชื่อมต่อและจุดโหนดด้วย OpenCV Anti-Aliasing
   - แบ่งเลเยอร์อิสระ (Face Mesh, Contours, Lips, Irises, Pose Skeleton, Left/Right Hands, Analytics HUD)
4. **Biomechanical Analytics (`core/analytics.py`):**
   - คำนวณมุมข้อศอก (Elbow Angle), มุมข้อเข่า (Knee Angle), และความเอียงของลำตัว (Torso Inclination) จากพิกัดเวกเตอร์