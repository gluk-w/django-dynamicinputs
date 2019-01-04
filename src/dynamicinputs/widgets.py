import itertools

from collections import Iterable

from django.template.loader import render_to_string
from django.forms import Widget


class DynamicInputsWidget(Widget):
    """
    Form Widget
    """
    template_name = 'dynamicinputs/skeleton.html'

    class Media:
        css = {
            'all': ('dynamicinputs/dynamicinputs.css',)
        }
        js = ('dynamicinputs/dynamicinputs.js',)

    def __init__(self, *args, **kwargs):
        super(DynamicInputsWidget, self).__init__(*args, **kwargs)

    def set_params(self, widget, default_count, max_count, button):
        """
        Set basic widget
        """
        self._subwidget = widget
        self.default_count = default_count
        self.max_count = max_count
        self.button = button

    def has_value(self, val):
        """
        Check if value is either empty or a dict with empty values
        """
        if isinstance(val, dict):
            return any(val.values())
        if isinstance(val, Iterable):
            return any(val)
        return bool(val)

    def value_from_datadict(self, data, files, name):
        new_data = []
        result = []

        # Convert datadict to list of dictionaries with single value
        # for each key related to current field
        for key, values in data.lists():
            if not key.startswith(name) or values is None:
                continue

            new_data.append([
                {key: val}
                for val in values
            ])

        for group in zip(*new_data):
            item = dict(itertools.chain.from_iterable(
                it.items() for it in group)
            )
            if self.has_value(item):
                result.append(self._subwidget.value_from_datadict(item, files, name))

        return result

    def render(self, name, value, attrs=None):
        if value is None or not isinstance(value, list):
            value = []
        else:
            # Filter out empty values
            value = [v for v in value if v]

        inputs = []

        # Store "required" value
        _required = self._subwidget.is_required
        self._subwidget.is_required = False

        # Hidden sample
        sample = self._subwidget.render(name, None)

        rows_number = max(self.default_count, len(value))
        if getattr(self, 'max_count', None) is not None:
            if rows_number > self.max_count:
                rows_number = self.max_count

        for v in range(rows_number):
            try:
                val = value[v]
            except Exception as e:
                val = None

            # Required (if it is required) should only be $default_count number of rows
            self._subwidget.is_required = _required if v < rows_number else False

            inputs.append(self._subwidget.render(name, val))

        return render_to_string(self.template_name, {
            'name': name,
            'sample': sample,
            'inputs': inputs,
            'button': self.button,
            'max': self.max_count,
            'min': self.default_count
        })

    def id_for_label(self, id_):
        if id_:
            id_ = 'dynamicinputs_' + id_
        return id_
