import pytest
from collections import OrderedDict

from django.db.models.fields import Field
from django.forms import fields, widgets, Form
from django.utils import six
from django.utils.datastructures import MultiValueDict

from dictionaryfield.fields import DictionaryFormField

from dynamicinputs.fields import ArrayField, DynamicInputField


class SampleForm(Form):
    parent_names = DynamicInputField(
        fields.CharField(
            label="Names and addresses of parent companies",
            widget=widgets.Textarea(),
            help_text="If your publishing company has no parent companies then enter 'none'"),
        max_count=10,
        button='Add company',
        error_messages={'required': 'Custom error message'}
    )
    editorial_management = DynamicInputField(
        DictionaryFormField(
            OrderedDict([
                ('name', fields.CharField(label="Name")),
                ('title', fields.CharField(label="Title")),
            ])
        ),
        required=False
    )


class NestedForm(Form):
    dict_field = DictionaryFormField(
        OrderedDict([
            ('dynamic_field', DynamicInputField(
                DictionaryFormField(
                    fields=OrderedDict([
                        ('name', fields.CharField(
                            label="Name",
                            required=True,
                        )),
                        ('title', fields.CharField(
                            label="Specific responsibilities",
                            required=True,
                        )),
                    ])),
            ))
        ])
    )


def test_no_data():
    test_form = SampleForm()
    rendered_field = six.text_type(test_form['parent_names'])
    assert rendered_field.count('<div class="dynamicinputs-row">') == 1
    assert rendered_field.count("Delete row") == 2
    assert rendered_field.count('<textarea cols="40" name="parent_names" rows="10">') == 2


def test_multiple_rows():
    test_form = SampleForm(MultiValueDict({'parent_names': ['one', 'two']}))
    assert test_form.is_valid() == True
    assert test_form.cleaned_data['parent_names'] == ['one', 'two']
    rendered_field = six.text_type(test_form['parent_names'])
    assert rendered_field.count('<div class="dynamicinputs-row">') == 2
    assert rendered_field.count("Delete row") == 4
    assert rendered_field.count('<textarea cols="40" name="parent_names" rows="10">') == 3
    assert 'one' in rendered_field
    assert 'two' in rendered_field


def test_empty_value():
    test_form = SampleForm(MultiValueDict({'parent_names': ['one', 'two', ''],
                                           'editorial_management__name': ['John Doe', 'Jane Poe', ''],
                                           'editorial_management__title': ['CTO', 'CEO', '']}))
    assert test_form.is_valid() == True
    assert test_form.cleaned_data['parent_names'] == ['one', 'two']
    assert test_form.cleaned_data['editorial_management'] == [
        {'name': 'John Doe', 'title': 'CTO'},
        {'name': 'Jane Poe', 'title': 'CEO'}
    ]


def test_empty_rows_submitted():
    test_form = SampleForm(data=MultiValueDict({'parent_names': None,
                                                'editorial_management__name': None,
                                                'editorial_management__title': None}))
    assert test_form.is_valid() is False, "parent_names is required"

    # editorial_management is not required that's why it should be present in cleaned_data
    assert test_form.cleaned_data == {
        "editorial_management": []
    }


def test_nested_form():
    data = MultiValueDict()
    data.setlist("dict_field__dynamic_field__name", ["name%s" % i for i in range(0, 5)])
    data.setlist("dict_field__dynamic_field__title", ["title%s" % i for i in range(0, 5)])
    form = NestedForm(data)
    assert form.is_valid()
    assert form.cleaned_data == {'dict_field': {
        'dynamic_field': [
            {'name': 'name0', 'title': 'title0'},
            {'name': 'name1', 'title': 'title1'},
            {'name': 'name2', 'title': 'title2'},
            {'name': 'name3', 'title': 'title3'},
            {'name': 'name4', 'title': 'title4'},
        ]
    }}


def test_arrayfield_formfield():
    """
    Test ``ArrayField.formfield`` method
    """
    line_field = fields.CharField(max_length=100)
    field = ArrayField("Phones", field=line_field, button="Add phone", default_count=2, max_count=10)
    form_field = field.formfield()

    assert isinstance(form_field, DynamicInputField)
    assert not form_field.help_text
    assert form_field.field == line_field
    assert form_field.button == field.button
    assert form_field.default_count == field.default_count
    assert form_field.max_count == field.max_count


@pytest.mark.parametrize('kwargs,error_expected', [
    ({}, True),
    ({'field': "Field"}, True),
    ({'field': fields.CharField(max_length=100)}, False),
])
def test_arrayfield_check(mocker, kwargs, error_expected):
    """
    Test ``ArrayField.check`` method
    :param mocker: ``pytest-mock`` fixture: Thin-wrapper around the ``mock`` package:
    :param kwargs: keyword arguments for ArrayField constructor
    :param error_expected: flag showing whether errors are expected or not
    """
    field = ArrayField(**kwargs)
    with mocker.patch.object(Field, 'check', return_value=[]):
        errors = field.check()
    assert bool(errors) == error_expected


def test_error_message():
    """
    Make sure custom error message works
    """
    test_form = SampleForm(MultiValueDict({'parent_names': []}))
    assert test_form.is_valid() is False
    assert "Custom error message" in test_form.errors['parent_names']


