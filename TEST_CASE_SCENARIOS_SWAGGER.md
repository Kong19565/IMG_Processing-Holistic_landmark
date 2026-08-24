# 📋 Test Case Scenarios Document: MediaPipe Holistic Landmark API (Swagger / OpenAPI 3.0)

**Project:** MediaPipe Holistic Landmark Detection & Biometric Analytics Studio (Work_6)  
**Specification Standards:** OpenAPI 3.0.3 / Swagger UI  
**Base URL:** `http://localhost:5000`  
**Swagger UI Endpoint:** `http://localhost:5000/docs` หรือ `http://localhost:5000/swagger`  
**OpenAPI Spec Files:** `swagger.json` | `swagger.yaml`  

---

## 📌 1. ภาพรวมชุดทดสอบ (Overview)

เอกสารฉบับนี้กำหนด **Test Case Scenarios** สำหรับทดสอบระบบ REST APIs และ Stream Endpoints ของโครงการ **MediaPipe Holistic Landmark Studio** ผ่าน **Swagger UI / OpenAPI Specification** โดยครอบคลุมทั้ง:
1. **Positive Test Cases:** การทำงานปกติของระบบเมื่อได้รับ Request ที่ถูกต้อง
2. **Negative Test Cases:** การรับมือกับข้อผิดพลาด (Missing file, Invalid format, Corrupted binary)
3. **Edge Cases & Boundary Conditions:** ภาพที่ไม่มีมนุษย์, ท่าทางยกมือ/ก้มตัว, การสลับ Layer Annotation
4. **State & Telemetry Lifecycle:** การตรวจสอบสถานะกล้อง การสตรีม MJPEG และการอ่านข้อมูลชีวกลศาสตร์ (Joint Angles)

---

## 📊 2. ตารางสรุป Master Test Scenario Matrix

| Scenario ID | Category / Tag | Endpoint | Method | Scenario Type | Expected Status | วัตถุประสงค์หลัก |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **TS-CAM-01** | Camera & Stream | `/api/camera/start` | `POST` | Positive | `200 OK` | เปิดกล้องเว็บแคมและเริ่ม Thread ประมวลผลภาพสด |
| **TS-CAM-02** | Camera & Stream | `/api/camera/start` | `POST` | Negative | `500 Internal Error` | กรณีเปิดกล้องไม่สำเร็จ (ไม่มีฮาร์ดแวร์/อุปกรณ์ไม่ว่าง) |
| **TS-CAM-03** | Camera & Stream | `/api/camera/stop` | `POST` | Positive | `200 OK` | ปิดกล้องและคืนทรัพยากร VideoCapture |
| **TS-CAM-04** | Camera & Stream | `/api/camera/status` | `GET` | State Check | `200 OK` | ตรวจสอบสถานะกล้องขณะยังไม่เปิด (`is_running: false`) |
| **TS-CAM-05** | Camera & Stream | `/api/camera/status` | `GET` | State Check | `200 OK` | ตรวจสอบสถานะกล้องขณะเปิดทำงาน (`is_running: true`, `fps > 0`) |
| **TS-STR-01** | Camera & Stream | `/video_feed` | `GET` | Stream | `200 OK` | รับ MJPEG Stream เปิดครบทุก Layer (`face`, `pose`, `hands`, `analytics`) |
| **TS-STR-02** | Camera & Stream | `/video_feed` | `GET` | Stream | `200 OK` | รับ MJPEG Stream แบบเปิดเฉพาะ Pose Skeleton |
| **TS-TEL-01** | Telemetry | `/api/telemetry` | `GET` | Positive (Idle) | `200 OK` | ดึง Telemetry ขณะกล้องยังไม่ทำงานหรือยังไม่มีเฟรม |
| **TS-TEL-02** | Telemetry | `/api/telemetry` | `GET` | Positive (Live) | `200 OK` | ดึง Telemetry และพิกัด 543 Landmarks พร้อมมุมข้อต่อ |
| **TS-TEL-03** | Telemetry | `/api/telemetry` | `GET` | Biometric Event | `200 OK` | ตรวจจับท่ายกมือ (`hands_up_status: Both Hands Raised`) |
| **TS-IMG-01** | Media Processing | `/api/process_image` | `POST` | Positive | `200 OK` | อัปโหลดรูปภาพคน ตรวจจับ 543 Landmarks + คำนวณมุมข้อต่อ |
| **TS-IMG-02** | Media Processing | `/api/process_image` | `POST` | Positive | `200 OK` | อัปโหลดรูปภาพโดยเลือกเปิดเฉพาะ Layer Pose และ HUD |
| **TS-IMG-03** | Media Processing | `/api/process_image` | `POST` | Edge Case | `200 OK` | อัปโหลดรูปวิวที่ไม่มีคน (คืนค่า 0 Landmarks อย่างราบรื่น) |
| **TS-IMG-04** | Media Processing | `/api/process_image` | `POST` | Negative | `400 Bad Request` | ส่ง Request โดยไม่มี Field `file` |
| **TS-IMG-05** | Media Processing | `/api/process_image` | `POST` | Negative | `400 Bad Request` | ส่งไฟล์ที่มีชื่อว่างเปล่า (`filename: ""`) |
| **TS-IMG-06** | Media Processing | `/api/process_image` | `POST` | Negative | `400 Bad Request` | ส่งไฟล์ Corrupted / Non-image bytes |
| **TS-VID-01** | Media Processing | `/api/process_video` | `POST` | Positive | `200 OK` | อัปโหลดไฟล์วิดีโอ MP4 ประมวลผลและสร้างวิดีโอ Overlay |
| **TS-VID-02** | Media Processing | `/api/process_video` | `POST` | Negative | `400 Bad Request` | ส่ง Request วิดีโอโดยไม่มี Field `file` |
| **TS-VID-03** | Media Processing | `/api/process_video` | `POST` | Negative | `400 Bad Request` | ส่งไฟล์วิดีโอที่เสียหายหรือไม่สามารถ Decode ได้ |
| **TS-DOC-01** | Documentation | `/swagger.json` | `GET` | Validation | `200 OK` | ตรวจสอบความถูกต้องของ OpenAPI 3.0 Specification JSON |
| **TS-DOC-02** | Documentation | `/docs` | `GET` | Validation | `200 OK` | ตรวจสอบการโหลดหน้า Swagger UI Web Dashboard |

