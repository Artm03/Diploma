import face_recognition
import pickle
import cv2 
import os
import typing as tp
import uuid
import numpy as np
import datetime

from PIL import ImageFont, ImageDraw, Image
from fastapi.responses import JSONResponse
from fastapi import UploadFile, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import insert, select, func

from app.schemas import users as users_models
from app.schemas import neuro as neuro_models
from app import main

PATH_TO_DIR = os.environ.get("PATH_IMAGES")



async def handle(
    pics: tp.List[UploadFile],
    gallery: str,
    current_user: users_models.User,
    conn: AsyncSession,
):
    try:
        cascPathface = os.path.dirname(
            cv2.__file__) + "/data/haarcascade_frontalface_alt2.xml"
        # load the harcaascade in the cascade classifier
        faceCascade = cv2.CascadeClassifier(cascPathface)
        path = PATH_TO_DIR + str(current_user.email) + '/'
        data: tp.List = {}
        if not os.path.exists(path):
            os.makedirs(path)
        if os.path.exists(path + 'face_enc'):
            data = pickle.loads(open(path + 'face_enc', "rb").read())
        for pic in pics:
            filename = uuid.uuid4().hex + '.png'
            id = uuid.uuid4().hex
            file_path = path + filename
            with open(file_path, "wb+") as f:
                f.write(pic.file.read())
                f.close()

            image = cv2.imread(file_path)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb)
            # convert image to Greyscale for haarcascade
            boxes = face_recognition.face_locations(rgb, model='hog')

            # the facial embeddings for face in input
            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []

            for (num, encoding) in enumerate(encodings):
                matches = face_recognition.compare_faces(data['encodings'], encoding)

                name = "Unknown"
                if True in matches:
                    matchedIdx = 0
                    for (i, b) in enumerate(matches):
                        if b:
                            matchedIdx = i
                            break
                    counts = {}
                    # loop over the matched indexes and maintain a count for
                    # each recognized face face
                    name = data["names"][matchedIdx]

                    counts[name] = counts.get(name, 0) + 1

                    name = max(counts, key=counts.get)

                    people_name = (
                        await conn.exec(
                            select(
                                neuro_models.UsersImages.filename,
                                neuro_models.UsersImages.id,
                                neuro_models.UsersImages.created_at,
                                neuro_models.ImagesPeople.name,
                            )
                            .where(name == neuro_models.UsersImages.filename)
                            .join(
                                neuro_models.ImagesPeople,
                                neuro_models.UsersImages.id == neuro_models.ImagesPeople.image_id,
                            )
                        )
                    ).fetchone()
                    names.append(people_name['name'])
                # loop over the recognized faces
            draw = ImageDraw.Draw(pil_image)
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 35, encoding="unic")
            for ((x, y, w, h), name) in zip(boxes, names):
                draw.text((h, x), name, font=font)
                # cv2.putText(image, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                # 0.75, (0, 255, 0), 2)
            new_image = np.asarray(pil_image)
            new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(file_path, new_image)

            main.storage.upload_file(file_path, 'neurobucket', file_path)

            await conn.exec(
                insert(neuro_models.UsersImages),
                [
                    {
                        "id": id,
                        "user_id": current_user.id,
                        "gallery_id": gallery,
                        "filename": file_path,
                        "created_at": datetime.datetime.now(datetime.timezone.utc),
                    },
                ],
            )
            if names:
                await conn.exec(
                    insert(neuro_models.ImagesPeople),
                    [
                        {
                            "id": uuid.uuid4().hex,
                            "image_id": id,
                            "name": name,
                        }
                        for name in names
                    ],
                )
            else:
                await conn.exec(
                    insert(neuro_models.ImagesPeople),
                    [
                        {
                            "id": uuid.uuid4().hex,
                            "image_id": id,
                            "name": '',
                        }
                    ],
                )

            await conn.commit()

            os.remove(file_path)

        f = open(path + 'face_enc', "wb")
        f.write(pickle.dumps(data))
        f.close()
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=str(e),
        )
    return {"message": "File saved successfully"}
