"""seed mock data

Revision ID: 0002
Revises: 0001
Create Date: 2025-10-01
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
from sqlalchemy.sql import table, column

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

users_table = table('users',
    column('id', sa.Integer),
    column('name', sa.String),
    column('email', sa.String),
    column('registered_at', sa.DateTime),
    column('is_verified_author', sa.Boolean),
    column('avatar', sa.String),
)

def upgrade():
    op.bulk_insert(users_table, [
        {'id':1, 'name':'Alice', 'email':'alice@example.com', 'registered_at': datetime.utcnow(), 'is_verified_author': True, 'avatar': None},
        {'id':2, 'name':'Bob', 'email':'bob@example.com', 'registered_at': datetime.utcnow(), 'is_verified_author': False, 'avatar': None},
    ])
    conn = op.get_bind()
    conn.execute(sa.text("""
        INSERT INTO news (title, content, author_id, published_at, cover) VALUES
        ('First news', '{"blocks": [{"type":"paragraph","text":"Hello world"}]}', 1, now(), NULL);
    """))
    conn.execute(sa.text("""
        INSERT INTO comments (text, news_id, author_id, published_at) VALUES
        ('Nice post!', 1, 2, now());
    """))

def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM comments;"))
    conn.execute(sa.text("DELETE FROM news;"))
    conn.execute(sa.text("DELETE FROM users;"))
