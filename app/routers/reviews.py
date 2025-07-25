from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession, AsyncScalarResult
from sqlalchemy.orm import selectinload

from app.backend.db_depends import get_db
from sqlalchemy import select, insert

from app.models.comments import Comment
from app.routers.auth import get_current_user
from app.schemas import CreateComment
from app.models import *


async def upgrade_rating(product: Product, grades: AsyncScalarResult) -> float:
    grades_all = grades.all()
    if grades_all:
        new_rating = round(sum(grades_all) / len(grades_all), 1)
    else: new_rating = 0
    product.rating = new_rating

    return new_rating

router = APIRouter(prefix='/reviews', tags=['reviews'])

@router.get('/')
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Comment).where(Comment.is_active == True))
    all_reviews = reviews.all()
    if not all_reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no reviews.'
        )
    return all_reviews

@router.get('/{product_slug}')
async def products_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    reviews = await db.scalars(select(Comment).where(Comment.product_id == product.id))
    reviews_all = reviews.all()
    if not reviews_all:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no reviews.'
        )
    return reviews_all


@router.post('/{product_slug}', status_code=status.HTTP_201_CREATED)
async def add_review(db: Annotated[AsyncSession, Depends(get_db)],
                     product_slug: str,
                     create_review: CreateComment,
                     get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_customer'):
        product = await db.scalar(select(Product).where(Product.slug == product_slug))
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Product not found'
            )

        await db.execute(insert(Comment).values(user_id = get_user.get('id'),
                                                product_id= product.id,
                                                comment = create_review.comment,
                                                grade = create_review.grade,
                                                is_active = True))

        grades = await db.scalars(
            select(Comment.grade).where(
                Comment.product_id == product.id,
                Comment.is_active == True
            ))
        new_rating = await upgrade_rating(product, grades)
        await db.commit()

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not enough permission for this action'
        )

    return  {"detail": "Review added successfully", "new_rating": new_rating}


@router.delete('/{comment_id}/')
async def delete_reviews(db: Annotated[AsyncSession, Depends(get_db)], comment_id: int,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    comment_delete = await db.scalar(select(Comment).
                                     options(selectinload(Comment.product)).
                                     where(Comment.id == comment_id))
    if not comment_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no comment found'
        )
    if get_user.get('is_admin'):
        comment_delete.is_active = False
        grades = await db.scalars(
            select(Comment.grade).where(
                Comment.product_id == comment_delete.product_id,
                Comment.is_active == True
            )
        )
        product = comment_delete.product
        await upgrade_rating(product, grades)
        await db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not enough permission for this action'
        )


