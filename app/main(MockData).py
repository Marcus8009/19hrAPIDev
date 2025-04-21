from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body 
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

from fastapi.middleware.cors import CORSMiddleware

#(venv2) uvicorn app.main:app --reload
app = FastAPI()

#http://127.0.0.1:8000/docs
#http://127.0.0.1:8000/redoc

class Post(BaseModel):
    title:str
    content:str
    published: bool = True 
    rating: Optional[int] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None
    rating: Optional[int] = None


while True:
    try: 
        conn = psycopg2.connect(  # ← fixed here
            host="localhost",
            database="fastapi",
            user="postgres",       # ← also change 'username' to 'user'
            password="password",
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        print("Database connection was successful")
        break
    except Exception as error:
        print("Connection to database failed")
        print("Error: ", error)
        time.sleep(2)
    
my_posts = [{"title": "title of post 1", "content": "content of post 1" , "id" : 1},
            {"title": "title of post 2", "content": "content of post 2" , "id" : 2},
            {"title": "title of post 3", "content": "content of post 3" , "id" : 3},
            {"title": "title of post 4", "content": "content of post 4" , "id" : 4}
            ]

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p
        
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i 

@app.get("/")
def root():
    return {"message": "Hello World!!!"}

#Get Posts
@app.get("/posts")
def get_posts():
    return {"data": my_posts}

# @app.get("/posts/latest")
# def get_latest_post():
#     post = my_posts[len(my_posts)-1]
#     return {"detail": post}

#Get Single Post
# @app.get("/posts/{id}")
# def get_post(id: int, response: Response):
#     post = find_post(id)
#     if not post:
#         response.status_code = status.HTTP_404_NOT_FOUND
#         return {"message": f"Post with id {id} not found"}
#     return {"post_detail": post}

#Get Single Post
@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} not found")
    return {"post_detail": post}



#Post Posts
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict['id'] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict}

#Delete Post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int):
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post with id:{id} does not exist")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
#For delete you want to just return a status code instead of a print statement because of fastapi rules.



#Update Post with PUT 
@app.put("/posts/{id}")
def update_post(id:int, post:Post):
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id:{id} does not exist")
    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[index] = post_dict
    return {"message": "Post updated successfully", "data": post_dict}

                
#Update Post with PATCH
@app.patch("/posts/{id}")
def patch_post(id: int, post: PostUpdate):
    index = find_index_post(id)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist"
        )

    existing_post = my_posts[index]

    # Update only the fields that were sent in the request
    post_data = post.dict(exclude_unset=True)
    updated_post = {**existing_post, **post_data}

    my_posts[index] = updated_post

    return {"message": "Post partially updated successfully", "data": updated_post}








# @app.post("/createposts")
# def create_posts(payload: dict = Body(...)):
#     print(payload)
#     return {"new_post": f"title {payload['title']} content {payload['content']}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
