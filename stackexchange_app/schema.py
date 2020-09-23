from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Index, DateTime, func
)

__all__ = ['topic', 'question', 'questions_page']

meta = MetaData()


topic = Table(
    'topics', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('topic', String(300), index=True, unique=True, nullable=False),
    Column('questions_count', Integer, default=0),
    Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False),
)


question = Table(
    'questions', meta,
    Column('stackexchange_id', Integer, primary_key=True, unique=True, nullable=False),
    Column('title', String(300), nullable=False),
    Column('link', String(400), nullable=False),
    Column('creation_date', DateTime(timezone=True), nullable=False),
)


questions_page = Table(
    'questions_pages', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('number', Integer, nullable=False),
    Column('size', Integer, nullable=False),
    Column('order', String(4), nullable=False),
    Column('question_id', Integer, ForeignKey('questions.stackexchange_id'), index=True),
    Column('topic_id', Integer, ForeignKey('topics.id'), index=True),
    Index('ix__pages__number_size_order', 'number', 'size', 'order', 'topic_id', unique=False)
)
