def detect_event(track, zone):

    previous = track["current_zone"]

    track["previous_zone"] = previous
    track["current_zone"] = zone

    if (
        previous == "ENTRY"
        and zone == "EXIT"
    ):
        return "ENTRY"

    if (
        previous == "EXIT"
        and zone == "ENTRY"
    ):
        return "EXIT"

    return None
