"""empty message

Revision ID: ca4a5853e61f
Revises: 
Create Date: 2022-04-07 11:07:41.342800

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'ca4a5853e61f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('lga')
    op.drop_table('donation')
    op.alter_column('breakout', 'break_amt',
               existing_type=mysql.FLOAT(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('breakout', 'break_amt',
               existing_type=mysql.FLOAT(),
               nullable=False)
    op.create_table('donation',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('fullname', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('email', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('amt', mysql.FLOAT(), nullable=True),
    sa.Column('date', mysql.TIMESTAMP(), server_default=sa.text('current_timestamp()'), nullable=True),
    sa.Column('status', mysql.ENUM('pending', 'paid', 'failed'), nullable=True),
    sa.Column('ref', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('others', mysql.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('lga',
    sa.Column('lga_id', mysql.INTEGER(display_width=10, unsigned=True), autoincrement=True, nullable=False),
    sa.Column('state_id', mysql.INTEGER(display_width=11), server_default=sa.text('0'), autoincrement=False, nullable=False),
    sa.Column('lga_name', mysql.VARCHAR(length=50), server_default=sa.text("''"), nullable=False),
    sa.PrimaryKeyConstraint('lga_id'),
    mysql_default_charset='utf8',
    mysql_engine='MyISAM'
    )
    # ### end Alembic commands ###
