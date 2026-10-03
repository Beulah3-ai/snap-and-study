# 📚 Snap & Study

### Snap it. Understand it. Study smarter.

Snap & Study is an AI-powered study assistant that helps students understand questions, diagrams, handwritten notes, textbook pages, formulas, code, and other study materials.

Students can upload a study image or type a question, and Snap & Study uses Google Gemini to provide a clear, simple, student-friendly explanation. The application also integrates Twilio WhatsApp to send study explanations directly to the student's WhatsApp.

---

## ✨ Features

- 📸 Upload study questions, diagrams, notes, and textbook pages
- 💬 Ask questions using text
- 🤖 AI-powered explanations using Google Gemini
- 🧠 Simple, student-friendly explanations
- 📝 Step-by-step solutions for problems
- 📊 Explanation of diagrams and important concepts
- 📚 Summarization of study notes and textbook content
- 📲 Send study explanations to WhatsApp using Twilio
- 🔐 Secure API credential management using Streamlit secrets

---

## 🏗️ Application Architecture

```text
Student
   │
   ├── Upload Image
   │
   └── Type Question
          │
          ▼
   ┌─────────────────┐
   │    Streamlit    │
   │       App       │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │  Google Gemini  │
   │   Multimodal AI │
   └────────┬────────┘
            │
            ▼
    Study Explanation
            │
       ┌────┴────┐
       │         │
       ▼         ▼
    Display    Twilio
 Explanation   WhatsApp
                 │
                 ▼
            Student's
             WhatsApp
live demo:  "https://snap-and-study-yegg7hmiqpe37zgptwugur.streamlit.app/"
