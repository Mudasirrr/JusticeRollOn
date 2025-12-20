# ⚖️ JusticeRollOn  
### *Empowering Citizens · Enabling Justice · Ensuring Transparency*

---
[Website:](https://proceeding-justicerollon.onrender.com/)


## 🌍 Vision & Slogan

**JusticeRollOn** envisions a world where **access to justice is transparent, inclusive, and technology-driven**.  
The platform empowers ordinary citizens to raise legal and civic issues while ensuring accountability through professional verification and administrative oversight.

> *“Justice should not be delayed, hidden, or inaccessible — it should roll on for everyone.”*

---

## 🎯 Project Aim

The primary aim of **JusticeRollOn** is to:

- Democratize access to justice  
- Provide a secure platform for legal evidence submission  
- Enable transparent petition handling  
- Support civic participation through verified public visibility  

This project aligns with **UN Sustainable Development Goal 16 (Peace, Justice & Strong Institutions)**.

---

## 📘 Introduction

Many individuals face barriers in accessing justice due to:
- Complex legal systems  
- High costs  
- Lack of transparency  
- Limited access to legal professionals  

**JusticeRollOn** addresses these challenges by introducing a **LegalTech civic platform** that bridges the gap between citizens, lawyers, and governing authorities using modern web technologies.

---

## 🧾 Project Description

**JusticeRollOn** is a **full-stack web application** consisting of:

- **Frontend**: WordPress (user interaction & content visibility)
- **Backend**: Django (this repository)
- **Database**: SQLite (development), scalable to cloud databases in production

This repository contains the **Django backend**, which handles:

- User authentication & authorization
- Role-based access control
- Evidence upload & validation
- Petition lifecycle management
- Secure API communication
- Administrative moderation workflows

---


## 👥 User Roles & Responsibilities

### 👤 Citizen
- Register and log in
- Upload legal evidence (images, PDFs, documents)
- Create justice-related petitions
- Track petition status

### ⚖️ Lawyer
- Review and verify submitted evidence
- Moderate petitions
- Provide legal validation

### 🛡️ Administrator
- Approve or reject petitions
- Publish verified petitions to the **Justice Index**
- Ensure ethical, legal, and platform compliance

### 🌍 Public User
- View verified and published petitions
- Explore the Justice Index
- Participate in civic transparency

---

---

## 🧰 Requirements

Before setting up **JusticeRollOn**, ensure your system meets the following requirements.

### 🐍 Python
- **Python version**: `3.10 or higher` (Recommended: **Python 3.11**)
- Download: https://www.python.org/downloads/

> ⚠️ *Make sure Python is added to PATH during installation.*

---

### 📦 Required Python Libraries

The project depends on the following libraries:

- **Django>=4.2** – Backend web framework  
- **djangorestframework** – REST API development  
- **django-cors-headers** – Cross-Origin Resource Sharing support  
- **python-dotenv** – Environment variable management  
- **Pillow** – Image processing for evidence uploads  
- **python-docx** – Handling `.docx` documents  
- **xhtml2pdf** – PDF generation  
- **gunicorn** – WSGI HTTP server (production)  
- **whitenoise** – Static file handling  

All dependencies are listed in **`requirements.txt`**.

---

## ⚙️ Installation & Setup

Follow the steps below to install and run the project locally.

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Mudasirrr/JusticeRollOn.git
cd JusticeRollOn


## 🏗️ System Architecture

```-
[ WordPress Frontend ]
        ↓ REST APIs
[ Django Backend (This Repository) ]
        ↓ Django ORM
[ Database (SQLite / Cloud DB) ]
