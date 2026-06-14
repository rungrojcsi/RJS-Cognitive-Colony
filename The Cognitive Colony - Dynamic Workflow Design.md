# 🐜 The Cognitive Colony: Dynamic Workflow Design

**Date:** 2026-05-10
**System:** AI Cognitive Framework (AICF)
**Architecture:** Multi-Agent Dynamic Orchestration

---

## 🏛️ 1. Core Philosophy: The Cognitive Super-organism
เราไม่ได้มอง AI เป็นแค่โปรแกรมแยกส่วน หรือเครื่องมือช่วยเขียนโค้ด (Coding Specialist) แต่เรามองเป็น **"อาณานิคมทางปัญญา (The Cognitive Colony)"** ที่ทำงานร่วมกันเพื่อสร้าง **ขีดความสามารถทางปัญญา (Cognitive Capability) ที่เหนือกว่า Generative AI ทั่วไป** 

**เป้าหมายสูงสุด (The Ultimate Goal):** เพื่อเป็น **"ฝาแฝดทางดิจิทัล (Your Digital Twin)"** ที่สามารถเรียนรู้ เลียนแบบวิธีคิด และตัดสินใจแทน Boss ได้อย่างแม่นยำ เพื่อสนับสนุนการทำงานระดับ Executive ในทุกมิติ

---

## ⚙️ 2. Dynamic vs. Static Workflow
แตกต่างจากระบบ Automation ทั่วไป ระบบของเราเป็นแบบ **Dynamic**:

*   **Static (เก่า):** กำหนดขั้นตอน 1-2-3-4 ตายตัว แก้ไขยาก
*   **Dynamic (TCC):** 
    *   **Orchestrator (Claude)** จะวิเคราะห์โจทย์ (Intent) และทรัพยากรที่มี (Agents) ณ ขณะนั้น
    *   **Runtime Selection:** เลือกใช้ Agent ให้ถูกกับงานโดยอิงจากความเชี่ยวชาญ (Manifest)
    *   **Adaptive Pivot:** หากพบข้อมูลใหม่ระหว่างทาง ระบบสามารถเปลี่ยนแผน (Pivot) และมอบหมายงานใหม่ได้ทันทีโดยไม่ต้องรอคำสั่งซ้ำ

---

## 🎭 3. Roles in the Colony