---

## 🔬 3. รายละเอียด Test Case Scenarios (Scenario Specifications)

---

### 📷 หมวดหมู่ที่ 1: Camera & Stream Lifecycle

#### 🔹 TS-CAM-01: Start Live Camera Stream (Positive Case)
- **Endpoint:** `POST /api/camera/start`
- **Request Headers:** `Content-Type: application/json`
- **Request Body:** `{}` (Empty)
- **Precondition:** มีกล้องเว็บแคมเชื่อมต่อกับเครื่องและพร้อมใช้งาน
- **Expected Response (HTTP 200 OK):**
```json
{
  "status": "ok",
  "message": "Camera started"
}
```
- **Assertion Rules:**
  1. `response.status_code == 200`
  2. `response.json["status"] == "ok"`

---

#### 🔹 TS-CAM-02: Start Camera Hardware Failure (Negative Case)
- **Endpoint:** `POST /api/camera/start`
- **Precondition:** กล้องถูกโปรแกรมอื่นแย่งใช้งาน หรือไม่มีฮาร์ดแวร์กล้อง
- **Expected Response (HTTP 500 Internal Server Error):**
```json
{
  "status": "error",
  "message": "Could not open camera"
}
```
- **Assertion Rules:**
  1. `response.status_code == 500`
  2. `response.json["status"] == "error"`

---

#### 🔹 TS-CAM-03: Stop Live Camera Stream (Positive Case)
- **Endpoint:** `POST /api/camera/stop`
- **Expected Response (HTTP 200 OK):**
```json
{
  "status": "ok",
  "message": "Camera stopped"
}
```
- **Assertion Rules:**
  1. `response.status_code == 200`
  2. `response.json["status"] == "ok"`

---

#### 🔹 TS-CAM-04: Get Camera Status (Idle State)
- **Endpoint:** `GET /api/camera/status`
- **Precondition:** กล้องอยู่ในสถานะปิด (`is_running == false`)
- **Expected Response (HTTP 200 OK):**
```json
{
  "is_running": false,
  "fps": 0.0
}
```
- **Assertion Rules:**
  1. `response.status_code == 200`
  2. `response.json["is_running"] == false`
  3. `response.json["fps"] == 0.0`

