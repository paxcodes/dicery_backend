"""configure ON DELETE CASCADE

Revision ID: f9349e8e2007
Revises: 8cc7df598021
Create Date: 2020-12-30 14:06:19.137594

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "f9349e8e2007"
down_revision = "8cc7df598021"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("room_logs_room_code_fkey", "room_logs", type_="foreignkey")
    op.create_foreign_key(
        None, "room_logs", "rooms", ["room_code"], ["code"], ondelete="CASCADE"
    )
    op.drop_constraint(
        "room_players_room_code_fkey", "room_players", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "room_players", "rooms", ["room_code"], ["code"], ondelete="CASCADE"
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "room_players", type_="foreignkey")
    op.create_foreign_key(
        "room_players_room_code_fkey", "room_players", "rooms", ["room_code"], ["code"]
    )
    op.drop_constraint(None, "room_logs", type_="foreignkey")
    op.create_foreign_key(
        "room_logs_room_code_fkey", "room_logs", "rooms", ["room_code"], ["code"]
    )
    # ### end Alembic commands ###