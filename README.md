إليك ملف README.md مُعاد # 🏗️ Wakeel Mihna PRO (mihna-core)
> **The First Autonomous Geo-Global AI-ConTech & Field Digital Twin Platform**

[![Google Cloud Run](https://img.shields.io/badge/Google%20Cloud-Cloud%20Run-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Built with Gemini](https://img.shields.io/badge/Built%20with-Gemini%20API-8E75B2?logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Architecture: Multi-Agent](https://img.shields.io/badge/Architecture-Multi--Agent-00C853)](https://github.com/AaydFaisalAbdoMohammed/mihna-core)

---

## 🌟 Executive Summary
**Wakeel Mihna PRO** is an enterprise-grade, multi-agent AI ConTech ecosystem designed to bridge project engineering, automated structural risk assessment, real-time quantity surveying (BOQ), and localized contractor matching into a unified digital twin pipeline.

Driven by advanced **Google Gemini AI models**, the platform converts raw engineering specifications into high-precision room distributions, mathematical finite-element stress simulations, automated payroll & cost calculations, and instant cryptographic contract verification.

> 🚀 **Engineering Note:** Architected, developed, containerized, and deployed to **Google Cloud Run** 100% via a mobile smartphone device under resource-constrained conditions.

---

## 🚀 Key Capabilities & Modules

### 1. 📐 AI-ConTech & Generative Spatial Planning
* **Generative Floor Plans:** Automatically processes complex engineering inputs to project optimal room distributions, spatial square-meter allocations, and target budget constraints.
* **Automated BOQ & Cost Estimation:** Instantaneous line-item calculation for raw materials (reinforcement steel, ready-mix concrete, masonry blocks, and finishing coatings) with automatic risk-buffer adjustments.

### 2. 🔬 Physics & Structural Stress Engine (Live Twin)
* Integrated mathematical validation engines executing structural stress and deflection verification:
  * **Euler-Bernoulli Beam Deflection:**
    $$EI \frac{d^4 v}{d x^4} = q(x)$$
  * **Dynamic Seismic Load Equation:**
    $$M\ddot{u} + C\dot{u} + Ku = -F(t)$$

### 3. 🌐 Geo-Localized ConTech Marketplace & Escrow
* **Dynamic Bidding:** Connects geospatial field data with verified local contractors.
* **Instant Notifications:** Asynchronous real-time alerts via **WhatsApp API** and **Telegram Bot API** for site logs and budget threshold updates.
* **Cryptographic Security:** Smart contract digital signature generation utilizing HMAC SHA512 hashing protocols.

---

## 🏗️ Production System Architecture

```text
                    +------------------------------------+
                    |        Client Interface            |
                    | (Multi-Language / Dark & Light)    |
                    +-----------------+------------------+
                                      |
                                      v
                    +-----------------+------------------+
                    |    Python Enterprise Core App      |
                    |   (Google Cloud Run Container)     |
                    +--------+-----------------+---------+
                             |                 |
            +----------------+                 +-----------------+
            |                                                    |
            v                                                    v
+-----------+-----------+                               +--------+----------+
|  Google Gemini API    |                               |  Database Layer   |
| (Multi-Agent Logic &  |                               | (Cloud SQL /      |
| Structural Reasoning) |                               | PostgreSQL /      |
+-----------------------+                               |  Supabase RLS)    |
                                                        +-------------------+


```
## 🛠️ Technology Stack
| Domain | Technologies Used |
|---|---|
| **Core & Backend** | Python, Multi-Agent Logic, HMAC SHA512 Cryptography |
| **AI Framework** | Google Gemini API (Structured JSON & Reasoning Workflows) |
| **Database & Analytics** | PostgreSQL, Google Cloud SQL, Supabase RLS |
| **Cloud & Infrastructure** | Google Cloud Run, Docker Containers, GitHub Actions CI/CD |
| **Messaging & Telemetry** | Telegram Bot API, WhatsApp Notifications API |
## 📂 Repository Structure
```text
mihna-core/
├── .devcontainer/        # Local development environment container configuration
├── .github/workflows/   # Automated CI/CD pipelines for Google Cloud Run deployment
├── data/plans/           # RAG knowledge base & baseline engineering plan templates
├── Dockerfile            # Container definition optimized for Google Cloud Run
├── app.py                # Core application entry point & interface router
├── ai.py                 # LiveTwinEngine for structural physics & stress analysis
├── cloudsql_utils.py     # Cloud SQL / PostgreSQL enterprise connector
├── auth.py               # Authentication, access control & multi-tenant isolation
├── utils.py              # Cryptographic smart contract hash generators (SHA512)
├── config.py             # Enterprise secrets & service key handlers
└── requirements.txt      # Production runtime dependencies

```
## 🏃 Quick Start & Local Spin-up
### Prerequisites
 * Python 3.10+
 * Google Gemini API Key
 * PostgreSQL / Supabase Instance (Optional for local testing)
### Installation
 1. **Clone the repository:**
   ```bash
   git clone [https://github.com/AaydFaisalAbdoMohammed/mihna-core.git](https://github.com/AaydFaisalAbdoMohammed/mihna-core.git)
   cd mihna-core
   
   ```
 2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   
   ```
 3. **Configure Environment Variables:**
   Create a .env file or export environment variables:
   ```bash
   export GEMINI_API_KEY="your_gemini_api_key"
   
   ```
 4. **Run the Application:**
   ```bash
   streamlit run app.py
   
   ```
## 📄 License
Distributed under the **MIT License**. See LICENSE for more information.
```

---