---

#### 🔹 TS-CAM-05: Get Camera Status (Active Streaming State)
- **Endpoint:** `GET /api/camera/status`
- **Precondition:** กล้องเปิดทำงานอยู่ (`/api/camera/start` สำเร็จแล้ว)
- **Expected Response (HTTP 200 OK):**
```json
{
  "is_running": true,
  "fps": 28.5
}
```
- **Assertion Rules:**
  1. `response.status_code == 200`
  2. `response.json["is_running"] == true`
  3. `response.json["fps"] > 0`

---

### 📡 หมวดหมู่ที่ 2: Telemetry & Biometric Analytics

#### 🔹 TS-TEL-01: Get Telemetry (Idle / No Frame)
- **Endpoint:** `GET /api/telemetry`
- **Precondition:** กล้องยังไม่เปิดหรือกำลังรอเฟรมแรก
- **Expected Response (HTTP 200 OK):**
```json
{
  "status": "idle",
  "fps": 0.0,
  "analytics": {},
  "face_landmarks_count": 0,
  "pose_landmarks_count": 0,
  "left_hand_landmarks_count": 0,
  "right_hand_landmarks_count": 0
}
```
- **Assertion Rules:**
  1. `response.status_code == 200`
  2. `response.json["face_landmarks_count"] == 0`
  3. `response.json["analytics"] == {}`

---

#### 🔹 TS-TEL-02: Get Telemetry (Live Body Detected - Upright Posture)
- **Endpoint:** `GET /api/telemetry`
- **Precondition:** มีบุคคลยืนตรงหน้ากล้อง
- **Expected Response (HTTP 200 OK):**
```json
{
  "status": "live",
  "fps": 29.8,
  "analytics": {
    "left_elbow_angle": 164.5,
    "right_elbow_angle": 158.2,
    "left_knee_angle": 178.0,
    "right_knee_angle": 176.4,
    "left_shoulder_angle": 24.1,
    "right_shoulder_angle": 22.8,
    "shoulder_slope": 1.2,
    "torso_inclination": 3.5,
    "posture_status": "Upright / Balanced",
    "hands_up_status": "Hands Down"
  },
  "face_landmarks_count": 478,
  "pose_landmarks_count": 33,
  "left_hand_landmarks_count": 21,
  "right_hand_landmarks_count": 21,
  "landmarks": {
    "face_landmarks": [{"x": 0.51, "y": 0.32, "z": -0.02}],
    "pose_landmarks": [{"x": 0.50, "y": 0.28, "z": -0.15, "visibility": 0.99}],
    "left_hand_landmarks": [{"x": 0.35, "y": 0.65, "z": -0.01}],
    "right_hand_landmarks": [{"x": 0.65, "y": 0.66, "z": -0.01}]
  }
}
```
- **Assertion Rules:**
  1. `face_landmarks_count == 478`
  2. `pose_landmarks_count == 33`
  3. `analytics["posture_status"] in ["Upright / Balanced", "Leaning / Slouched", "Shoulder Tilted"]`
  4. `0 <= analytics["left_elbow_angle"] <= 180`

---

#### 🔹 TS-TEL-03: Get Telemetry (Hands Raised Gesture Detection)
- **Endpoint:** `GET /api/telemetry`
- **Precondition:** บุคคลยกมือทั้งสองข้างขึ้นเหนือระดับไหล่
- **Expected Response (HTTP 200 OK):**
```json
{
  "status": "live",
  "fps": 30.0,
  "analytics": {
    "hands_up_status": "Both Hands Raised",
    "posture_status": "Upright / Balanced"
  }
}
```
- **Assertion Rules:**
  1. `analytics["hands_up_status"] == "Both Hands Raised"`

---

### 🖼️ หมวดหมู่ที่ 3: Static Image Processing (`/api/process_image`)

