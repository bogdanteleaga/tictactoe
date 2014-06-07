from app import db, app
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context


class User(db.Model):
    """User model in database"""
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(64))
    p1 = db.relationship('Match', backref='p1', lazy='dynamic',
                         primaryjoin="User.id==Match.player1")
    p2 = db.relationship('Match', backref='p2', lazy='dynamic',
                         primaryjoin="User.id==Match.player2")

    def hash_password(self, password):
        """Create password hash"""
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        """Verify password hash"""
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        """Generate token"""
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        """Verifies token and returns user"""
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user

    def __repr__(self):
        return '<User %r>' % (self.nickname)


class Match(db.Model):
    """Match model in database"""
    id = db.Column(db.Integer, primary_key=True)
    player1 = db.Column(db.Integer, db.ForeignKey('user.id'))
    player2 = db.Column(db.Integer, db.ForeignKey('user.id'))
    winner = db.Column(db.Integer, index=True)

    def __repr__(self):
        """Temporarily a match might get created without a second player"""
        return '<Match between %s and %s winner %s>' % (self.p1.nickname,
                                                        (self.p2.nickname if
                                                         self.p2
                                                         else "None"),
                                                        self.winner)
