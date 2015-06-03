"""empty message

Revision ID: 1aaa22ae9aa2
Revises: 492155420b67
Create Date: 2015-06-02 03:21:10.949056

"""

# revision identifiers, used by Alembic.
revision = '1aaa22ae9aa2'
down_revision = '492155420b67'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('card', sa.Column('weekly_commits', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('card', 'weekly_commits')
    ### end Alembic commands ###