"""add tenant foundations - Modified to BackFill tenancy column

Revision ID: 8c600c6f73d0
Revises: ae6f0f72576f
Create Date: 2026-11-01 18:17:31.998323

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c600c6f73d0'
down_revision: Union[str, Sequence[str], None] = 'ae6f0f72576f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create tenants
    op.create_table(
        "tenants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_tenants_slug",
        "tenants",
        ["slug"],
        unique=True,
    )

    # 2. Create users
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("external_issuer", sa.String(500), nullable=False),
        sa.Column("external_subject", sa.String(255), nullable=False),
        sa.Column("email", sa.String(320), nullable=True),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "external_issuer",
            "external_subject",
            name="uq_users_external_identity",
        ),
    )

    # 3. Create API keys
    op.create_table(
        "api_keys",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("key_prefix", sa.String(32), nullable=False),
        sa.Column("key_hash", sa.String(128), nullable=False),
        sa.Column("permissions", sa.JSON(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_api_keys_tenant_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key_hash"),
    )

    op.create_index(
        "ix_api_keys_key_prefix",
        "api_keys",
        ["key_prefix"],
    )
    op.create_index(
        "ix_api_keys_tenant_id",
        "api_keys",
        ["tenant_id"],
    )

    # 4. Create tenant memberships
    op.create_table(
        "tenant_memberships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "role",
            sa.String(50),
            server_default="viewer",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_tenant_memberships_tenant_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_tenant_memberships_user_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "user_id",
            name="uq_tenant_memberships_tenant_user",
        ),
    )

    op.create_index(
        "ix_tenant_memberships_tenant_id",
        "tenant_memberships",
        ["tenant_id"],
    )
    op.create_index(
        "ix_tenant_memberships_user_id",
        "tenant_memberships",
        ["user_id"],
    )

    # 5. Create a deterministic development tenant
    tenant_id = uuid.UUID("d9e20000-0000-4000-8000-000000000001")

    op.bulk_insert(
        sa.table(
            "tenants",
            sa.column("id", sa.Uuid()),
            sa.column("name", sa.String()),
            sa.column("slug", sa.String()),
        ),
        [
            {
                "id": tenant_id,
                "name": "Atlas Development",
                "slug": "atlas-development",
            }
        ],
    )

    # 6. Add nullable tenant columns
    op.add_column(
        "documents",
        sa.Column("tenant_id", sa.Uuid(), nullable=True),
    )

    op.add_column(
        "document_chunks",
        sa.Column("tenant_id", sa.Uuid(), nullable=True),
    )

    op.add_column(
        "conversations",
        sa.Column("tenant_id", sa.Uuid(), nullable=True),
    )

    # 7. Backfill existing documents and conversations
    tenant_param = sa.bindparam("tenant_id", type_=sa.Uuid())

    op.execute(
        sa.text(
            "UPDATE documents SET tenant_id = :tenant_id "
            "WHERE tenant_id IS NULL"
        ).bindparams(tenant_param).params(tenant_id=tenant_id)
    )

    op.execute(
        sa.text(
            "UPDATE conversations SET tenant_id = :tenant_id "
            "WHERE tenant_id IS NULL"
        ).bindparams(tenant_param).params(tenant_id=tenant_id)
    )

    # 8. Backfill chunks from their parent documents
    op.execute(
        sa.text("""
            UPDATE document_chunks AS chunks
            SET tenant_id = documents.tenant_id
            FROM documents
            WHERE chunks.document_id = documents.id
              AND chunks.tenant_id IS NULL
        """)
    )

    # 9. Enforce NOT NULL
    op.alter_column(
        "documents",
        "tenant_id",
        existing_type=sa.Uuid(),
        nullable=False,
    )

    op.alter_column(
        "document_chunks",
        "tenant_id",
        existing_type=sa.Uuid(),
        nullable=False,
    )

    op.alter_column(
        "conversations",
        "tenant_id",
        existing_type=sa.Uuid(),
        nullable=False,
    )

    # 10. Add document composite uniqueness
    op.create_unique_constraint(
        "uq_documents_tenant_id_id",
        "documents",
        ["tenant_id", "id"],
    )

    # 11. Add foreign keys
    op.create_foreign_key(
        "fk_documents_tenant_id",
        "documents",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "fk_conversations_tenant_id",
        "conversations",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Remove the previous single-column foreign key.
    op.drop_constraint(
        "document_chunks_document_id_fkey",
        "document_chunks",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "fk_document_chunks_tenant_document",
        "document_chunks",
        "documents",
        ["tenant_id", "document_id"],
        ["tenant_id", "id"],
        ondelete="CASCADE",
    )

    # 12. Add indexes
    op.create_index(
        "ix_documents_tenant_id",
        "documents",
        ["tenant_id"],
    )

    op.create_index(
        "ix_document_chunks_tenant_id",
        "document_chunks",
        ["tenant_id"],
    )

    op.create_index(
        "ix_conversations_tenant_id",
        "conversations",
        ["tenant_id"],
    )


def downgrade() -> None:
    # Remove foreign keys first
    op.drop_constraint(
        "fk_document_chunks_tenant_document",
        "document_chunks",
        type_="foreignkey",
    )

    # Restore the previous index from the prior migration for consistency
    op.create_foreign_key(
        "document_chunks_document_id_fkey",
        "document_chunks",
        "documents",
        ["document_id"],
        ["id"],
    )

    op.drop_constraint(
        "fk_conversations_tenant_id",
        "conversations",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_documents_tenant_id",
        "documents",
        type_="foreignkey",
    )

    op.drop_constraint(
        "uq_documents_tenant_id_id",
        "documents",
        type_="unique",
    )

    # Remove indexes
    op.drop_index("ix_conversations_tenant_id", table_name="conversations")
    op.drop_index("ix_document_chunks_tenant_id", table_name="document_chunks")
    op.drop_index("ix_documents_tenant_id", table_name="documents")

    # Remove tenant columns
    op.drop_column("conversations", "tenant_id")
    op.drop_column("document_chunks", "tenant_id")
    op.drop_column("documents", "tenant_id")

    # Remove newly created tables
    op.drop_table("tenant_memberships")
    op.drop_table("api_keys")
    op.drop_table("users")

    op.drop_index("ix_tenants_slug", table_name="tenants")
    op.drop_table("tenants")
