from .. import db

from .mixins import IdMixin

# Both users and  can have roles
class Role(db.Model, IdMixin):
    __tablename__ = "roles"
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    permissions = db.Column(db.BigInteger, default=0)

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return "<Role %r>" % (self.name)
