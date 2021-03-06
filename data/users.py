import datetime
import sqlalchemy

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    telegram_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    min_price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
