"""empty message

Revision ID: 6d8b8934df38
Revises: cce9d054cc41
Create Date: 2019-04-20 13:54:43.657184

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d8b8934df38'
down_revision = 'cce9d054cc41'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('challenge_progress', sa.Column('finished', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('challenge_progress', 'finished')
    # ### end Alembic commands ###
