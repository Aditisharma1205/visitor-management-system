from datetime import datetime
from app.models import VisitorLog


def create_entry(db, user_id):

    existing = (
        db.query(VisitorLog)
        .filter(
            VisitorLog.user_id == user_id,
            VisitorLog.status == "IN"
        )
        .first()
    )

    if existing:
        return

    log = VisitorLog(
        user_id=user_id,
        entry_time=datetime.now(),
        status="IN"
    )

    db.add(log)
    db.commit()

    print(f"ENTRY CREATED USER={user_id}")


def create_exit(db, user_id):

    active = (
        db.query(VisitorLog)
        .filter(
            VisitorLog.user_id == user_id,
            VisitorLog.status == "IN"
        )
        .order_by(
            VisitorLog.id.desc()
        )
        .first()
    )

    if active is None:
        return

    active.exit_time = datetime.now()
    active.status = "OUT"

    db.commit()

    print(f"EXIT CREATED USER={user_id}")