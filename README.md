🧠 VisionPass – AI-Powered Real-Time Face Recognition & Visitor Management System

A real-time AI-based face recognition system that automates visitor tracking using webcam input, deep learning models, and vector-based face matching. The system integrates anti-spoofing, live tracking, and structured logging to create a secure and intelligent identity management pipeline.

🚀 Features
🎥 Real-time webcam face detection
🧠 Face recognition using InsightFace embeddings
🛡️ Anti-spoofing detection using MiniFASNet (ONNX)
👤 User registration with face embedding storage
📊 Visitor entry & exit logging system
🔍 Fast face matching using ChromaDB vector search
🗄️ Structured data storage using MySQL
⚡ Real-time communication using WebSockets
📸 Snapshot capture for entries, exits, and unknown users
📱 Interactive React-based dashboard

🏗️ System Architecture
Webcam (React Frontend)
        ↓
WebSocket Streaming
        ↓
FastAPI Backend
        ↓
Face Detection (InsightFace)
        ↓
Anti-Spoofing (MiniFASNet)
        ↓
Embedding Generation
        ↓
ChromaDB (Face Matching)
        ↓
MySQL (User + Logs Storage)
        ↓
React Dashboard Updates

🧰 Tech Stack

Frontend
React.js
react-webcam
WebSocket API
Tailwind CSS

Backend
FastAPI (Python)
WebSockets
SQLAlchemy
AI / ML
InsightFace (buffalo_l model)
MiniFASNet (ONNX Runtime)
NumPy / Cosine Similarity

Databases
MySQL (structured data)
ChromaDB (vector embeddings)


📂 Project Structure
Face-Recognition-System/
│
├── backend/
│   ├── app/
│   │   ├── services/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── websocket/
│   │   └── main.py
│   ├── reid_memory.py
│   ├── tracker.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── Recognize.jsx
│   └── package.json
│
├── embeddings/
├── uploads/
├── README.md


⚙️ Installation & Setup
1. Clone Repository
git clone https://github.com/your-username/visionpass.git
cd visionpass
2. Backend Setup
cd backend
python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt

Run server:

uvicorn app.main:app --reload
3. Frontend Setup
cd frontend
npm install
npm start
4. Database Setup (MySQL)

Create database:

CREATE DATABASE visionpass;

Import tables (handled via SQLAlchemy models).

🧠 How It Works
User registers with face image
System extracts face embedding using InsightFace
Embedding is stored in ChromaDB
Live webcam feed sends frames via WebSocket
Backend detects face and extracts embedding
Embedding is matched with stored vectors
If match found → user identified
Otherwise → marked as unknown visitor
Entry/exit logs stored in MySQL

🛡️ Anti-Spoofing
Uses MiniFASNet ONNX model
Detects fake faces (photo/video attacks)
Works with track-based smoothing for stability

📊 Database Design
Users Table
id
name
embedding_path
photo_path
Visitor Logs
id
user_id
entry_time
exit_time
status
Unknown Visitors
id
timestamp
snapshot_path

📌 Key Highlights
Real-time AI pipeline
Hybrid database architecture (MySQL + ChromaDB)
Anti-spoofing integrated system
WebSocket-based streaming
Production-style modular backend design

🚀 Future Improvements
GPU acceleration (CUDA support)
Redis-based distributed tracking
JWT authentication system
Cloud storage (AWS S3) for images
Scalable vector database (Qdrant/Milvus)

👨‍💻 Author

Built project focused on real-time AI systems, computer vision, and scalable backend architecture.

📄 License

This project is for academic and learning purposes.
