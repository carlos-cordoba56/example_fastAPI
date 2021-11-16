from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func

from typing import List, Optional

from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix= '/posts',
    tags=['Posts']
)

# ------------------------------
# ------ método post - Create---
# ------------------------------

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PostRespoce)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), 
                currrent_user = Depends(oauth2.get_current_user)):

    new_post = models.Post(owner_id=currrent_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

# ------------------------------
# ------ métodos get - Read-----
# ------------------------------

# @router.get( "/", response_model=List[schemas.PostRespoce] )
@router.get( "/", response_model=List[schemas.PostRespoceWithVotes] )
def read_posts(db: Session = Depends(get_db), 
                currrent_user :int = Depends(oauth2.get_current_user),
                limit: int = 5, skip: int = 0, search: Optional[str] = '' ):

    # posts = (db.query(models.Post)
    #             .filter(models.Post.title.contains(search))
    #             .offset(skip)
    #             .limit(limit).all())
    posts = (db.query(models.Post, func.count(models.Vote.post_id).label('votes'))
                .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
                .group_by(models.Post.id)
                .filter(models.Post.title.contains(search))
                .offset(skip)
                .limit(limit)
                .all()
            )
    # print(posts)
    
    return posts

# @router.get( '/{id}', response_model=schemas.PostRespoce )
@router.get( '/{id}', response_model=schemas.PostRespoceWithVotes)
def read_post( id: int, db: Session = Depends(get_db), 
                currrent_user :int = Depends(oauth2.get_current_user) ):

    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post = (db.query(models.Post, func.count(models.Vote.post_id).label('votes'))
                .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
                .group_by(models.Post.id)
                .filter(models.Post.id == id)
                .first()
            )
    if not post:
        raise HTTPException( status_code=status.HTTP_404_NOT_FOUND, 
                             detail=f'post with id={id} was not found' )

    return post

# ------------------------------
# ------ método put - Update----
# ------------------------------

@router.put('/{id}', response_model=schemas.PostRespoce)
def update_post( id: int, post: schemas.PostUpdate, db: Session = Depends(get_db), 
                currrent_user :int = Depends(oauth2.get_current_user) ):

    updated_post = db.query(models.Post).filter(models.Post.id == id)
    if not updated_post.first():
        raise HTTPException( status_code=status.HTTP_404_NOT_FOUND, 
                             detail=f'post with id={id} was not found' )
    
    if updated_post.owner_id != currrent_user.id:
        raise HTTPException( status_code=status.HTTP_403_FORBIDDEN, 
                             detail=f'Not authorized to perform requested action' )
    
    updated_post.update(post.dict(), synchronize_session=False)
    db.commit()

    return updated_post.first()

# ------------------------------
# ------ método delete - Delete-
# ------------------------------

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post( id: int, db: Session = Depends(get_db), 
                currrent_user :int = Depends(oauth2.get_current_user) ):

    deleted_post = db.query(models.Post).filter(models.Post.id == id)
    if not deleted_post.first():
        raise HTTPException( status_code=status.HTTP_404_NOT_FOUND, 
                             detail=f'post with id={id} was not found' )
    
    if deleted_post.owner_id != currrent_user.id:
        raise HTTPException( status_code=status.HTTP_403_FORBIDDEN, 
                             detail=f'Not authorized to perform requested action' )
    
    deleted_post.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)