from typing import Dict, Any, Optional

# Single active session state (simple version)
LIVE_STATE: Dict[str, Any] = {
    "session_id": None,
    "frame": None,              # base64 encoded image
    "active_tracks": [],        # current frame detections
    "seen_track_ids": set(),    # optional (debug only)
    "status": "IDLE"            # IDLE / ACTIVE / ENDED
}


def set_live_state(
    session_id: int,
    frame: Optional[str],
    active_tracks: list
):
    """
    Called every websocket frame.
    Overwrites current live view of system.
    """

    LIVE_STATE["session_id"] = session_id
    LIVE_STATE["frame"] = frame
    LIVE_STATE["active_tracks"] = active_tracks
    LIVE_STATE["status"] = "ACTIVE"


def clear_live_state(session_id: Optional[int] = None):
    """
    Called when websocket disconnects or session ends.
    """
    LIVE_STATE["session_id"] = None
    LIVE_STATE["frame"] = None
    LIVE_STATE["active_tracks"] = []
    LIVE_STATE["seen_track_ids"] = set()
    LIVE_STATE["status"] = "IDLE"


def get_live_state():
    return LIVE_STATE