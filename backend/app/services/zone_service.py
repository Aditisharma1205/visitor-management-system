ENTRY_ZONE = 200
EXIT_ZONE = 450


def get_zone(bbox):

    x1, y1, x2, y2 = bbox

    center_x = (x1 + x2) / 2

    if center_x < ENTRY_ZONE:
        return "ENTRY"

    if center_x > EXIT_ZONE:
        return "EXIT"

    return "CENTER"