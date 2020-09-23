"""Init

Revision ID: 58ba0e46b750
Revises: 
Create Date: 2020-09-21 10:23:39.654842

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '58ba0e46b750'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('questions',
    sa.Column('stackexchange_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=300), nullable=False),
    sa.Column('link', sa.String(length=400), nullable=False),
    sa.Column('creation_date', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('stackexchange_id'),
    sa.UniqueConstraint('stackexchange_id')
    )
    op.create_table('topics',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('topic', sa.String(length=300), nullable=False),
    sa.Column('questions_count', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_topics_topic'), 'topics', ['topic'], unique=True)
    op.create_table('questions_pages',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.Column('order', sa.String(length=4), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.Column('topic_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['questions.stackexchange_id'], ),
    sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix__pages__number_size_order', 'questions_pages', ['number', 'size', 'order', 'topic_id'], unique=False)
    op.create_index(op.f('ix_questions_pages_question_id'), 'questions_pages', ['question_id'], unique=False)
    op.create_index(op.f('ix_questions_pages_topic_id'), 'questions_pages', ['topic_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_questions_pages_topic_id'), table_name='questions_pages')
    op.drop_index(op.f('ix_questions_pages_question_id'), table_name='questions_pages')
    op.drop_index('ix__pages__number_size_order', table_name='questions_pages')
    op.drop_table('questions_pages')
    op.drop_index(op.f('ix_topics_topic'), table_name='topics')
    op.drop_table('topics')
    op.drop_table('questions')
    # ### end Alembic commands ###