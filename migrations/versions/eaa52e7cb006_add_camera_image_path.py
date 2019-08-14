"""add camera image path

Revision ID: eaa52e7cb006
Revises: 30f675d5401b
Create Date: 2019-07-22 22:14:23.669508

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eaa52e7cb006'
down_revision = '30f675d5401b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('camera', sa.Column('image', sa.String(length=128), nullable=True))
    op.create_index(op.f('ix_camera_image'), 'camera', ['image'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_camera_image'), table_name='camera')
    op.drop_column('camera', 'image')
    # ### end Alembic commands ###
