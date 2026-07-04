// src/api/config.js

// Change this IP to the machine running FastAPI
export const SERVER_IP = "127.0.0.1";

// REST API
export const API_URL = `http://${SERVER_IP}:8000`;

// WebSocket
export const WS_URL = `ws://${SERVER_IP}:8000/ws`;