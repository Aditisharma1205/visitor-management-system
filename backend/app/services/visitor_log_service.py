from datetime import datetime
from app.models import VisitorLog


def create_entry(
    db,
    user_id=None,
    unknown_visitor_id=None,
    snapshot_path=None,
    session_id=None
):

    # Registered visitor
    if user_id is not None:

        existing = (
            db.query(VisitorLog)
            .filter(
                VisitorLog.user_id == user_id,
                VisitorLog.status == "INSIDE"
            )
            .first()
        )

    # Unknown visitor
    else:

        existing = (
            db.query(VisitorLog)
            .filter(
                VisitorLog.unknown_visitor_id
                == unknown_visitor_id,
                VisitorLog.status == "INSIDE"
            )
            .first()
        )

    if existing:
        return existing

    log = VisitorLog(
        session_id=session_id,
        user_id=user_id,
        unknown_visitor_id=unknown_visitor_id,
        entry_time=datetime.now(),
        status="INSIDE",
        entry_snapshot=snapshot_path
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    print(
        f"ENTRY CREATED "
        f"USER={user_id} "
        f"UNKNOWN={unknown_visitor_id}"
    )

    return log


def create_exit(
    db,
    user_id=None,
    unknown_visitor_id=None,
    snapshot_path=None
):

    # Registered visitor
    if user_id is not None:

        active = (
            db.query(VisitorLog)
            .filter(
                VisitorLog.user_id == user_id,
                VisitorLog.status == "INSIDE"
            )
            .order_by(
                VisitorLog.id.desc()
            )
            .first()
        )

    # Unknown visitor
    else:

        active = (
            db.query(VisitorLog)
            .filter(
                VisitorLog.unknown_visitor_id
                == unknown_visitor_id,
                VisitorLog.status == "INSIDE"
            )
            .order_by(
                VisitorLog.id.desc()
            )
            .first()
        )

    if active is None:
        return None

    active.exit_time = datetime.now()

    active.status = "OUT"

    active.exit_snapshot = snapshot_path

    db.commit()

    print(
        f"EXIT CREATED "
        f"USER={user_id} "
        f"UNKNOWN={unknown_visitor_id}"
    )

    return active