import face_recognition
import pickle
import cv2 
import os
import typing as tp
import uuid

from fastapi.responses import JSONResponse
from fastapi import status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import insert

from app.schemas import users as users_models
from app.schemas import neuro as neuro_models
from app import main

PATH_TO_DIR = os.environ.get("PATH_IMAGES")


async def handle(
    pics: tp.List[neuro_models.FileWithName],
    current_user: users_models.User,
    conn: AsyncSession,
):
    try:
        path = PATH_TO_DIR + str(current_user.id) + '/'
        data = []
        if not os.path.exists(path):
            os.makedirs(path)
        if os.path.exists(path + 'face_enc'):
            data = pickle.loads(open(path + 'face_enc', "rb").read())
        for pic in pics:
            filename = uuid.uuid4().hex + '.png'
            id = uuid.uuid4().hex
            file_path = path + filename
            main.storage.write(file=pic.file, name=file_path)
            with open(file_path, "wb+") as f:
                f.write(pic.file.file.read())
            image = cv2.imread(file_path)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            #используем библиотеку Face_recognition для обнаружения лиц
            boxes = face_recognition.face_locations(rgb, model='hog')
            # вычисляем эмбеддинги для каждого лица
            encodings = face_recognition.face_encodings(rgb, boxes)
            # loop over the encodings
            for encoding in encodings:
                data.append({'encoding': encoding, 'name': pic.name})

            await conn.exec(
                insert(neuro_models.UsersImages),
                [
                    {
                        "id": id,
                        "user_id": current_user.id,
                        "filename": filename,
                    },
                ],
            )
            await conn.commit()

            await conn.exec(
                insert(neuro_models.ImagesPeople),
                [
                    {
                        "id": uuid.uuid4().hex,
                        "image_id": id,
                        "name": pic.name,
                    },
                ],
            )
            await conn.commit()
        f = open(path + 'face_enc', "wb+")
        f.write(pickle.dumps(data))
        f.close()
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Error when save images"},
        )
    return {"message": "File saved successfully"}
