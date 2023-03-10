from fastapi import FastAPI, Depends, status, Response, HTTPException
from . import schemas, models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import List
from .hashing import Hash



app = FastAPI()

models.Base.metadata.create_all(engine)



def get_db():
    db = SessionLocal()

    try : 
        yield db

    finally:
        db.close()



@app.post('/blog', status_code=status.HTTP_201_CREATED, tags=['Blogs'])
def create(request: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, body=request.body, user_id = 1)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@app.get('/blog', tags=['Blogs'], response_model=List[schemas.BlogShow,])
def all(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    if not blogs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data in blogs table")
    return blogs


@app.get('/blog/{id}', status_code=200, tags=['Blogs'], response_model=schemas.BlogShow)
def show(id:int,db : Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=F"Blog with id {id} not found")
    return blog


@app.delete('/blog/{id}', status_code=status.HTTP_204_NO_CONTENT, tags=['Blogs'])
def destroy(id, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {id} not found")
    blog.delete(synchronize_session=False)
    db.commit()
    return 'done'


@app.put('/blog/{id}', status_code=status.HTTP_202_ACCEPTED, tags=['Blogs'])
def update(id, request: schemas.Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)

    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {id} not found")

    blog.update({"title": request.title, "body" : request.body})
    db.commit()
    return 'updated'






@app.post('/users', tags=['Users'], response_model=schemas.ShowUser, status_code=status.HTTP_201_CREATED)
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == request.email).first():
        raise HTTPException(detail=f"email {request.email} is already taken!. Please try with another one", status_code=status.HTTP_400_BAD_REQUEST)
    new_user = models.User(name = request.name, email = request.email, password = Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get('/users', tags=['Users'], response_model=List[schemas.ShowUser], status_code=status.HTTP_200_OK)
def all_user(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    if not users:
        raise HTTPException(detail=f"There is no data in users table", status_code=status.HTTP_404_NOT_FOUND)
    return users



@app.get('/users/{email}', tags=["Users"], response_model=schemas.ShowUser, status_code=status.HTTP_200_OK)
def view_user(email:str , db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    print(user)
    if not user:
        raise HTTPException(detail=f"user with email {email} does not exists", status_code=status.HTTP_404_NOT_FOUND)
    return user


@app.put('/users/{email}', tags=['Users'])
def update_user(email:str, request:schemas.User, db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email)
    if not user.first():
        raise HTTPException(detail=f"There is no user with email {email}", status_code=status.HTTP_404_NOT_FOUND)
    user.update({"name" : request.name, "email" : request.email, "password" : request.password})
    # user.first().email = "rasheeed123@gmail.com"
    db.commit()
    return "User updated successfully"


@app.delete('/users/{email}', tags=['Users'])
def delete_user(email:str, db :  Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email)
    if not user.first():
        raise HTTPException(detail=f"User with email {email} does not exists", status_code=status.HTTP_404_NOT_FOUND)
    user.delete(synchronize_session=False)
    db.commit()
    return f"User {email} deleted successfully"
