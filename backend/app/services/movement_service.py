def detect_event(track, zone):

    if track["first_zone"] is None:
        track["first_zone"] = zone

    track["current_zone"] = zone

    first_zone = track["first_zone"]

    if (
        first_zone == "ENTRY"
        and zone == "EXIT"
    ):
        track["first_zone"] = None
        return "ENTRY"

    if (
        first_zone == "EXIT"
        and zone == "ENTRY"
    ):
        track["first_zone"] = None
        return "EXIT"

    return None