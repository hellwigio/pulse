"""Move category ownership to questions, preserving existing associations."""
from alembic import op
import sqlalchemy as sa

revision = '9c2a8e41b670'
down_revision = '0f1ed447632d'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    duplicates = connection.execute(sa.text(
        'SELECT question_id FROM categories GROUP BY question_id HAVING COUNT(*) > 1'
    )).first()
    if duplicates:
        raise RuntimeError('Multiple categories reference one question; resolve duplicates before upgrading')
    # The old category_id was unused: the ORM association is authoritative.
    connection.execute(sa.text(
        'UPDATE questions SET category_id = '
        '(SELECT id FROM categories WHERE categories.question_id = questions.id)'
    ))
    with op.batch_alter_table('categories', naming_convention={
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s'
    }) as batch:
        batch.drop_constraint('fk_categories_question_id_questions', type_='foreignkey')
        batch.drop_column('question_id')
    with op.batch_alter_table('questions') as batch:
        batch.create_foreign_key('fk_questions_category_id_categories', 'categories', ['category_id'], ['id'])


def downgrade():
    connection = op.get_bind()
    incompatible = connection.execute(sa.text(
        'SELECT categories.id FROM categories LEFT JOIN questions '
        'ON questions.category_id = categories.id GROUP BY categories.id HAVING COUNT(questions.id) != 1'
    )).first()
    if incompatible:
        raise RuntimeError('Downgrade requires exactly one question per category')
    with op.batch_alter_table('questions') as batch:
        batch.drop_constraint('fk_questions_category_id_categories', type_='foreignkey')
    op.add_column('categories', sa.Column('question_id', sa.Integer(), nullable=True))
    connection.execute(sa.text(
        'UPDATE categories SET question_id = '
        '(SELECT id FROM questions WHERE questions.category_id = categories.id)'
    ))
    with op.batch_alter_table('categories') as batch:
        batch.alter_column('question_id', existing_type=sa.Integer(), nullable=False)
        batch.create_foreign_key('fk_categories_question_id_questions', 'questions', ['question_id'], ['id'])
