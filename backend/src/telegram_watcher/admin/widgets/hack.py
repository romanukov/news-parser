from django.contrib.admin import widgets
from django.contrib.admin.widgets import (
    AutocompleteSelect, AutocompleteSelectMultiple,
)
from django.contrib.admin.options import get_ul_class

class FixedForeignKeyRawIdWidget(widgets.ForeignKeyRawIdWidget):
    # WARNING: Hack
    def label_and_url_for_value(self, value):
        return None, None


class ForeignKeyCachedMixin:
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Get a form Field for a ForeignKey.
        """
        db = kwargs.get('using')

        if db_field.name in self.get_autocomplete_fields(request):
            kwargs['widget'] = AutocompleteSelect(db_field.remote_field,
                                                  self.admin_site, using=db)
        elif db_field.name in self.raw_id_fields:
            kwargs['widget'] = FixedForeignKeyRawIdWidget(db_field.remote_field,
                                                          self.admin_site,
                                                          using=db)
        elif db_field.name in self.radio_fields:
            kwargs['widget'] = widgets.AdminRadioSelect(attrs={
                'class': get_ul_class(self.radio_fields[db_field.name]),
            })
            kwargs['empty_label'] = _('None') if db_field.blank else None

        if 'queryset' not in kwargs:
            queryset = self.get_field_queryset(db, db_field, request)
            if queryset is not None:
                kwargs['queryset'] = queryset

        return db_field.formfield(**kwargs)