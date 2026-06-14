# TCC Agents — Collaboration Folder Protocol

Folder นี้ใช้เป็น shared workspace สำหรับส่งงานระหว่าง Claude และ Agents ทุกตัว รวมถึง Boss+Antigravity

## Structure

```
Agents/
├── Antigravity/
│   ├── task.md      ← Claude เขียน task ให้ Boss นำไปสั่ง Antigravity
│   └── results.md   ← Boss/Antigravity เขียนผลลัพธ์กลับ → Claude อ่าน
├── Gemini/
│   ├── task.md      ← Claude เขียน prompt แล้วรัน gemini -p โดยตรง
│   └── results.md   ← Claude เขียน output จาก Gemini ไว้ reference
├── Grok/            (via openrouter --model grok)
├── Deepseek/        (via openrouter --model deepseek)
├── ChatGPT/         (via openrouter --model gpt4o)
└── OpenRouter/      (generic — model ระบุใน task.md)
```

## Protocol

### Claude → Agent (write task)
1. Claude เขียน `task.md` ใน folder ของ agent นั้น
2. Fields: Status / Assigned at / Prompt / Context
3. Status: `pending`

### Agent → Claude (write results)
1. Agent (หรือ Boss สำหรับ Antigravity) เขียน `results.md`
2. Fields: Status / Completed at / Output
3. Status: `done` | `error`
4. Claude poll `results.md` จนเจอ status=done

### Status values
- `empty` — ไม่มีงาน
- `pending` — Claude assign แล้ว รอ agent รัน
- `done` — agent เสร็จแล้ว Claude อ่านได้
- `error` — งานล้มเหลว ดู Output สำหรับ error message

## Antigravity Special Case
Antigravity ไม่มี headless CLI → Boss เป็น bridge:
1. Claude เขียน `Antigravity/task.md`
2. **Boss** อ่าน task.md → copy prompt → สั่ง Antigravity
3. **Boss** copy output จาก Antigravity → เขียนลง `Antigravity/results.md`
4. Claude อ่าน results.md → synthesize

## Reset
หลัง task เสร็จ Claude จะ reset task.md และ results.md กลับ status=empty
