from django.contrib import admin
from .models import Prestizas, Profilis, Receptas, Reitingas, Komentaras, Raktazodis, Sablonas, ReceptoRaktazodis


class ReceptoRaktazodisInline(admin.TabularInline):
    model = ReceptoRaktazodis
    extra = 1


class ReceptasAdmin(admin.ModelAdmin):
    list_display = (
    'titulas', 'vidutinis_reitingas', 'reitingu_kiekis', 'favoritu_kiekis', 'gaminimo_laikas', 'ar_veganiskas',
    'ar_vegetariskas', 'data', 'sablonas')
    search_fields = ('titulas', 'aprasas')
    list_filter = ('ar_veganiskas', 'ar_vegetariskas', 'sablonas')

    inlines = [ReceptoRaktazodisInline]


class ProfilisAdmin(admin.ModelAdmin):
    list_display = ('profilis', 'vardas', 'prestizo_taskai', 'prestizas')
    fields = ('profilis', 'vardas', 'aprasas', 'nuotrauka', 'prestizo_taskai', 'prestizas')


class ReitingasAdmin(admin.ModelAdmin):
    list_display = ('profilis', 'receptas', 'favoritas', 'reitingas')


class KomentarasAdmin(admin.ModelAdmin):
    list_display = ('receptas', 'profilis', 'turinys')


class PrestizasAdmin(admin.ModelAdmin):
    list_display = ('lygio_pavadinimas', 'tasku_reikalavimas')


class SablonasAdmin(admin.ModelAdmin):
    list_display = ('pavadinimas', 'aprasas')


admin.site.register(Prestizas, PrestizasAdmin)
admin.site.register(Profilis, ProfilisAdmin)
admin.site.register(Receptas, ReceptasAdmin)
admin.site.register(Reitingas, ReitingasAdmin)
admin.site.register(Komentaras, KomentarasAdmin)
admin.site.register(Sablonas, SablonasAdmin)
admin.site.register(Raktazodis)
