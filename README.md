# 🧠 Visitor Management System – AI-Powered Real-Time Face Recognition

An AI-powered real-time Visitor Management System that automates visitor registration, identity verification, and live monitoring using deep learning, computer vision, and vector similarity search. The system integrates anti-spoofing, real-time tracking, WebSocket streaming, and hybrid database architecture to provide secure and intelligent visitor management.

---

# 🚀 Features

### 👤 Visitor Management
- Face-based visitor registration
- Automatic visitor check-in
- Current visitor tracking
- Visitor entry & exit logging
- Complete visitor history
- Visitor search functionality

### 🧠 Face Recognition
- Real-time face detection
- Face recognition using InsightFace embeddings
- Embedding aggregation for improved recognition
- ChromaDB vector similarity search
- Recognition cache for faster inference
- Re-identification memory for stable tracking

### 🛡️ Security
- Anti-spoofing detection using MiniFASNet (ONNX)
- Unknown visitor detection
- Snapshot capture for unknown visitors
- Duplicate recognition prevention

### 📊 Admin Dashboard
- Live monitoring dashboard
- Active session monitoring
- Current visitors table
- Unknown visitors management
- Visitor history
- Session history
- Live recognition status

### ⚡ Real-Time Processing
- Live webcam streaming
- WebSocket-based communication
- Real-time face tracking
- Zone-based visitor monitoring
- Automatic session management

---

# 🏗️ System Architecture

```
User Frontend (React)
        │
        ▼
 Webcam Streaming
        │
        ▼
 WebSocket Communication
        │
        ▼
 FastAPI Backend
        │
        ├───────────────┐
        │               │
        ▼               ▼
 Face Detection    Anti-Spoofing
 (InsightFace)     (MiniFASNet)
        │
        ▼
 Face Embedding
        │
        ▼
 Embedding Aggregation
        │
        ▼
 ChromaDB Vector Search
        │
        ▼
 Recognition Cache
        │
        ▼
 Re-ID Memory
        │
        ▼
 Visitor Logging
        │
        ▼
 MySQL Database
        │
        ▼
 Admin Dashboard Updates
```

---

# 🧰 Tech Stack

## Frontend

### User Frontend
- React.js
- Vite
- Axios
- WebSocket API

### Admin Frontend
- React.js
- Vite
- Axios
- React Router

---

## Backend

- FastAPI
- SQLAlchemy
- WebSockets
- OpenCV
- NumPy
- ONNX Runtime

---

## AI / ML

- InsightFace (buffalo_l)
- MiniFASNet (Anti-Spoofing)
- Face Embedding Aggregation
- Cosine Similarity Matching

---

## Databases

- MySQL (Structured Data)
- ChromaDB (Vector Embeddings)

---

# 📂 Project Structure

```
face-recog-sys/
│
├── admin-frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── antispoof/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── websocket_routes.py
│   │   ├── routes.py
│   │   ├── tracker.py
│   │   ├── models.py
│   │   └── main.py
│   │
│   ├── uploads/
│   ├── requirements.txt
│   └── run.py
│
├── user-frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── README.md
└── .gitignore
```

---

# ⚙️ Installation & Setup

## 1️⃣ Clone Repository

```bash
git clone https://github.com/Aditisharma1205/visitor-management-system.git

cd visitor-management-system
```

---

## 2️⃣ Backend Setup

```bash
cd backend

python -m venv venv
```

Activate virtual environment

### Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file inside `backend/app`

```env
DATABASE_URL=your_database_url
```

Run the backend

```bash
python run.py
```

or

```bash
uvicorn app.main:app --reload
```

---

## 3️⃣ User Frontend

```bash
cd user-frontend

npm install

npm run dev
```

---

## 4️⃣ Admin Frontend

```bash
cd admin-frontend

npm install

npm run dev
```

---

# 🧠 How It Works

1. User registers with facial images.
2. Face embeddings are generated using InsightFace.
3. Embeddings are stored in ChromaDB.
4. Live webcam frames are streamed via WebSocket.
5. Backend performs face detection.
6. Anti-spoofing validates the face.
7. Face embeddings are generated.
8. Embeddings are matched against ChromaDB.
9. Registered visitors are identified.
10. Unknown visitors are stored separately.
11. Visitor logs are automatically maintained.
12. Admin dashboard updates in real time.

---

# 🛡️ Anti-Spoofing

- MiniFASNet ONNX model
- Detects spoof attacks using printed photos or mobile screens
- Integrated directly into the real-time recognition pipeline
- Recognition proceeds only after successful liveness verification

---

# 📊 Database Design

## MySQL

### Users
- User Details
- Registered Face Information

### Visitor Logs
- Entry Time
- Exit Time
- Status
- Session Details

### Unknown Visitors
- Snapshot
- Detection Timestamp

### Sessions
- Recognition Sessions
- Session Statistics

---

## ChromaDB

Stores high-dimensional face embeddings for fast vector similarity search.

---

# 📌 Key Highlights

- Real-time AI-powered face recognition
- Anti-spoofing integrated recognition pipeline
- Hybrid database architecture (MySQL + ChromaDB)
- WebSocket-based live streaming
- Modular FastAPI backend
- Embedding aggregation for robust recognition
- Re-identification memory for stable tracking
- Unknown visitor management
- Live admin monitoring dashboard
- Production-style project architecture

---

# 🚀 Future Improvements

- JWT Authentication
- Multi-camera support
- Docker deployment
- GPU acceleration (CUDA)
- Redis-based distributed tracking
- Qdrant/Milvus vector database support
- Email/SMS notifications
- Analytics dashboard
- Cloud deployment (AWS/Azure)

---

# 👨‍💻 Author

**Aditi Sharma**

B.Tech Computer Science Engineering
