# Branch: `feat/cli-local-eval`
**Course:** Digital Image Processing (Work_6)  
**Repository:** [Kong19565/IMG_Processing-Holistic_landmark](https://github.com/Kong19565/IMG_Processing-Holistic_landmark)

---

## 👥 ผู้รับผิดชอบใน Branch นี้ (Responsible Members)

| รหัสนักศึกษา | ชื่อ-นามสกุล (TH) | Name-Surname (EN) | หน้าที่และความรับผิดชอบใน Branch นี้ |
| :---: | :--- | :--- | :--- |
| **6710301032** | นาย ธนัท จงธีรธนโชติ | Thanut Jongteerathanachote | - ออกแบบและพัฒนาระบบ Command-Line Interface (`main_cli.py`)<br>- พัฒนาระบบประมวลผลกล้อง Webcam สด พร้อมปุ่มคีย์ลัด (Hotkeys) สลับเลเยอร์แบบ Real-time<br>- พัฒนาระบบประมวลผลไฟล์วิดีโอ (Frame-by-frame with timestamps) และการ Export ข้อมูล Landmark JSON |
| **6710301007** | นาย ดรัณภพ พิทักษ์กิจไพศาล | Darunpop Pitakkitpaisarn | - จัดเตรียมชุดสื่อตัวอย่างรูปภาพและคลิปวิดีโอสังเคราะห์ (`sample_media/download_samples.py`)<br>- ทดสอบและประเมินประสิทธิภาพความเร็วการประมวลผล (Inference Latency & FPS Benchmark) |

---

## 🎯 วัตถุประสงค์และขอบเขตงานของ Branch (`feat/cli-local-eval`)
1. **Interactive CLI Tool (`main_cli.py`):**
   - รองรับการประมวลผล 3 รูปแบบ: `--source webcam`, `--source image_path`, `--source video_path`
   - ระบบ Hotkeys: `[F]` Face, `[P]` Pose, `[H]` Hands, `[A]` Analytics, `[S]` Snapshot, `[Q]` Exit
   - ส่งออกข้อมูลพิกัด Landmark และผลการวิเคราะห์มุมข้อต่อเป็นไฟล์ `.json` ผ่าน `--export-json`
2. **Sample Media Pipeline (`sample_media/`):**
   - ดาวน์โหลดรูปภาพตัวอย่างท่าทางและภาพบุคคล
   - สคริปต์สร้างไฟล์วิดีโอทดสอบแบบสังเคราะห์ (`sample_clip.mp4`) เพื่อทดสอบไปป์ไลน์วิดีโอได้อย่างรวดเร็ว