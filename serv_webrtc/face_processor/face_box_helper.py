class FaceBox(object):
    top_x: int
    top_y: int
    bottom_x: int
    bottom_y: int


def coordinates_to_face_boxs(locs):
    """
    Converts a list of coordinates from
    face_recognition to a FaceBox object

    (face_recognition returns:
    top, right, bottom, left)
    """

    faces = []
    for location in locs:
        face = FaceBox()
        face.top_x=location[3]
        face.top_y=location[0]
        face.bottom_x=location[1]
        face.bottom_y=location[2]
        faces.append(face)

    return faces

