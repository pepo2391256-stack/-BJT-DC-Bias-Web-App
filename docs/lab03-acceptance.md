# Lab 03 · ผลทดสอบ A1–A5 ผ่าน Browser

- วันที่ทดสอบ: 17 พ.ย. 2569
- URL: <http://127.0.0.1:5000/>
- วิธีตรวจ: OpenCode Browser (navigate → select mode → fill form → click **Calculate DC Bias** → อ่านตารางผลจริง)
- ค่าคงที่ร่วม: V<sub>CC</sub> = 12 V · R<sub>C</sub> = 2.2 kΩ · β = 100 · V<sub>BE</sub> = 0.70 V
- เกณฑ์ผ่าน: |ΔI<sub>C</sub>| ≤ 0.01 mA และ |ΔV<sub>CE</sub>| ≤ 0.02 V

## ค่าอ้างอิงอิสระ (คำนวณมือจากสมการในใบงาน ไม่ได้มาจากโปรแกรม)

| กรณี | I<sub>C</sub> อ้างอิง | V<sub>CE</sub> อ้างอิง |
|---|---|---|
| A1 Divider · R1=100 k, R2=22 k, RE=1 k | 1.230 mA | 8.051 V |
| A2 Fixed · RB=1 MΩ | 1.130 mA | 9.514 V |
| A3 Emitter · RB=1 MΩ, RE=1 kΩ | 1.026 mA | 8.705 V |
| A4 Emitter · RB=1 MΩ, RE=2 kΩ | 0.940 mA | 8.033 V |
| A5 Fixed · RB=0 | — ต้องแจ้งข้อผิดพลาด | — |

## ผลที่เห็นจริงบนหน้าเว็บ

| กรณี | โหมดที่เลือก + ค่าที่กรอก | V_B | V_E | V_C | V_CE | I_C | I_B | หลักฐาน | สถานะ |
|---|---|---|---|---|---|---|---|---|---|
| A1 | Voltage Divider · R1=100, R2=22, RE=1 (kΩ) | 1.942 V | 1.242 V | 9.294 V | 8.052 V | 1.230 mA | 12.30 µA | [ภาพ](lab03/A1-divider.jpeg) | PASS |
| A2 | Fixed · RB=1000 kΩ | 0.700 V | 0.000 V | 9.514 V | 9.514 V | 1.130 mA | 11.30 µA | [ภาพ](lab03/A2-fixed.jpeg) | PASS |
| A3 | Emitter · RB=1000 kΩ, RE=1 kΩ | 1.737 V | 1.037 V | 9.742 V | 8.705 V | 1.026 mA | 10.26 µA | [ภาพ](lab03/A3-emitter-re1k.jpeg) | PASS |
| A4 | Emitter · RB=1000 kΩ, RE=2 kΩ | 2.599 V | 1.899 V | 9.932 V | 8.033 V | 0.940 mA | 9.40 µA | [ภาพ](lab03/A4-emitter-re2k.jpeg) | PASS |
| A5 | Fixed · RB=0 | — | — | — | — | — | — | [ภาพ](lab03/A5-fixed-rb0-error.jpeg) | PASS |

## หมายเหตุรายกรณี

- **A1** — ผลตรงกับชุดที่บันทึกไว้ก่อนแก้โค้ด (Lab 02) ทุกค่า: V<sub>B</sub> 1.942 V, I<sub>C</sub> 1.230 mA, V<sub>CE</sub> 8.052 V และ V<sub>TH</sub>/R<sub>TH</sub> ยังแสดงเฉพาะโหมดนี้
- **A2** — ฟอร์มไม่มีช่อง R<sub>E</sub> (แสดงเฉพาะ V<sub>CC</sub>, R<sub>B</sub>, R<sub>C</sub>, β, V<sub>BE</sub>) และ V<sub>E</sub> = 0.000 V ตามวงจร Fixed
- **A3** — มีช่อง R<sub>E</sub> และค่าที่กรอกถูกใช้จริง (V<sub>E</sub> = 1.037 V)
- **A4** — เปลี่ยนเฉพาะ R<sub>E</sub> 1 → 2 kΩ โดยโหมดและค่าอื่นคงเดิม; I<sub>C</sub> ลดลง 1.026 → 0.940 mA และ V<sub>CE</sub> ลดลง 8.705 → 8.033 V ตรงกับที่ทำนายไว้ (R<sub>E</sub> ใหญ่ขึ้น → กระแสฐาน/collector ลดลง)
- **A5** — หน้าเว็บตอบ `HTTP 400` พร้อมกล่อง "ตรวจสอบข้อมูลอีกครั้ง · Fixed Bias — RB ต้องมากกว่า 0" ไม่มีตารางผลลัพธ์ค้างจากรอบก่อน และหน้าเว็บไม่ล่ม

## ตรวจซ้ำแบบไม่ใช้เบราว์เซอร์

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
# Ran 25 tests ... OK
```