#### 🔹 TS-IMG-01: Full Body Landmark Analysis (Positive Case)
- **Endpoint:** `POST /api/process_image`
- **Content-Type:** `multipart/form-data`
- **Form Parameters:**
  - `file`: `sample_pose1.jpg` (Binary Image File)
  - `face`: `"1"`
  - `tesselation`: `"1"`
  - `pose`: `"1"`
  - `hands`: `"1"`
  - `analytics`: `"1"`
- **Expected Response (HTTP 200 OK):**
```json
{
  "status": "success",
  "inference_time_ms": 45.3,
  "fps": 22.1,
  "annotated_image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "analytics": {
    "left_elbow_angle": 155.2,
    "right_elbow_angle": 160.1,
    "left_knee_angle": 175.4,
    "right_knee_angle": 177.0,
    "left_shoulder_angle": 30.5,
    "right_shoulder_angle": 28.2,
    "shoulder_slope": 0.8,
    "torso_inclination": 4.1,
    "posture_status": "Upright / Balanced",
    "hands_up_status": "Hands Down"
  },
  "face_landmarks_count": 478,
  "pose_landmarks_count": 33,
  "left_hand_landmarks_count": 21,
  "right_hand_landmarks_count": 21,
  "landmarks": {
    "face_landmarks": [...],
    "pose_landmarks": [...],
    "left_hand_landmarks": [...],
    "right_hand_landmarks": [...]
  }
}
```
- **Assertion Rules:**
  1. `response.status_code == 200`
  2. `res_json["status"] == "success"`
  3. `res_json["annotated_image_base64"].startswith("data:image/jpeg;base64,")`
  4. `res_json["inference_time_ms"] > 0`

---

#### 🔹 TS-IMG-02: Image Processing with Custom Layer Toggles (Positive Case)
- **Endpoint:** `POST /api/process_image`
- **Form Parameters:**
  - `file`: `sample_pose1.jpg`
  - `face`: `"0"`
  - `tesselation`: `"0"`
  - `pose`: `"1"`
  - `hands`: `"0"`
  - `analytics`: `"1"`
- **Expected Response (HTTP 200 OK):**
```json
{
  "status": "success",
  "annotated_image_base64": "data:image/jpeg;base64,..."
}
```

---

#### 🔹 TS-IMG-03: Image with No Person (Edge Case)
- **Endpoint:** `POST /api/process_image`
- **Form Parameters:**
  - `file`: รูปภาพทิวทัศน์/พื้นหลังว่างเปล่า
- **Expected Response (HTTP 200 OK):**
```json
{
  "status": "success",
  "face_landmarks_count": 0,
  "pose_landmarks_count": 0,
  "left_hand_landmarks_count": 0,
  "right_hand_landmarks_count": 0,
  "analytics": {
    "left_elbow_angle": null,
    "right_elbow_angle": null,
    "posture_status": "Unknown",
    "hands_up_status": "None"
  }
}
```
- **Assertion Rules:**
  1. ไม่เกิด Error 500
  2. `face_landmarks_count == 0`
  3. `pose_landmarks_count == 0`
  4. `analytics["posture_status"] == "Unknown"`

---

#### 🔹 TS-IMG-04: Missing File Field (Negative Case)
- **Endpoint:** `POST /api/process_image`
- **Form Parameters:** `{}` (ไม่มี Field `file`)
- **Expected Response (HTTP 400 Bad Request):**
```json
{
  "error": "No file uploaded"
}
```
- **Assertion Rules:**
  1. `response.status_code == 400`
  2. `response.json["error"] == "No file uploaded"`

---

#### 🔹 TS-IMG-05: Empty Filename Upload (Negative Case)
- **Endpoint:** `POST /api/process_image`
- **Form Parameters:** `file` มี payload ว่างและ `filename: ""`
- **Expected Response (HTTP 400 Bad Request):**
```json
{
  "error": "Empty filename"
}
```
- **Assertion Rules:**
  1. `response.status_code == 400`
  2. `response.json["error"] == "Empty filename"`

---

#### 🔹 TS-IMG-06: Corrupted / Invalid Image Bytes (Negative Case)
- **Endpoint:** `POST /api/process_image`
- **Form Parameters:** `file` เป็น text file หรือ byte ขยะที่ไม่ใช่รูปภาพ
- **Expected Response (HTTP 400 Bad Request):**
```json
{
  "error": "Invalid image format"
}
```
- **Assertion Rules:**
  1. `response.status_code == 400`
  2. `response.json["error"] == "Invalid image format"`

