"""init db

Revision ID: 9e54ba0246cc
Revises:
Create Date: 2025-06-22 02:15:17.197633

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9e54ba0246cc"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "file_metadata",
        sa.Column("file_metadata_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("file_name", sa.String(), nullable=False),
        sa.Column("file_size", sa.Numeric(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "ARCHIVED", "DAMAGED", name="filestatus"), nullable=False),
        sa.Column("uploaded_at", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("file_metadata_id"),
    )
    op.create_index(op.f("ix_file_metadata_file_name"), "file_metadata", ["file_name"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_file_metadata_file_name"), table_name="file_metadata")
    op.drop_table("file_metadata")
    # ### end Alembic commands ###
