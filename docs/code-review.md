# Code Review — Lab 02

วันที่ review: 10 พ.ย. 2026
ขอบเขต: `app.py`, `dc_bias.py`, `templates/index.html`, `static/style.css`, `tests/`

## สรุปผล

| ด้าน | ผล | หมายเหตุ |
|---|---|---|
| Separation of concerns | ผ่าน | `dc_bias.py` ไม่ import Flask; template ไม่มีสมการฟิสิกส์ |
| ความถูกต้องของสมการ | ผ่าน | ตรงกับการคำนวณมือใน `docs/validation.md` |
| หน่วย | ผ่าน | ทุกค่าที่แสดงมี V / mA / µA / kΩ |
| Validation | ผ่าน | R≤0, β≤0, ค่าไม่ใช่ตัวเลข → HTTP 400 + ข้อความ |
| Warning | ผ่าน | Cutoff (VTH ≤ VBE) และ Saturation (VCE < 0.3 V) |
| Tests | ผ่าน | 14 เทสต์ (10 engineering + 4 HTTP) |
| ความปลอดภัยเบื้องต้น | ผ่าน | ไม่มี secret, `.venv/` และ `.env` ถูก ignore |
| UI | ผ่านหลังแก้ | พบ bug แล้วแก้ (ข้อ 1 ด้านล่าง) |

## ปัญหาที่พบและวิธีแก้

1. **Label ในฟอร์มแตกแนวตั้ง**
   - อาการ: `V`, `CC`, `V` ขึ้นคนละบรรทัด เพราะ `<label>` เป็น `display:grid`
     และ `<sub>`/`<span class="unit">` ถูกมองเป็น grid item แยก
   - แก้: ห่อข้อความ label ด้วย `<span class="label-text">` ให้เหลือ 2 grid item
     (ข้อความ + input)

2. **Template เคยแสดงผลเฉพาะกรณี active**
   - อาการ: ไม่มีคำอธิบายว่าทำไมค่าไม่น่าเชื่อถือ
   - แก้: เพิ่มการ์ด `Model Assumptions & Region Limits` ระบุเงื่อนไข Cutoff/Saturation

3. **ไม่เห็นที่มาของตัวเลข**
   - อาการ: ผู้ตรวจไม่รู้ว่าค่ามาจาก Python หรือ hardcode
   - แก้: เพิ่ม `<details>` แสดงการแทนค่าในสมการทุกบรรทัด

4. **Git แจ้งเตือน LF → CRLF**
   - อาการ: warning ตอน `git add`
   - ตัดสิน: เป็นพฤติกรรมปกติของ `core.autocrlf` บน Windows ไม่กระทบการรัน
     และ GitHub จัดเก็บเป็น LF ตาม `.gitattributes` (`* text=auto`)

## สิ่งที่ตรวจแล้วไม่พบปัญหา

- ไม่มี SQL/คำสั่ง shell ที่รับค่าจากผู้ใช้
- ไม่มี API key หรือรหัสผ่านในไฟล์ที่ commit
- ไม่มี dependency ส่วนเกิน (`requirements.txt` มีเฉพาะ Flask)

## หลักฐานการตรวจ

```bash
python -m unittest discover -s tests -v
# Ran 14 tests — OK
```

ภาพหน้าจอ: `docs/screenshot-result.jpeg`, `docs/screenshot-error.jpeg`,
`docs/screenshot-warning.jpeg`
