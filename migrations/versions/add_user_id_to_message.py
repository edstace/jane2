"""add user_id to message table

Revision ID: add_user_id_to_message
Revises: 
Create Date: 2025-02-26 16:17

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'add_user_id_to_message'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add user_id column
    op.add_column('message',
        sa.Column('user_id', sa.Integer(), nullable=True)
    )
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_message_user_id', 
        'message', 'users',
        ['user_id'], ['id']
    )
    
    # Add index on conversation_id if it doesn't exist
    op.create_index(
        op.f('ix_message_conversation_id'),
        'message', ['conversation_id'],
        unique=False,
        if_not_exists=True
    )

def downgrade():
    # Remove foreign key constraint first
    op.drop_constraint('fk_message_user_id', 'message', type_='foreignkey')
    
    # Remove user_id column
    op.drop_column('message', 'user_id')
    
    # Remove conversation_id index
    op.drop_index(op.f('ix_message_conversation_id'), table_name='message')
