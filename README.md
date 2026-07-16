# Mihna-agent
Autonomous AI PM converting vague ideas to structured MVP plans (tasks, stack, priorities) in seconds using Gemini 2.5 Flash. Live web app, Supabase sync &amp; Telegram alerts. Built for XPRIZE.
# 🧠 Mihna-Agent: The Autonomous AI Technical Product Manager

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](رابط_التطبيق_الخاص_بك)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Built with Gemini](https://img.shields.io/badge/Built%20with-Gemini%202.5%20Flash-4285F4?logo=google)](https://ai.google.dev/)

## 🚀 The Problem We Solve
**70% of freelancers and startups fail due to vague project scoping.** Writing a clear, actionable project plan takes days and requires deep technical expertise. This is the #1 bottleneck in freelance platforms.

## 💡 Our Solution: An Agentic Workflow
**Mihna-Agent is an autonomous AI agent that replaces the technical product manager.** Simply describe your project idea in plain English (or Arabic), and the agent generates a **complete, structured MVP plan** in under 3 seconds, including:
- ✅ A professional executive summary
- ✅ A suggested tech stack (Flutter, Next.js, Supabase, etc.)
- ✅ 5-7 detailed technical tasks with estimated days and priorities (High/Medium/Low)

## 🌟 Why Mihna-Agent Wins (لجنة التحكيم)
- **Speed:** Reduces project scoping time from days to 3 seconds.
- **Accuracy:** Enforces a rigid, validated structure that ensures high-quality output.
- **Actionable:** Doesn't just talk; it saves data to the database and alerts the team instantly via Telegram.

## 🏗️ Production-Ready Architecture
- **AI Engine:** Google Gemini 2.5 Flash (using Structured Prompting to output pure JSON).
- **Frontend:** Interactive Web App built with Streamlit.
- **Database:** Supabase (PostgreSQL) for storing projects and tasks.
- **Alerts:** Real-time Telegram bot notifications to the admin on every new project.
- **Deployment:** Hosted on Streamlit Community Cloud.

## 🎯 How It Works (The Demo)
1.  **User Input:** The client enters their name, project idea, budget, and timeline.
2.  **AI Processing:** The agent analyzes the text using Gemini and generates a structured JSON plan.
3.  **Sync & Alert:** The plan is saved to Supabase, and an instant notification is sent to the founder's Telegram.
4.  **Download:** The client can download the plan as JSON or a readable text file.

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **AI:** Google Gemini API (gemini-2.5-flash)
- **Database:** Supabase (PostgreSQL)
- **Notifications:** Telegram Bot API
- **Language:** Python

## 🏆 XPRIZE Alignment
This project addresses the **"Entrepreneurship & Job Creation"** category by automating the most time-consuming part of project management, allowing freelancers to focus on execution and enabling non-technical founders to launch their visions rapidly.

## 📂 Repository Structure
```text
Mihna-agent/
├── app.py             # The core Streamlit application
├── requirements.txt   # Project dependencies
├── .gitignore         # Files to ignore (e.g., .env)
└── README.md          # Project documentation
