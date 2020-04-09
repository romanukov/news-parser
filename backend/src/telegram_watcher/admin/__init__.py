from django import forms
from django.forms import widgets
from django.contrib.admin import ModelAdmin, TabularInline, StackedInline

from telegram_watcher.admin.user import MyUserAdmin
from telegram_watcher.models import Source, Message, UserSource, Feed, SourceGroup, User, TelegramAccount, MessageFile
from django.contrib.admin import site
from .user import MyUserAdmin
from .widgets.table_select import TableSelectMultiple


class SourceAdmin(ModelAdmin):
    search_fields = 'link',


site.register(Source, SourceAdmin)
site.register(UserSource)
site.register(Feed)
site.register(Message)
site.register(MessageFile)


class AccountAdmin(ModelAdmin):
    readonly_fields = ('amount_sources', 'authorized', 'phone_code_hash', 'runned')
    list_display = ('id', 'phone', 'amount_sources', 'runned', 'authorized')


class SourceGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_fields['sources'].help_text = ''


    class Media:
        css = {
            'all': ('https://cdn.datatables.net/1.10.7/css/jquery.dataTables.css',)
        }
        js = (
            'https://code.jquery.com/jquery-3.3.1.min.js',
            'https://cdn.datatables.net/1.10.7/js/jquery.dataTables.min.js',
        )

    class Meta:
        model = SourceGroup
        widgets = {
            'sources': TableSelectMultiple(
                item_attrs=[
                    'id',
                    'link',
                    'type'
                ],
                enable_shift_select=True,
                enable_datatables=True,
                bootstrap_style=True,
                datatable_options={
                    'paging': True,
                    "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
                    "columnDefs": [
                        {"searchable": True, "targets": 1},
                    ],
                    'searching': True
                },
            ),
        }
        fields = '__all__'

from .widgets.hack import ForeignKeyCachedMixin


class SourceGroupSourceInline(ForeignKeyCachedMixin, TabularInline):
    fields = ('source',)
    autocomplete_fields = ('source',)
    model = SourceGroup.sources.through


class SourceGroupAdmin(ModelAdmin):
    list_display = ('name', )
    fields = ('name','sources')
    autocomplete_fields = ('sources',)

    class Media:
        css = {'all': ('source_group.css',)}

    # inlines = [
    #     SourceGroupSourceInline
    # ]


site.register(TelegramAccount, AccountAdmin)
site.register(User, MyUserAdmin)
site.register(SourceGroup, SourceGroupAdmin)

