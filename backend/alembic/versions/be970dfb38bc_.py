"""empty message

Revision ID: be970dfb38bc
Revises: 30486836a7cc
Create Date: 2026-08-09 17:22:50.985444

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = 'be970dfb38bc'
down_revision: str | Sequence[str] | None = '30486836a7cc'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
