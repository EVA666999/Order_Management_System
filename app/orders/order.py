from datetime import datetime
import json
from aiokafka import AIOKafkaProducer
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import and_, delete, insert, or_, select, update
from slugify import slugify
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.auth.auth import get_current_user
from app.tasks.order_task import process_order
import redis.asyncio as redis
from app.services.kafka_service import get_kafka_producer
from app.services.redis_service import get_redis
from loguru import logger
from celery import Celery
import time

from app.database.db_depends import get_db
from app.schemas import CreateOrder, UpdateStatus
from aiokafka import AIOKafkaProducer
from app.models.orders import Orders

router = APIRouter(prefix='/orders', tags=['orders'])

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_order(
    db: Annotated[AsyncSession, Depends(get_db)],
    create_order: CreateOrder,
    kafka_producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    logger.info(f"Creating order with data: {create_order}")
    try:
        new_order = Orders(
            user_id=current_user['id'],
            items=create_order.items,
            total_price=create_order.total_price,
            status=create_order.status,
            created_at=datetime.utcnow()
        )

        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)

        order_data = {
            'id': str(new_order.id),
            'user_id': new_order.user_id,
            'items': new_order.items,
            'total_price': new_order.total_price,
            'status': new_order.status.value,
            'created_at': new_order.created_at.isoformat()
        }

        process_order.delay(str(new_order.id))

        response = {
            'detail': 'Order created successfully',
            'id': new_order.id
        }

        try:
            await kafka_producer.send_and_wait(
                'new_orders', 
                json.dumps(order_data).encode('utf-8')
            )
        except Exception as kafka_error:
            logger.error(f"Error sending to Kafka: {kafka_error}")
            # Не прерываем работу, просто логируем ошибку
        
        return response
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Error creating order: {str(e)}"
        )
    
@router.get("/{order_id}", status_code=200)
async def get_order(
    order_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
    current_user: Annotated[dict, Depends(get_current_user)]
):
    cached_order = await redis_client.get(f"order:{order_id}")
    if cached_order:
        return json.loads(cached_order)
    
    order = await db.scalar(
        select(Orders).where(
            Orders.id == order_id, 
            Orders.user_id == current_user['id']
        )
    )
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order_dict = order.__dict__
    del order_dict['_sa_instance_state']
    
    await redis_client.setex(
        f"order:{order_id}", 
        300,
        json.dumps(order_dict, default=str)
    )
    
    return order_dict

@router.put('/{order_id}')
async def update_product(
    db: Annotated[Session, Depends(get_db)], 
    order_id: UUID,
    update_status: UpdateStatus,
    current_user: Annotated[dict, Depends(get_current_user)]):
    order = await db.scalar(
        select(Orders).where(
            Orders.id == order_id, 
            Orders.user_id == current_user['id']
        )
    )
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    await db.execute(
        update(Orders).where(Orders.id == order.id).values(
            status=update_status.status,
        )
    )
    await db.commit()

    return {
        'detail': 'Product updated successfully'
    }


@router.get('/user/{user_id}/')
async def get_reviews_for_product(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int,):
    orders = await db.scalars(
        select(Orders).where(Orders.user_id == user_id)
    )
    orders = orders.all()
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No orders for user_id: {user_id}"
        )
    return orders