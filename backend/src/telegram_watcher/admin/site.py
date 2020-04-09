from django.contrib import admin


class AdminSite(admin.AdminSite):
    site_header = "Telegram parser"
    site_title = "Telegram parser"
    index_title = ""


site = AdminSite()
