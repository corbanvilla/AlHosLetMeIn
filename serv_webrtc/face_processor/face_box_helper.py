class FaceBox(object):
    top_x: int
    top_y: int
    bottom_x: int
    bottom_y: int


def coordinates_to_face_box(locs):
    """
    Converts a list of coordinates from
    face_recognition to a FaceBox object

    (face_recognition returns:
    top, right, bottom, left)
    """

    face = FaceBox(
        top_x=locs[3],
        top_y=locs[0],
        bottom_x=[1],
        bottom_y=locs[2]
    )
    return face

