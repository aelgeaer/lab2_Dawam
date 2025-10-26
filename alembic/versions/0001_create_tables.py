"""create tables

Revision ID: 0001
Revises: 
Create Date: 2025-10-01
"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('email', sa.String(256), nullable=False, unique=True),
        sa.Column('registered_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('is_verified_author', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('avatar', sa.String(512), nullable=True),
    )
    op.create_table(
        'news',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('content', sa.JSON, nullable=False),
        sa.Column('published_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('author_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cover', sa.String(512), nullable=True),
    )
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('news_id', sa.Integer, sa.ForeignKey('news.id', ondelete='CASCADE'), nullable=False),
        sa.Column('author_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('published_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table('comments')
    op.drop_table('news')
    op.drop_table('users')
