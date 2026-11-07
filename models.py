import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    decks = db.relationship("Deck", backref="owner", lazy=True)


class Card(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))
    card_class = db.Column(db.String(50))
    level = db.Column(db.Integer)
    power = db.Column(db.Integer)
    color = db.Column(db.String(100))
    text = db.Column(db.Text)
    image_url = db.Column(db.Text)

    # ★新規追加: IRIS ONE判定 (デフォルトはFalse)
    is_iris_one = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "class": self.card_class,
            "level": self.level,
            "power": self.power,
            "color": self.color,
            "text": self.text,
            "image_url": self.image_url,
            "is_iris_one": self.is_iris_one,  # ★追加
        }


class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    cards = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "cards": json.loads(self.cards)}
