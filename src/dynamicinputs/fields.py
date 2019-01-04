import json

from django.core import checks
from django.utils import six
from django.core.exceptions import ValidationError
from django.forms import Field
from django.utils.translation import ugettext_lazy as _

from jsonfield import JSONField

from .widgets import DynamicInputsWidget


class DynamicInputField(Field):
    """
    Form field for handling dynamic list of fields (instances of field param)
    """
    widget = DynamicInputsWidget
    default_error_messages = {
        'required': _('At least one field is required.'),
    }

    def __init__(self, field, default_count=1, max_count=None, button='Add', *args, **kwargs):
        self.field = field
        self.default_count = default_count
        self.max_count = max_count
        self.button = button

        label = kwargs.pop('label', None)
        help_text = kwargs.pop('help_text', None)
        kwargs.pop('max_length', None)
        # Allow only DictionaryWidget and its subclasses to act as widget
        if 'widget' in kwargs and not (
                    isinstance(kwargs['widget'], DynamicInputsWidget) or
                    issubclass(kwargs['widget'], DynamicInputsWidget)):
            kwargs.pop('widget')

        super(DynamicInputField, self).__init__(
            label=self.field.label or label,
            help_text=self.field.help_text or help_text,
            *args, **kwargs)
        self.widget.set_params(self.field.widget, default_count, max_count, button)

    def prepare_value(self, value):
        if isinstance(value, six.string_types):
            try:
                value = json.loads(value)
            except ValueError:
                value = []
        return value

    def validate(self, value):
        """
        Validate generic rules
        """
        if not value and self.required:
            raise ValidationError(self.error_messages["required"])

    def clean(self, value):
        """
        Call .clean() for each row
        """
        self.validate(value)
        return [self.field.clean(it) for it in value]

    def has_changed(self, initial, data):
        # make sure initial is deserialized before comparing
        if isinstance(initial, six.string_types):
            try:
                initial = json.loads(initial)
            except (TypeError, ValueError):
                pass
        return super(DynamicInputField, self).has_changed(initial, data)


class ArrayField(JSONField):
    """
    Model field for storing DynamicInputField data in JSON array format
    """
    form_class = DynamicInputField

    def __init__(self, *args, **kwargs):
        self.field = kwargs.pop('field', None)
        self.default_count = kwargs.pop('default_count', None)
        self.max_count = kwargs.pop('max_count', None)
        self.button = kwargs.pop('button', None)
        super(ArrayField, self).__init__(*args, **kwargs)

    def check(self, **kwargs):
        errors = super(ArrayField, self).check(**kwargs)
        errors.extend(self._check_field_attribute(**kwargs))
        return errors

    def _check_field_attribute(self, **kwargs):
        if self.field is None:
            return [
                checks.Error(
                    "ArrayFields must define a 'field' attribute.",
                    obj=self,
                )
            ]
        elif not isinstance(self.field, Field):
            return [
                checks.Error(
                    "'field' must be a django.forms.fields.Field instance",
                    obj=self,
                )
            ]
        return []

    def formfield(self, **kwargs):
        defaults = {'field': self.field}
        for attribute_name in ('default_count', 'max_count', 'button'):
            if getattr(self, attribute_name, None) is not None:
                defaults[attribute_name] = getattr(self, attribute_name)
        defaults.update(kwargs)
        field = super(ArrayField, self).formfield(**defaults)
        field.is_hidden = False
        # we don't need default help_text set by JSONFieldBase.formfield
        if not defaults.get('help_text') and not self.help_text:
            field.help_text = ""
        return field
