"""embedding_dimension_768

Revision ID: a10226436f1b
Revises: 93f083eb884e
Create Date: 2026-10-27 19:33:40.584270

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a10226436f1b'
down_revision: Union[str, Sequence[str], None] = '93f083eb884e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
      op.execute("ALTER TABLE embeddings ALTER COLUMN vector TYPE vector(768)")

def downgrade() -> None:
      op.execute("ALTER TABLE embeddings ALTER COLUMN vector TYPE vector(1536)")