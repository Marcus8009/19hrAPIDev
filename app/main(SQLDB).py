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
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}

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
def get_post(id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    #the extra comma is because a tuple is needed - tuple rule
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} not found")
    return {"post_detail": post}




#Create Posts
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    #bad method prone to sql injection = cursor.execute(f"INSERT INTO posts (title, content, published) VALUES ('{post.title}', '{post.content}', '{post.published}')")
    cursor.execute(
    "INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *",
    (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


# Delete Post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (id,))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist"
        )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

#For delete you want to just return a status code instead of a print statement because of fastapi rules.



# Update Post with PUT 
@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(
        """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
        (post.title, post.content, post.published, id)
    )
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist"
        )

    return {"data": updated_post}


                
# Update Post with PATCH
@app.patch("/posts/{id}")
def patch_post(id: int, post: PostUpdate):
    # Convert only the fields that were actually sent in the request
    post_data = post.dict(exclude_unset=True)

    if not post_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    # Dynamically build the SET clause
    set_clause = ", ".join([f"{key} = %s" for key in post_data.keys()])
    values = list(post_data.values())
    values.append(id)  # Add id to the end for WHERE clause

    query = f"UPDATE posts SET {set_clause} WHERE id = %s RETURNING *"

    cursor.execute(query, tuple(values))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist"
        )

    return {"message": "Post partially updated successfully", "data": updated_post}








# @app.post("/createposts")
# def create_posts(payload: dict = Body(...)):
#     print(payload)
#     return {"new_post": f"title {payload['title']} content {payload['content']}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
