from app.models import CameraSession, VisitorLog
from app.utils.time_utils import now_ist
from sqlalchemy.orm import Session


def start_session(db: Session):
    session = CameraSession(
        start_time=now_ist(),
        status="ACTIVE"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def end_session(db: Session, session_id: int):
    session = db.query(CameraSession).filter(
        CameraSession.id == session_id
    ).first()

    if not session:
        return None

    session.end_time = now_ist()
    session.status = "ENDED"

    # NOTE: this counts logs linked via VisitorLog.session_id. Nothing in
    # the websocket handler currently sets session_id when it calls
    # create_entry/create_exit, so today this will always come back as 0
    # until that wiring is added. Fixed the query logic (previous version
    # referenced VisitorLog.track_id and status == "Known"/"Unknown",
    # neither of which exist on the model, so this crashed with an
    # AttributeError every time a session was ended).
    logs = session.logs

    session.total_visitors = len(
        {(l.user_id, l.unknown_visitor_id) for l in logs}
    )
    session.known_visitors = len(
        {l.user_id for l in logs if l.user_id is not None}
    )
    session.unknown_visitors = len(
        {l.unknown_visitor_id for l in logs if l.unknown_visitor_id is not None}
    )

    db.commit()
    return session
