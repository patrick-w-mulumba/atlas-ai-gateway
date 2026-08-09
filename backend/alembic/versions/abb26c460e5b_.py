"""empty message

Revision ID: abb26c460e5b
Revises: be970dfb38bc
Create Date: 2026-08-09 17:37:11.591023

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = 'abb26c460e5b'
down_revision: str | Sequence[str] | None = 'be970dfb38bc'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
