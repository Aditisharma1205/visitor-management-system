🧠 VisionPass
AI-Powered Real-Time Face Recognition & Identity Tracking System

VisionPass is a real-time face recognition system built for continuous identity tracking using WebSockets, InsightFace embeddings, ChromaDB vector search, and session-based tracking logic. It processes live webcam streams and maintains identity consistency across frames using caching, clustering, and track-based persistence.

🚀 Key Capabilities
👤 User registration with face capture
🧠 High-accuracy face embeddings using InsightFace
🗄️ Hybrid storage system (MySQL + ChromaDB)
⚡ Real-time webcam streaming via WebSockets
🔍 Vector similarity-based identity recognition
🧩 Track-based identity persistence across frames
📦 Embedding clustering for noise reduction
⚡ Recognition caching for performance optimization
📊 Structured visitor logging system
🏗️ System Architecture

VisionPass is built as a multi-layer identity recognition pipeline:

1. User Registration Layer

Each user is enrolled into the system through face capture and embedding generation.

Flow:

User Registration
      ↓
Face Capture (Image Input)
      ↓
InsightFace Embedding Generation
      ↓
MySQL → User Metadata Storage
ChromaDB → Vector Embedding Storage

Purpose:

Maintain structured user records (MySQL)
Enable fast semantic face search (ChromaDB)
2. Real-Time Recognition Layer

The system processes live video streams using WebSockets for low-latency inference.

Flow:

Webcam Stream (Frontend)
        ↓
WebSocket Transmission
        ↓
Backend Frame Processing
        ↓
Face Detection (InsightFace)
        ↓
Embedding Extraction
        ↓
ChromaDB Similarity Search
        ↓
Identity Resolution

Output:

Real-time identity detection from live camera feed
Instant mapping of faces to registered users
3. Tracking & Identity Persistence Layer

To ensure stability across frames, detected faces are assigned persistent track identities.

Flow:

Detected Face
      ↓
Track Assignment (Track ID)
      ↓
Continuous Frame Association
      ↓
Track Persistence Logic

Capabilities:

Maintains identity across consecutive frames
Reduces repeated recognition calls
Stabilizes detection under motion or occlusion
4. Embedding Clustering Layer

Multiple embeddings from the same identity are aggregated to improve robustness.

Flow:

Frame Embeddings
      ↓
Temporal Aggregation
      ↓
Clustered Representation
      ↓
Refined Identity Vector

Impact:

Reduces noise from lighting, angle, and blur
Improves recognition consistency
Produces more stable identity representation
5. Recognition Cache Layer

To optimize performance, repeated recognition calls are minimized using caching.

Flow:

Track ID → Identity Match
      ↓
Cache Storage
      ↓
Reuse Identity for Subsequent Frames

Benefit:

Reduces redundant vector database queries
Improves real-time FPS performance
Stabilizes identity output over time
6. Visitor Logging System

The system maintains structured logs of identity activity.

Data Stored:

User ID
Entry Time
Exit Time
Session Status

Flow:

Identity Detected → Session Start
Identity Lost → Session End
Log Stored in Database
🧰 Tech Stack
Backend
FastAPI
WebSockets
InsightFace
ChromaDB (Vector Database)
MySQL
NumPy
Frontend
React (Vite)
WebSocket Client
Webcam Integration
Axios
⚙️ System Highlights
Real-time face recognition pipeline optimized for streaming input
Hybrid database architecture for structured + vector storage
Track-based identity persistence for temporal consistency
Embedding clustering for robust recognition under variation
Low-latency WebSocket communication pipeline
Scalable recognition caching layer for performance efficiency
🧠 Core Design Philosophy

VisionPass is designed around a streaming identity resolution model, where:

Recognition is not frame-based
Identity is not re-evaluated unnecessarily
Temporal consistency is prioritized over per-frame accuracy
System stability is achieved through tracking + caching + clustering layers
📊 System Summary
Layer	Purpose
Registration	Identity onboarding
Recognition	Real-time face identification
Tracking	Temporal consistency
Clustering	Embedding stabilization
Cache	Performance optimization
Logging	Session history
🧾 Output

VisionPass produces:

Live identity recognition
Persistent track-based user mapping
Structured visitor session logs
Optimized real-time inference pipeline
