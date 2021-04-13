from django.contrib import admin
from .models import Catalog, CustomField, Record, Provenance, Manufacturer

# Register your models here.

class CatalogAdmin(admin.ModelAdmin):
    def get_changeform_initial_data(self, request):
        get_data = super(CatalogAdmin, self).get_changeform_initial_data(request)
        get_data['created_by'] = request.user.pk
        return get_data

admin.site.register(Record)
admin.site.register(Catalog, CatalogAdmin)
admin.site.register(CustomField)
admin.site.register(Provenance)
admin.site.register(Manufacturer)