# Implementation Plan — Lab 02

ขอบเขต: Flask Web App สำหรับ DC Bias ของ NPN BJT แบบ Voltage-Divider Bias
ภายในคาบเดียว (DC เท่านั้น ไม่มี AC/Transient/SPICE)

## ลำดับงานและผลลัพธ์

| # | งาน | ไฟล์ | เกณฑ์ตรวจรับ |
|---|-----|------|--------------|
| 1 | กำหนดแบบจำลองและสมการ | `docs/design-note.md` | Brainstorm + Planning |
| 2 | เขียนฟังก์ชันคำนวณ + validation | `dc_bias.py` | DC Bias ถูกหลักวงจร |
| 3 | เขียน Flask routes | `app.py` | Web App multi-file |
| 4 | สร้างฟอร์ม + แผนผัง + ตารางผล | `templates/index.html` | รับ/แสดงผลได้ |
| 5 | จัดรูปแบบและ responsive | `static/style.css` | ใช้งานบน Browser ได้ |
| 6 | เขียน engineering tests | `tests/test_dc_bias.py` | Automated Tests |
| 7 | เขียน HTTP tests | `tests/test_web.py` | Flask test client |
| 8 | ตรวจค่ากับการคำนวณมือ | `docs/validation.md` | ความถูกต้องของ DC Bias |
| 9 | เก็บหลักฐาน + review | `docs/acceptance-checklist.md`, `docs/code-review.md` | Review + หลักฐานส่งงาน |
| 10 | Commit / Push | GitHub | GitHub Reproducibility |

## เกณฑ์เสร็จของแต่ละงาน (Definition of Done)

- โค้ดรันได้โดยไม่ error และ `python -m unittest discover -s tests` ผ่านทั้งหมด
- ทุกค่าที่แสดงมีหน่วย
- อินพุตผิดต้องได้ข้อความอ่านได้ ไม่ทำให้หน้าเว็บล้ม
- ผลนอก Forward-Active ต้องมี warning
- มีหลักฐานภาพหน้าจอหรือ log สำหรับเกณฑ์ที่ตรวจด้วยตา

## การแบ่งงานตามความรับผิดชอบของไฟล์

- `dc_bias.py` — สมการ + validation (ไม่ import Flask)
- `app.py` — HTTP, อ่านฟอร์ม, จัดรูปแบบตัวเลข
- `templates/index.html` — แสดงผลเท่านั้น ไม่มีสมการฟิสิกส์
- `static/style.css` — หน้าตา
- `tests/` — ตรวจทั้งคณิตศาสตร์และ HTTP

## ความเสี่ยงและวิธีลด

| ความเสี่ยง | วิธีลด |
|---|---|
| แปลงหน่วย kΩ ผิด | แปลงครั้งเดียวใน `dc_bias.py` + test ค่าอ้างอิง |
| ค่า IC ติดลบตอนอิ่มตัว | ตรวจ `VCE < 0.3 V` แล้วขึ้น warning |
| หน้าเว็บล้มเมื่ออินพุตผิด | `ValidationError` + HTTP 400 + re-render ฟอร์ม |
| งานเกินเวลา | จำกัดเฉพาะ DC Bias, ไม่ทำ AC/Transient |
