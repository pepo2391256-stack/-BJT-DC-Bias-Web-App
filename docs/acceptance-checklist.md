# Acceptance Checklist — Lab 02 (A1–A7)

ตรวจเมื่อ: 10 พ.ย. 2026 · Commit: `0a5ddf7` (ก่อนเพิ่มเอกสารชุดนี้)

| # | เกณฑ์ | สถานะ | หลักฐาน |
|---|-------|--------|----------|
| A1 | `GET /` เปิดผ่าน localhost ได้ HTTP 200 และเห็น Input Form | ✅ | `Invoke-WebRequest http://127.0.0.1:5000/` → 200 · ภาพ `docs/screenshot-input.jpeg` |
| A2 | `POST /calculate` ให้ Python คำนวณและแสดงผลใน HTML (ไม่ hardcode) | ✅ | ภาพ `docs/screenshot-result.jpeg` (VB 1.942 V, VCE 8.052 V, IC 1.230 mA) · `tests/test_web.py` |
| A3 | ค่าตรงกับการคำนวณอิสระภายใต้แบบจำลองเดียวกัน | ✅ | ตารางคำนวณมือใน `docs/validation.md` · `tests/test_dc_bias.py` |
| A4 | R≤0, β≤0, ข้อมูลไม่ใช่ตัวเลข → Error ชัดเจน หน้าไม่ล้ม | ✅ | ภาพ `docs/screenshot-error.jpeg` · HTTP 400 · `ValidationTest` 3 เทสต์ |
| A5 | เตือนกรณี Cutoff / Saturation | ✅ | ภาพ `docs/screenshot-warning.jpeg` (Saturation, VCE = −0.451 V) · `RegionTest` 2 เทสต์ |
| A6 | ≥3 Automated Tests ด้าน Engineering + ≥1 Flask test client | ✅ | **14 เทสต์** (10 engineering + 4 web) · `docs/test-log.txt` |
| A7 | Clone repo แล้วติดตั้ง/รัน/ทดสอบตาม README ได้ | ⏳ | README มีคำสั่งครบ แต่ต้อง **Publish repository** ขึ้น GitHub ก่อนจึงจะ clone ได้ |

## หลักฐานที่ต้องส่ง Moodle

| สิ่งที่ต้องส่ง | ไฟล์ / ค่า |
|---|---|
| Repository URL | (เติมหลัง Publish) |
| Commit SHA | `0a5ddf7` + commit ของเอกสารชุดนี้ |
| ภาพหน้าจอเว็บที่คำนวณสำเร็จ | `docs/screenshot-result.jpeg` |
| ภาพหน้าจอ error / warning | `docs/screenshot-error.jpeg`, `docs/screenshot-warning.jpeg` |
| Test log | `docs/test-log.txt` |
| Design / Validation / Reflection | `docs/design-note.md`, `docs/validation.md`, `docs/reflection.md` |

## วิธีรันซ้ำเพื่อตรวจเอง

```powershell
.\.venv\Scripts\Activate.ps1
python -m flask --app app run --debug
# เปิด http://127.0.0.1:5000/

python -m unittest discover -s tests -v
```

## Rubric (10 คะแนน)

| เกณฑ์ | คะแนน | สิ่งที่ส่ง |
|---|---|---|
| Brainstorm + Planning สมเหตุสมผล | 1 | `docs/design-note.md` |
| Flask Web App เปิดได้ รับ/แสดงผล (multi-file) | 3 | `app.py`, `templates/`, `static/`, ภาพหน้าจอ |
| DC Bias ถูกหลักวงจร มีหน่วย/สมมติฐาน | 2 | `dc_bias.py`, `docs/validation.md` |
| Automated Tests + Validation + Warning | 2 | `tests/`, `docs/test-log.txt`, ภาพ error/warning |
| Review, GitHub Commit/Push, README, Reflection | 2 | commit history, `README.md`, `docs/reflection.md` |
