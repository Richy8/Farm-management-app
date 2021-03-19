"""empty message

Revision ID: 64230b51cad3
Revises: f6f9bb3e2f05
Create Date: 2019-08-03 13:16:08.482647

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '64230b51cad3'
down_revision = 'f6f9bb3e2f05'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('customers', sa.Column('city', sa.String(length=50), nullable=True))
    op.add_column('customers', sa.Column('region', sa.String(length=50), nullable=True))
    op.add_column('customers', sa.Column('state', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('customers', 'state')
    op.drop_column('customers', 'region')
    op.drop_column('customers', 'city')
    # ### end Alembic commands ###