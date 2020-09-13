from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Index, DateTime, func
)
from sqlalchemy.orm import (
    relationship
)

__all__ = ['topic', 'question', 'topics_questions']

meta = MetaData()

topics_questions = Table(
    'topics_questions', meta,
    Column('topic_id', Integer, ForeignKey('topics.id'), index=True),
    Column('question_id', Integer, ForeignKey('questions.id'), index=True),
    Column('topic_number', Integer, index=True, nullable=False),
    Index('uix_topics_questions', 'topic_id', 'question_id', unique=True)
)

topic = Table(
    'topics', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('topic', String(300), index=True, unique=True, nullable=False),
    Column('questions_count', Integer, default=0),
    Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False),
)


question = Table(
    'questions', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('stackexchange_id', Integer, index=True, unique=True, nullable=False),
    Column('title', String(300), nullable=False),
    Column('link', String(400), nullable=False),
    Column('creation_date', DateTime(timezone=True), nullable=False),
)


topic.questions = relationship('questions', secondary=topics_questions, backref='topics')
