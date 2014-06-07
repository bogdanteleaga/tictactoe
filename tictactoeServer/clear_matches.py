#!flask/bin/python
from app import db, models
all_matches = models.Match.query.all()
for m in all_matches:
    db.session.delete(m)
db.session.commit()
