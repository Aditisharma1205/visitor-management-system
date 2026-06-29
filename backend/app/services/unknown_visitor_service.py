from app.models import UnknownVisitor


def create_unknown_visitor(
    db,
    track_id,
    image_path,
):

    visitor = UnknownVisitor(
        track_id=track_id,
        image_path=image_path,
    )

    db.add(visitor)
    db.commit()
    db.refresh(visitor)

    visitor.name = f"Unknown_{visitor.id:03d}"

    db.commit()
    db.refresh(visitor)

    print(
        f"UNKNOWN CREATED {visitor.name}"
    )

    return visitor