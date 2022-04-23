"""
Таблица для хранения перманентной информации о пользователе
"""
import sqlalchemy

from db_session import SqlAlchemyBase


class User(SqlAlchemyBase):

    def __repr__(self):
        return f'<{self.__class__.__name__}> {self.id} {self.name} {self.amount}'

    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    amount = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

