# 🧘 Fitra – Online Coaching Platform (Django) 🚀

**Fitra** is an online coaching platform built with **Django**.  
It showcases available coaching packages and allows users to register through a detailed form, upload progress photos, and activate their account via **email verification**.

The project is currently **Work in Progress (WIP)** and will be expanded with **online payments** and additional automation features.
## ✨ Key Features

- 🏠 **Landing Page**
  - Displays: logo, slogan, brief section, about-us section, footer, social links
  - Shows **success stories** and **available packages**

- 📦 **Packages System**
  - Packages include pricing (before/after), duration, and image
  - Packages support pros/cons using Many-to-Many relations:
    - Advantages ✅
    - Disadvantages ⚠️

- 📝 **Registration Form**
  - Collects detailed user info (age, height, weight, goals, plan, etc.)
  - Supports uploading multiple images (progress photos)

- 📧 **Email Verification**
  - Activation link is generated using `TimestampSigner`
  - Accounts are stored as inactive until verified (`is_activated=False`)

- 🌍 **Multilingual Support**
  - The website supports **Arabic ↔ English** translations (i18n)
## 🔐 Email Activation Flow

1. User submits the registration form.
2. A `Member` record is created with `is_activated = False`.
3. The system sends an email containing an activation link.
4. When the user opens the activation link:
   - If the token is valid (within **24 hours**) → the account becomes active ✅
   - If the token is expired/invalid → the inactive record is deleted ❌

This keeps the database clean from unverified or fake registrations.
## 🧱 Data Model (High-Level)

### Website Content (Settings App)
- `Info` (logo, slogan)
- `Brief` (title, content, image)
- `AboutUs` (content, image)
- `Footer` (slogan, image)
- `SocialLinks` (YouTube, WhatsApp, Facebook, Instagram, TikTok, Telegram)
- `SuccessfullStories` (before/after images)
- `Packadges` with:
  - price before/after, duration, image
  - advantages & disadvantages (many-to-many)

### Members (Coaching Registration)
- `Member` (full profile + plan + lifestyle details + contact info)
- `Goals` (multiple goals per member)
- `Picture` (multiple images per member)
- `Governorate` (place of living)
## 🧭 Roadmap (Next Features)

- 💳 **Online Payments**
  - Allow users to pay for coaching packages securely
  - Connect package selection to payment confirmation

- ⏳ **Auto-cleanup for unverified users**
  - If a user does not verify their email within **24 hours**:
    - delete the inactive account automatically (scheduled job)

- 🛡️ Security & UX improvements
  - Better validation and error messaging
  - Stronger duplicate checks and anti-spam protection
## ▶️ Run Locally

> Update these commands based on your actual project structure.

```bash
# 1) Create and activate a virtual environment
python -m venv venv
# Windows:
venv\\Scripts\\activate
# Linux/Mac:
source venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Apply migrations
python manage.py migrate

# 4) Run the server
python manage.py runserver