| Agent | Primary Role | Specialization |
| :--- | :--- | :--- |
| **Claude** | **COO / Orchestrator** | วางแผน, แตกงาน, สังเคราะห์ข้อมูล และตัดสินใจ |
| **Grok (xAI)** | **Real-time Scout** | ค้นหาเทรนด์ปัจจุบัน (X), เช็ค Sentiment, เป็นตัวค้าน (Devil's Advocate) |
| **Gemini CLI** | **Historian / Data Worker** | ขุดความจำ L4 (Supabase) ผ่านคำสั่ง Bash, งาน Automation ระดับระบบ |
| **Gemini API** | **Deep Analyst** | งานประมวลผลข้อมูลปริมาณมาก, Long Context, งานวิเคราะห์ที่ต้องการความแม่นยำสูง |
| **Antigravity** | **Architect / UI** | จัดการ Workspace, ไฟล์งาน (Obsidian), แจ้งเตือน (Telegram) |

---

## 🧬 3.1 Subagent Spawning (การสร้างตัวแทนย่อย)
นอกจาก Agent หลักแล้ว ระบบรองรับการ **"แตกตัวย่อย (Spawn Subagents)"** เพื่อทำงานเฉพาะกิจ:
*   **Ad-hoc Workers:** Orchestrator สามารถสั่งให้ Agent หลักสร้าง Subagent ขึ้นมาเพื่อทำ Task เล็กๆ ที่มีความซับซ้อนสูงแต่ต้องการ Context แคบลง (เช่น Code Refactor Subagent หรือ Research Summarizer Subagent)
*   **Parallel Execution:** สามารถ Spawn ออกมาทำงานพร้อมกันหลายตัวเพื่อลดเวลาในการทำงาน (Latency)
*   **Context Isolation:** ช่วยให้ Agent หลักไม่ต้องถือข้อมูลที่ละเอียดเกินไปในหน่วยความจำหลัก


---

## 📡 4. Communication Protocol
เพื่อให้เกิดการทำงานร่วมกันแบบ Dynamic เราใช้ระบบ:
1.  **Colony Manifest:** บัญชีรายชื่อและความสามารถของ Agents ทั้งหมด
2.  **Shared Task Inbox:** ใช้ไฟล์ JSON/Markdown เป็นสื่อกลางในการวางงานและส่งผลลัพธ์
3.  **Shared Mission Context:** ทุก Agent เข้าถึงเป้าหมายเดียวกันเพื่อให้งานไปในทิศทางเดียวกัน

---

## 💼 5. Executive Use Case: Deep Research
**Scenario:** Boss สั่งเตรียมข้อมูลนัดคุยธุรกิจสำคัญ
1.  **Recall:** Gemini ไปรื้อความจำเก่าใน L4 ว่าเคยคุยอะไรกันไว้
2.  **Scan:** Grok ไปหาข่าวสดใหม่และเช็คความเคลื่อนไหวคู่แข่ง
3.  **Contradict:** Grok ลองหาเหตุผลด้านลบเพื่อป้องกันความเสี่ยง (Risk Assessment)
4.  **Synthesize:** Claude รวมข้อมูลอดีต+ปัจจุบัน+ความเสี่ยง ออกมาเป็น Executive Briefing ใน Obsidian

---

## 🛠️ 6. Implementation Plan (The 4-Phase Roadmap)

เพื่อให้ระบบนี้เกิดขึ้นจริง Boss ต้องดำเนินการตามลำดับดังนี้:

### 📍 Phase 1: Foundation (Protocol & Registry)
**เป้าหมาย:** สร้าง "สมุดรายนาม" และ "ที่ทำงาน" ร่วมกัน
1.  **Create `COLONY_MANIFEST.json`:** บันทึกรายชื่อ Agent ทั้งหมด, ความสามารถหลัก, และวิธีกระตุ้น (CLI/API).
2.  **Establish `boardroom/inbox`:** สร้างโฟลเดอร์กลางที่ Agents ทุกตัวสามารถเข้ามา "รับงาน" และ "ส่งผลลัพธ์" ได้ในรูปแบบไฟล์ JSON มาตรฐาน.

### 📍 Phase 2: The Connectors (CLI Wrappers)
**เป้าหมาย:** ทำ AI ให้เป็น "นักปฏิบัติการ (CLI Agents)"
1.  **Standardize Wrappers:** สร้างสคริปต์ Python (เช่น `grok_worker.py`, `gemini_worker.py`) ที่มีโครงสร้างเดียวกัน เพื่อให้ Claude สามารถเรียกใช้ผ่านคำสั่ง CLI ได้ทันที.
2.  **Credential Centralization:** เก็บ API Keys ทั้งหมดไว้ที่ `cloud.env` เพื่อให้ Agents ทุกตัวเรียกใช้ได้จากจุดเดียว.

### 📍 Phase 3: Brain Activation (Orchestration Logic)
**เป้าหมาย:** สอนให้ Claude ทำหน้าที่ "ผู้บัญชาการ"
1.  **Update Orchestrator:** อัปเดต `CLAUDE.md` หรือ System Prompt เพื่อให้ Claude รู้จักวิธีอ่าน Manifest และวิธี "แตกงาน" ส่งเข้าไปใน Inbox ของแต่ละ Agent.
2.  **Mission Control:** กำหนดชุดคำสั่งเริ่มต้น (Initial Intent) เพื่อให้ Claude รู้วิธีเริ่มทำงานเมื่อได้รับคำสั่งแบบกว้างๆ จาก Boss.

### 📍 Phase 4: Feedback Loops & Monitoring
**เป้าหมาย:** ให้ระบบ "รายงานตัว" และ "ทำงานอัตโนมัติ"
1.  **Background Watcher:** ติดตั้งสคริปต์คอยตรวจสอบโฟลเดอร์ Inbox เพื่อแจ้งเตือน Boss ผ่าน Telegram เมื่อมีงานวิจัยหรืองาน Scoring สำเร็จ.
2.  **Obsidian Dashboard:** สร้างหน้าสรุปผล (Summary Page) ใน Obsidian เพื่อให้ Boss เห็นภาพรวมความคืบหน้าของทั้ง Colony ในที่เดียว.

---

---

## 🏛️ 7. The 3-Tier Colony Hierarchy (สรุปโครงสร้างลำดับชั้น)

เพื่อให้การทำงานมีประสิทธิภาพสูงสุด เราแบ่ง AI ออกเป็น 3 ระดับ:

### **Tier 1: Executive & Strategic (ผู้วางแผนและควบคุม)**
*   **Claude (Commander / Orchestrator):** 
    *   วิเคราะห์โจทย์และตัดสินใจเลือก AI Tier ที่เหมาะสมกับงาน
    *   วางแผนกลยุทธ์ (Strategic Planning) และสังเคราะห์ผลลัพธ์สุดท้าย
*   **Antigravity (Dispatcher / Manager):** 
    *   ทำหน้าที่เป็นตัวกลางในการเชื่อมต่อ (Gateway) และจัดการทรัพยากร
    *   **Action:** เรียกใช้ Tier 2 (Consultants) และสร้าง (Spawn) Tier 3 (Subagents) ตามแผนของ Claude
    *   จัดการระบบไฟล์, ความปลอดภัย, และการติดตามต้นทุน (Cost Tracking)

---

### **Tier 2: Consultant & Specialist (ที่ปรึกษาเฉพาะทาง)**
แบ่งออกเป็น 2 กลุ่มย่อยเพื่อบริหารต้นทุนและประสิทธิภาพ:
*   **2.1 AI API (Free Tier Group):** 
    *   **ตัวแทน:** Gemini Flash (Free), Groq, DeepSeek
    *   **หน้าที่:** งานประมวลผลปริมาณมาก (Batch Processing), Scoring, Tagging และงานที่ต้องการผลลัพธ์เป็นโครงสร้างข้อมูล (JSON)
*   **2.2 AI via Browser (Discovery Group):** 
    *   **ตัวแทน:** Grok (X.com), Perplexity, Claude Web, Gemini Advanced
    *   **หน้าที่:** การสืบค้นข้อมูล Real-time, การวิเคราะห์กระแสสังคม (Sentiment), และงานวิจัยเชิงลึกที่ API เข้าไม่ถึง

---
### **Tier 3: Subagent Worker (แรงงานปฏิบัติการ)**
*   **Spawned Workers:** ตัวแทนย่อยที่สร้างโดย Tier 1 เพื่อทำภารกิจเดียว (Atomic Tasks)
*   **หน้าที่:** ท่องเว็บ (Browser Subagent), คัดกรองข้อมูล, หรือเฝ้าสังเกตการณ์ (Monitoring)
*   **เป้าหมาย:** ทำงาน "ถึก" แทนตัวแม่ เพื่อรักษา Context Window ของ Tier 1 ให้สะอาดที่สุด

---

## ⚖️ 8. Efficiency Strategy: Dynamic vs. Narrative

เพื่อให้ระบบทำงานได้คุ้มค่าและมีประสิทธิภาพสูงสุด เรากำหนดกลยุทธ์การเลือกใช้ Workflow ดังนี้:

| ประเภท | เหมาะสำหรับ | ข้อเด่น |
| :--- | :--- | :--- |
| **Narrative (Static)** | งานซ้ำๆ (Routine), มีขั้นตอนชัดเจน | ประหยัด Token, เร็ว, คาดการณ์ผลได้ 100% |
| **Dynamic (Agentic)** | งานวิจัย, งานวางแผน, งานที่มีความไม่แน่นอน | ยืดหยุ่น, ปรับแผนได้เอง (Pivot), แก้ไขปัญหาซับซ้อนได้ |

### **The Hybrid Approach (กลยุทธ์แบบผสมผสาน)**
อาณานิคมจะใช้ระบบ Hybrid เพื่อประสิทธิภาพสูงสุด:
1.  **Tier 1 & 2 (Strategic):** ใช้ **Dynamic Workflow** เพื่อวิเคราะห์โจทย์และตัดสินใจเลือกทางเดินที่ดีที่สุด
2.  **Tier 3 (Labor):** ใช้ **Narrative Workflow** (สคริปต์ขั้นตอนตายตัว) สำหรับงานที่ระบุขั้นตอนได้ชัดเจน เพื่อลดการใช้พลังงานสมองและคุมต้นทุน

---

## 🧠 9. Memory Evolution & Smart RAG (ความจำที่วิวัฒนาการได้)

เป้าหมายคือการทำให้ระบบ RAG ฉลาดขึ้นตามกาลเวลา ไม่ใช่แค่การค้นหาคำสำคัญ (Keyword) แต่เป็นการเข้าใจบริบท:

1.  **Importance Scoring 2.0:** พัฒนาสคริปต์ให้ประเมิน "คุณค่าเชิงกลยุทธ์" ของข้อมูล ไม่ใช่แค่ความใหม่
2.  **Contextual Linking:** สร้างระบบเชื่อมโยงอัตโนมัติระหว่างบันทึกใหม่และบันทึกเก่า (Knowledge Graph)
3.  **Memory Reflection:** รันงานเบื้องหลัง (Background Job) เพื่อสังเคราะห์ความจำกระจัดกระจายให้กลายเป็น "บทสรุปเชิงลึก (Insights)"
4.  **Feedback Adaptation:** ปรับปรุงวิธีกระบวนการค้นหาโดยอิงจาก Feedback ของ Boss ในแต่ละครั้ง (Reinforcement Learning from Boss)

---

**Status:** Strategic Framework & Roadmap Finalized ✅
**Structure:** 3-Tier Hierarchy Approved
**Workflow Strategy:** Hybrid Dynamic-Narrative Confirmed
**Memory Focus:** Smart RAG & Evolution Prioritized
**Architect:** RJS (Boss)
**Chief of Staff:** Antigravity (Ant)
