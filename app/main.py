from fastapi import FastAPI, File, UploadFile,Depends, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError
from sqlalchemy.orm import Session

from app.models import MediaFile, WaylineFile
from app.config import SessionLocal, Base, engine
from random import randint


import uuid
import os
import time
import boto3

app = FastAPI()

ACCESS_KEY = 'admincom'
SECRET_KEY = 'admin01101998'
BUCKET_NAME = 'imagens'
ENDPOINT_URL = 'http://minio:9000'
IMAGEDIR = '/app/images/'

s3_client = boto3.client('s3',
                         endpoint_url=ENDPOINT_URL,
                         aws_access_key_id=ACCESS_KEY,
                         aws_secret_access_key=SECRET_KEY,
                         region_name='us-east-1')



def create_bucket_if_not_exists(bucket_name):
    """Cria o bucket se ele não existir."""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            s3_client.create_bucket(Bucket=bucket_name)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()


@app.on_event("startup")
async def startup_event():
    create_bucket_if_not_exists(BUCKET_NAME)
    create_tables()

@app.get("/")
async def read_root():
    return RedirectResponse(url="/docs")

@app.get("/media_files")
async def get_media_files(db: Session = Depends(get_db)):
    media_files = db.query(MediaFile).all()
    return media_files

@app.post("/upload/media_files")
async def create_media_files(file: UploadFile = File(...), db: Session = Depends(get_db)):
    allowed_extensions = {"jpg", "jpeg", "png"}

    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in allowed_extensions:
           allowed_formats = ", ".join(allowed_extensions).upper()
           raise HTTPException(status_code=400, detail=f"Formato de arquivo inválido. Os formatos permitidos são: {allowed_formats}")

    try:
           file_contents = await file.read()
           file_size = len(file_contents)

           file_name = f"{uuid.uuid4()}.{file_extension}"

           s3_client.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=file_contents)

           file_record = MediaFile(
               file_id=str(uuid.uuid4()),
               file_name=file_name,
               file_object_key=file_name,
               file_size=file_size,
               create_time=int(time.time()),
               update_time=int(time.time())
           )

           db.add(file_record)
           db.commit()
           db.refresh(file_record)

           return {"filename": file_name, "file_id": file_record.file_id, "file_size": file_size}
    except NoCredentialsError:
           raise HTTPException(status_code=500, detail="Problemas nas credenciais.")
    except Exception as e:
           raise HTTPException(status_code=500, detail=str(e))





@app.put("/update/media_files/{file_id}")
async def update_media_file(file_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_file = db.query(MediaFile).filter(MediaFile.file_id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")


    file_contents = await file.read()
    s3_client.put_object(Bucket=BUCKET_NAME, Key=db_file.file_name, Body=file_contents)

    db_file.update_time = int(time.time())
    db.commit()
    db.refresh(db_file)

    return {"filename": db_file.file_name, "file_id": db_file.file_id, "updated": True}











@app.delete("/delete/media_files/{file_id}")
async def delete_media_file(file_id: str, db: Session = Depends(get_db)):
    db_file = db.query(MediaFile).filter(MediaFile.file_id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Arquivo nao existe.")

    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=db_file.file_name)
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Falhou ao deletar no MinIO S3: {str(e)}")

    db.delete(db_file)
    db.commit()

    return {"detail": "Arquivo deletado com sucesso."}

# ###################################################################



@app.get("/wayline_files")
async def get_wayline_files(db: Session = Depends(get_db)):
    wayline_files = db.query(WaylineFile).all()
    return wayline_files

@app.post("/upload/wayline_file")
async def create_wayline_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    allowed_extensions = {"kmz", "kml"}

    wayline_extension = file.filename.split('.')[-1].lower()
    if wayline_extension not in allowed_extensions:
        allowed_formats = ", ".join(allowed_extensions).upper()
        raise HTTPException(status_code=400, detail=f"Formato de arquivo inválido. Os formatos permitidos são: {allowed_formats}")

    try:
        wayline_contents = await file.read()
        wayline_size = len(wayline_contents)

        wayline_name = f"{uuid.uuid4()}.{wayline_extension}"

        s3_client.put_object(Bucket=BUCKET_NAME, Key=wayline_name, Body=wayline_contents)

        waylinefile_record = WaylineFile(
            wayline_id=str(uuid.uuid4()),
            wayline_name=wayline_name,
            wayline_object_key=wayline_name,
            favorited=False,
            create_time=int(time.time()),
            update_time=int(time.time())
        )

        db.add(waylinefile_record)
        db.commit()
        db.refresh(waylinefile_record)

        return {"filename": wayline_name, "wayline_id": waylinefile_record.wayline_id}
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="Problemas nas credencias.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/update/wayline_file/{wayline_id}")
async def update_wayline_file(wayline_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_file = db.query(WaylineFile).filter(WaylineFile.wayline_id == wayline_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

    wayline_contents = await file.read()
    s3_client.put_object(Bucket=BUCKET_NAME, Key=db_file.wayline_name, Body=wayline_contents)

    db_file.update_time = int(time.time())
    db.commit()
    db.refresh(db_file)

    return {"filename": db_file.wayline_name, "wayline_id": db_file.wayline_id, "updated": True}


@app.delete("/delete/wayline_files/{wayline_id}")
async def delete_wayline_file(wayline_id: str, db: Session = Depends(get_db)):
    db_file = db.query(WaylineFile).filter(WaylineFile.wayline_id == wayline_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Arquivo nao existe.")

    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=db_file.wayline_name)
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar arquivo no minIO S3: {str(e)}")

    db.delete(db_file)
    db.commit()

    return {"detail": "Arquivo deletado com successo."}
