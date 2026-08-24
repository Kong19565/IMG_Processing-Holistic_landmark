# Branch: `feat/flask-web-dashboard`
**Course:** Digital Image Processing (Work_6)  
**Repository:** [Kong19565/IMG_Processing-Holistic_landmark](https://github.com/Kong19565/IMG_Processing-Holistic_landmark)

---

## 👥 ผู้รับผิดชอบใน Branch นี้ (Responsible Members)

| รหัสนักศึกษา | ชื่อ-นามสกุล (TH) | Name-Surname (EN) | หน้าที่และความรับผิดชอบใน Branch นี้ |
| :---: | :--- | :--- | :--- |
| **6710301047** | นาย วิรัชสัณห์ เจนนานาโชค | Viruchsun Jennanachok | - ออกแบบและพัฒนาโครงสร้าง Web Server ด้วย Flask (`app.py`)<br>- พัฒนาระบบ Thread-safe Camera Manager สำหรับสตรีมภาพสดแบบ MJPEG (`/video_feed`)<br>- พัฒนา REST APIs สำหรับอัปโหลดภาพและวิดีโอ (`/api/process_image`, `/api/process_video`) |
| **6710301009** | นาย อภิสักก์ คงภักดี | Apisak Kongphakdee | - ออกแบบและสร้างหน้า Modern Dark Dashboard UI (`templates/index.html`, `static/css/style.css`)<br>- พัฒนาระบบ Client Controller (`static/js/app.js`) สำหรับ Live Telemetry Polling, สลับสวิตช์เลเยอร์, และ Dropzone Uploader<br>- พัฒนาชุดทดสอบ Web API Integration Tests (`tests/test_web.py`) |

---

## 🎯 วัตถุประสงค์และขอบเขตงานของ Branch (`feat/flask-web-dashboard`)
1. **Flask Web Server Backend (`app.py`):**
   - การจัดการกล้องแบบ Multi-threading ไม่ให้การประมวลผลบล็อก Main Event Loop
   - Endpoint `/video_feed`: สตรีมภาพแบบ MJPEG พร้อมรองรับ Query Parameters ปรับแต่งเลเยอร์แบบไดนามิก
   - Endpoint `/api/telemetry`: ส่งคืนสถิติมุมข้อต่อ ค่าความเอียงลำตัว จำนวน Landmark และค่า FPS ปัจจุบัน
2. **Modern Glassmorphism Dark UI (`templates/index.html`, `static/`):**
   - แดชบอร์ดมืดดีไซน์ล้ำสมัย พร้อมแถบสี Neon Accent (Cyan, Orange, Magenta, Yellow)
   - สวิตช์เปิด-ปิด Landmark แต่ละส่วน (Face Mesh, Pose, Hands, Biometrics)
   - เกจวัดมุมข้อต่อแบบเรียลไทม์ (Progress Bars)
   - Drag & Drop Dropzone สำหรับอัปโหลดรูปภาพและวิดีโอเพื่อวิเคราะห์ทันที
   - ตัวดูข้อมูลพิกัด JSON Inspector แบบย่อ-ขยายได้