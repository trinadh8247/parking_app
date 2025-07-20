# 🚗 Park Karo – Smart Parking Management System

**Park Karo** is a web-based smart parking management system built using **Flask**, designed to help admins manage parking lots and users book parking spots efficiently.

---

## 📁 Project Structure

```
parking_app/
│
├── app.py
├── requirements.txt
├── static/
│   ├── css/
│   │   └── (admin.css, login.css, etc.)
│   └── images/
│       └── (background images like register.jpeg)
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── admin.html
│   └── ...
├── applications/
│   ├── database.py
│   └── controllers.py
└── README.md
```

---

## 🚀 Features

- Admin dashboard with parking lot management
- View/add/edit/delete parking lots and slots
- View active and inactive lots
- Profile modal and edit feature
- User login and registration system
- Clean UI with modal-based popups

---

## 🧰 Tech Stack

- **Backend:** Flask, SQLAlchemy
- **Frontend:** HTML, CSS, Bootstrap
- **Database:** SQLite

---

## 🛠️ Setup Instructions

1. **Clone the repo**

```bash
git clone https://github.com/trinadh8247/parking_app.git
cd park-karo
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run the Flask app**

```bash
python app.py
```

The app will start on `http://127.0.0.1:5000`.

---


## 📌 Notes

- Make sure the `register.jpeg` and other images are present in `static/images/`.
- Admin profile modal uses Bootstrap, ensure Bootstrap JS and CSS are correctly linked in `base.html`.

---

## 📞 Contact

For issues or questions, contact [your-trinadh2026@gmail.com].

---

## 📄 License

MIT License
