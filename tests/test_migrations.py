from flask_migrate import upgrade, downgrade
from sqlalchemy import text

from pulse import create_app
from pulse.models import db


def test_category_migration_preserves_data(tmp_path):
    class Config:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{tmp_path / "migration.db"}'

    app = create_app(Config)
    with app.app_context():
        upgrade(revision='0f1ed447632d')
        db.session.execute(text("INSERT INTO questions (id, text) VALUES (1, 'Question?'), (2, 'Other?')"))
        db.session.execute(text("INSERT INTO answers (is_agree, question_id) VALUES (1, 1)"))
        db.session.execute(text("INSERT INTO categories (id, name, question_id) VALUES (3, 'General', 1)"))
        db.session.commit()
        upgrade()
        client = app.test_client()
        assert client.get('/questions/1').get_json()['category'] == {'id': 3, 'name': 'General'}
        assert client.get('/questions/2').get_json()['category'] is None
        assert client.get('/answers').get_json()[0]['question_id'] == 1
        assert db.session.execute(text('PRAGMA foreign_key_check')).all() == []
        db.session.remove()
        downgrade(revision='0f1ed447632d')
        assert db.session.execute(text('SELECT question_id FROM categories')).scalar() == 1
        db.session.remove()
        upgrade()
        assert client.get('/questions/1').get_json()['category_id'] == 3
