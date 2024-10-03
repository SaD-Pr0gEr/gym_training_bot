from typing import Union, Any

import sqlalchemy as sa
from sqlalchemy import MetaData, JSON
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


class Model(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            'ix': 'ix_%(column_0_label)s',
            'uq': 'uq_%(table_name)s_%(column_0_name)s',
            'ck': 'ck_%(table_name)s_`%(constraint_name)s`',
            'fk': 'fk_%(table_name)s_%(column_0_name)s_%'
                  '(referred_table_name)s',
            'pk': 'pk_%(table_name)s',
        }
    )
    type_annotation_map = {dict[Union[str, int], Any]: JSON}


class BaseModelMixin:

    @classmethod
    async def select(
            cls, session: AsyncSession, filter_data: dict | None = None,
            one: bool = False
    ):
        query = sa.select(cls)
        if filter_data:
            for key, value in filter_data.items():
                query = query.where(getattr(cls, key) == value)
        result = await session.execute(query)
        if one:
            return result.scalars().first()
        return result.scalars().all()

    @classmethod
    async def delete(cls, session: AsyncSession, filter_data: dict) -> None:
        query = sa.delete(cls)
        for key, value in filter_data.items():
            query = query.where(getattr(cls, key) == value)
        await session.execute(query)

    @classmethod
    async def update(
            cls, session: AsyncSession, filter_data: dict, update_data: dict
    ) -> None:
        query = sa.update(cls).values(**update_data)
        for key, value in filter_data.items():
            query = query.where(getattr(cls, key) == value)
        await session.execute(query)

    def display_text(self, *args, **kwargs) -> str:
        raise NotImplementedError
