"""
Orders module - API для управления заказами в системе.
"""
from datetime import datetime
import json
from typing import Annotated, Dict, Any
from uuid import UUID

from aiokafka import AIOKafkaProducer
from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi_limiter.depends import RateLimiter
from loguru import logger
import redis.asyncio as redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.auth.auth import get_current_user
from app.database.db_depends import get_db
from app.models.orders import Orders
from app.schemas import CreateOrder, UpdateStatus
from app.services.kafka_service import get_kafka_producer
from app.services.redis_service import get_redis
from app.tasks.order_task import process_order


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=15, seconds=60))],
    summary="Создание нового заказа"
)
async def create_order(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    create_order: CreateOrder,
    kafka_producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> Dict[str, Any]:
    """Создает новый заказ и запускает его обработку"""
    try:
        new_order = Orders(
            user_id=current_user["id"],
            items=create_order.items,
            total_price=create_order.total_price,
            status=create_order.status,
            created_at=datetime.utcnow(),
        )

        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)

        order_data = {
            "id": str(new_order.id),
            "user_id": new_order.user_id,
            "items": new_order.items,
            "total_price": new_order.total_price,
            "status": new_order.status.value,
            "created_at": new_order.created_at.isoformat(),
        }

        process_order.delay(str(new_order.id))
        response = {"detail": "Order created successfully", "id": new_order.id}

        try:
            await kafka_producer.send_and_wait(
                "new_orders", json.dumps(order_data).encode("utf-8")
            )
        except Exception as kafka_error:
            logger.error(f"Error sending to Kafka: {kafka_error}")

        return response
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating order: {str(e)}",
        )


@router.get(
    "/{order_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=20, seconds=60))],
    summary="Получение информации о заказе"
)
async def get_order(
    request: Request,
    order_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> Dict[str, Any]:
    """Получает заказ по ID с использованием кэширования"""
    cached_order = await redis_client.get(f"order:{order_id}")
    if cached_order:
        return json.loads(cached_order)

    order = await db.scalar(
        select(Orders).where(
            Orders.id == order_id, Orders.user_id == current_user["id"]
        )
    )

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order_dict = order.__dict__
    del order_dict["_sa_instance_state"]

    await redis_client.setex(
        f"order:{order_id}", 300, json.dumps(order_dict, default=str)
    )

    return order_dict


@router.put(
    "/{order_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
    summary="Обновление статуса заказа"
)
async def update_product(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    order_id: UUID,
    update_status: UpdateStatus,
    current_user: Annotated[dict, Depends(get_current_user)],
) -> Dict[str, str]:
    """Обновляет статус существующего заказа"""
    order = await db.scalar(
        select(Orders).where(
            Orders.id == order_id, Orders.user_id == current_user["id"]
        )
    )
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    await db.execute(
        update(Orders)
        .where(Orders.id == order.id)
        .values(
            status=update_status.status,
        )
    )
    await db.commit()

    return {"detail": "Product updated successfully"}


@router.get(
    "/user/{user_id}/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=20, seconds=60))],
    summary="Получение заказов пользователя"
)
async def get_orders_for_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int,
):
    """Возвращает все заказы указанного пользователя"""
    orders = await db.scalars(select(Orders).where(Orders.user_id == user_id))
    orders_list = orders.all()
    
    if not orders_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No orders for user_id: {user_id}",
        )
    
    return orders_list