import face_recognition
import pickle
import cv2 
import os
import typing as tp
import uuid
import datetime
import boto3

from fastapi.responses import JSONResponse
from fastapi import UploadFile, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import insert

from app.schemas import users as users_models
from app.schemas import neuro as neuro_models
from app import main

PATH_TO_DIR = os.environ.get("PATH_IMAGES")


async def calculate_embeddings(old_encodings: tp.List, names: tp.List, file_path: str, name: str):
    image = cv2.imread(file_path)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #используем библиотеку Face_recognition для обнаружения лиц
    boxes = face_recognition.face_locations(rgb, model='hog')
    # вычисляем эмбеддинги для каждого лица
    encodings = face_recognition.face_encodings(rgb, boxes)
    # loop over the encodings
    for encoding in encodings:
        old_encodings.append(encoding)
        names.append(name)


async def handle(
    pics: tp.List[UploadFile],
    names: tp.List[str],
    gallery: str,
    current_user: users_models.User,
    conn: AsyncSession,
):
    try:
        path = PATH_TO_DIR + str(current_user.email) + '/'
        data = {}
        encodings = []
        filenames = []
        if not os.path.exists(path):
            os.makedirs(path)
        if os.path.exists(path + 'face_enc'):
            data = pickle.loads(open(path + 'face_enc', "rb").read())
            encodings = data['encodings']
            filenames = data['names']
        for (idx, pic) in enumerate(pics):
            filename = uuid.uuid4().hex + '.png'
            id = uuid.uuid4().hex
            file_path = path + filename
            with open(file_path, "wb+") as f:
                f.write(pic.file.read())
                f.close()

            main.storage.upload_file(file_path, 'neurobucket', file_path)

            await calculate_embeddings(old_encodings=encodings, names=filenames, file_path=file_path, name=file_path)

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

            await conn.exec(
                insert(neuro_models.ImagesPeople),
                [
                    {
                        "id": uuid.uuid4().hex,
                        "image_id": id,
                        "name": names[idx],
                    },
                ],
            )
            await conn.commit()

            os.remove(file_path)
        print("KEKEKEKEKEKKEEKEK")
        f = open(path + 'face_enc', "wb")

        data = {'encodings': encodings, 'names': filenames}
        f.write(pickle.dumps(data))
        f.close()
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=str(e),
        )
    return {"message": "File saved successfully"}
