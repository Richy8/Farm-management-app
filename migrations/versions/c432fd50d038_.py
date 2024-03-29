"""empty message

Revision ID: c432fd50d038
Revises: 
Create Date: 2019-06-07 13:51:49.904418

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c432fd50d038'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('feedstocks', sa.Column('u_prod', sa.Float(), nullable=True, default=0))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('feedstocks', 'u_prod')
    # ### end Alembic commands ###
