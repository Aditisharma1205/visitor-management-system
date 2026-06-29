from app.models import UnknownVisitor


def create_unknown_visitor(
    db,
    track_id,
    image_path
):

    unknown = UnknownVisitor(
        track_id=track_id,
        image_path=image_path
    )

    db.add(unknown)
    db.commit()
    db.refresh(unknown)

    unknown.name = f"Unknown_{unknown.id}"

    db.commit()

    return unknown