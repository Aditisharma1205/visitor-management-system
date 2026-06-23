# 🧠 VisionPass  
## AI-Powered Real-Time Face Recognition & Identity Tracking System

![Architecture](assets/architecture.png)

VisionPass is a real-time face recognition system built for continuous identity tracking using **WebSockets, InsightFace embeddings, ChromaDB vector search, MySQL, and session-based tracking logic**.

It processes live webcam streams and maintains identity consistency across frames using caching, clustering, and track-based persistence.

---

## 🚀 Key Capabilities

- User registration with face capture
- High-accuracy InsightFace embeddings
- Hybrid storage (MySQL + ChromaDB)
- Real-time WebSocket streaming
- Vector similarity-based recognition
- Track-based identity persistence
- Embedding clustering for noise reduction
- Recognition caching for performance optimization
- Structured visitor logging system

---

## 🏗️ System Architecture

![System Architecture](assets/architecture.png)

---

## ⚙️ System Flow

### 1. User Registration
Face Capture → Embedding Generation → MySQL + ChromaDB Storage

### 2. Real-Time Recognition
Webcam → WebSocket → Backend → Face Detection → Embedding → ChromaDB → Identity

### 3. Tracking Layer
Face → Track ID → Persistent Identity Across Frames

### 4. Clustering Layer
Frame Embeddings → Aggregation → Stable Identity Vector

### 5. Recognition Cache
Track ID → Cached Identity → Skip Re-Query

### 6. Visitor Logging
Identity Detected → Session Start → Session End → DB Log

---

## 🧰 Tech Stack

### Backend
- FastAPI
- WebSockets
- InsightFace
- ChromaDB
- MySQL
- NumPy

### Frontend
- React (Vite)
- WebSocket Client
- Webcam Integration
- Axios

---

## ⚡ Highlights

- Real-time streaming architecture
- Hybrid SQL + vector database system
- Track-based identity persistence
- Embedding clustering for stability
- Low-latency WebSocket pipeline
- Optimized caching system

---

## 🧠 Design Philosophy

VisionPass is built around **stream-based identity resolution**, not frame-by-frame recognition.

It ensures:
- Temporal consistency over raw detection
- Stable identity across frames
- Reduced redundant computation
- Scalable real-time inference

---

## 📊 System Summary

| Layer | Purpose |
|------|--------|
| Registration | Identity onboarding |
| Recognition | Face identification |
| Tracking | Identity persistence |
| Clustering | Embedding stability |
| Cache | Performance optimization |
| Logging | Session history |

---

## 🧾 Output

- Real-time identity recognition
- Persistent tracking across frames
- Structured visitor session logs
- Optimized inference pipeline

---

## 📦 Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
