from typing import Sequence

import face_recognition

from app.db.models import Photo


async def is_one_person_on_photo(photo: Photo):
    img = face_recognition.load_image_file(photo.file)
    face_locations = face_recognition.face_locations(img)
    return len(face_locations) == 1


async def is_person_same(photos_of_person: Sequence[Photo], unknown_person: Photo):
    known_images = []
    for photo in photos_of_person:
        known_images.append(face_recognition.load_image_file(photo.file))
    unknown_image = face_recognition.load_image_file(unknown_person.file)

    known_faces = []
    for known_image in known_images:
        known_faces.append(face_recognition.face_encodings(known_image)[0])
    unknown_face = face_recognition.face_encodings(unknown_image)[0]

    result = face_recognition.compare_faces(known_faces, unknown_face)
    return any(result)
