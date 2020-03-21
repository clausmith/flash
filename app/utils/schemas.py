from marshmallow.fields import Nested


class PatchedNested(Nested):
    """ Patches marshmallow.fileds.Nested to enable symmetric
        serialization/deserialization of Nested fields.
    """

    def _deserialize(self, value, attr, data):
        if self.many and not utils.is_collection(value):
            self.fail("type", input=value, type=value.__class__.__name__)

        if isinstance(self.only, str):  # self.only is a field name
            if self.many:
                value = [{self.only: v} for v in value]
            else:
                value = {self.only: value}
        data, errors = self.schema.load(value)
        if errors:
            raise ValidationError(errors, data=data)
        return data
