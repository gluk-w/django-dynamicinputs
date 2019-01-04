# Form field with variable list of rows

Requires Django framework and jQuery javascript library.

## Installation

```
pip install dynamicinputs
```

## Usage
Add "dynamicinputs" to installed apps in django settings file:

```python
INSTALLED_APPS = (
    ...
    'dynamicinputs',
    ...
)
```

Then it can be used in model:

```python
from dynamicinputs import DynamicInputField

parent_names = DynamicInputField(
        fields.CharField(
            label="Names and addresses of parent companies",
            widget=widgets.Textarea(),
            help_text="If your publishing company has no parent companies then enter 'none'"),
        max_count=10,
        button='Add company')
    )
```

Include required css and js files into your template:

```
{% load static %}

<link href="{% static 'dynamicinputs/dynamicinputs.css' %}" rel="stylesheet"/>
<script type="text/javascript" src="{% static 'dynamicinputs/dynamicinputs.js' %}"></script>
```

