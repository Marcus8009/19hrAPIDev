from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body 
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from . import models, schemas
from .database import engine, get_db

# main.py → handles API logic
# schemas.py → holds all request/response models
# models.py → contains database structure

models.Base.metadata.create_all(bind=engine)
#python -m app.main
#uvicorn app.main:app --reload
#(venv2) uvicorn app.main:app --reload
app = FastAPI()

#http://127.0.0.1:8000/docs
#http://127.0.0.1:8000/redoc


#You need a separate schema for PATCH where every field is optional, otherwise Pydantic will complain that required fields are missing.

@app.get("/")
def root():
    return {"message": "Hello World!!!"}

#Get Posts
@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

#Get Single Post
@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} not found")
    return post
 
#Create Posts
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: schemas.Post, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# Delete Post - Single post, intuitive, fetches object into memory before deleting.
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} not found")
    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# #Delete Post - Skips loading the full post object into memory, more efficient.
# @app.delete("/posts_fast/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_post_fast(id: int, db: Session = Depends(get_db)):
#     post_query = db.query(models.Post).filter(models.Post.id == id)
#     if post_query.first() is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Post with id: {id} not found"
#         )
#     post_query.delete(synchronize_session=False)
#     db.commit()
#     return Response(status_code=status.HTTP_204_NO_CONTENT)



# Update Post with PUT 
@app.put("/posts/{id}", status_code=status.HTTP_202_ACCEPTED)
def update_post(id: int, updated_post: schemas.Post, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    existing_post = post_query.first()

    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} not found")

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()

                
# Update Post with PATCH
@app.patch("/posts/{id}")
def patch_post(id: int, post_update: schemas.PostUpdate, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    existing_post = post_query.first()

    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} not found")

    post_query.update(post_update.dict(exclude_unset=True), synchronize_session=False)
    db.commit()
    return {"message": "Post partially updated", "data": post_query.first()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
