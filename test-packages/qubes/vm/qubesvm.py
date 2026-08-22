def get_active_template(self):
    return getattr(self, "active_template", getattr(self, "template", None))


class QubesVM:
    pass