---

### 🎥 หมวดหมู่ที่ 4: Video Processing (`/api/process_video`)

#### 🔹 TS-VID-01: Short Video Landmark Tracking (Positive Case)
- **Endpoint:** `POST /api/process_video`
- **Content-Type:** `multipart/form-data`
- **Form Parameters:**
  - `file`: `sample_clip.mp4` (Binary Video File)
  - `face`: `"1"`, `pose`: `"1"`, `hands`: `"1"`, `analytics`: `"1"`
- **Expected Response (HTTP 200 OK):**
```json
{
  "status": "success",
  "output_video_url": "/static/uploads/output_1724500000_sample_clip.mp4",
  "processed_frames": 120,
  "total_time_seconds": 4.15,
  "average_fps": 28.9,
  "analytics": {
    "left_elbow_angle": 160.0,
    "right_elbow_angle": 158.4,
    "left_knee_angle": 178.2,
    "right_knee_angle": 177.5,
    "posture_status": "Upright / Balanced",
    "hands_up_status": "Hands Down"
  }
}
```
- **Assertion Rules:**
  1. `response.status_code == 200`
  2. `res_json["status"] == "success"`
  3. `res_json["processed_frames"] > 0`
  4. `res_json["output_video_url"].startswith("/static/uploads/")`

---

#### 🔹 TS-VID-02: Video Missing File Field (Negative Case)
- **Endpoint:** `POST /api/process_video`
- **Expected Response (HTTP 400 Bad Request):**
```json
{
  "error": "No file uploaded"
}
```

---

#### 🔹 TS-VID-03: Corrupted Video Format (Negative Case)
- **Endpoint:** `POST /api/process_video`
- **Form Parameters:** `file` เป็น binary ที่ไม่ใช่รูปแบบวิดีโอที่ OpenCV ถอดรหัสได้
- **Expected Response (HTTP 400 Bad Request):**
```json
{
  "error": "Could not decode uploaded video"
}
```
- **Assertion Rules:**
  1. `response.status_code == 400`
  2. `response.json["error"] == "Could not decode uploaded video"`

---

## 💻 4. ตัวอย่างคำสั่ง cURL สำหรับทดสอบแต่ละ Scenario

```bash
# 1. TS-CAM-01: Start Camera
curl -X POST http://localhost:5000/api/camera/start

# 2. TS-CAM-04: Get Camera Status
curl -X GET http://localhost:5000/api/camera/status

# 3. TS-TEL-02: Get Telemetry
curl -X GET http://localhost:5000/api/telemetry

# 4. TS-IMG-01: Process Image (Positive)
curl -X POST http://localhost:5000/api/process_image \
  -F "file=@sample_media/sample_pose1.jpg" \
  -F "face=1" \
  -F "pose=1" \
  -F "hands=1" \
  -F "analytics=1"

# 5. TS-IMG-04: Process Image (Negative - Missing File)
curl -X POST http://localhost:5000/api/process_image

# 6. TS-IMG-06: Process Image (Negative - Corrupt File)
curl -X POST http://localhost:5000/api/process_image \
  -F "file=@requirements.txt"

# 7. TS-CAM-03: Stop Camera
curl -X POST http://localhost:5000/api/camera/stop
```

---

## 🚀 5. วิธีการทดสอบผ่าน Swagger UI บนเบราว์เซอร์

1. **รันเซิร์ฟเวอร์ Flask:**
   ```bash
   python app.py
   ```
2. **เปิด Swagger UI:**
   เปิดเว็บเบราว์เซอร์ไปที่:
   ```
   http://localhost:5000/docs
   ```
3. **การทดสอบ Endpoint:**
   - คลิกที่ Endpoint ที่ต้องการทดสอบ (เช่น `POST /api/process_image`)
   - กดปุ่ม **"Try it out"**
   - เลือกไฟล์รูปภาพในช่อง `file` และกำหนดตัวเลือก Layer (0 หรือ 1)
   - กด **"Execute"**
   - ตรวจสอบ **Response Code (200, 400, 500)** และ **Response Body JSON** เทียบกับ Test Scenario Matrix ด้านบน
