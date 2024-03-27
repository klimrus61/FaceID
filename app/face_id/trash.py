from pathlib import Path

import face_recognition

basedir = Path(__file__).resolve().parent.parent.parent

known_image = face_recognition.load_image_file(
    basedir / "images" / "known_faces" / "klim.jpg"
)
unknown_image = face_recognition.load_image_file(
    basedir / "images" / "unknown" / "klim1.jpg"
)

klim_encoding = face_recognition.face_encodings(known_image)[0]
unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

results = face_recognition.compare_faces([klim_encoding], unknown_encoding)

pass
