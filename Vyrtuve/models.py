from django.db import models
from django.contrib.auth.models import User


class Prestizas(models.Model):
    """
    Modelis Prestižas apibrėžia duomenų struktūrą apie prestižo lygius ir jų reikalavimus.
    """

    PASIRINKIMAI = (
        ("Prestizo lygis įprastas", "Įprastas"),
        ("Prestizo lygis bronzinis", "Bronzinis"),
        ("Prestizo lygis sidabrinis", "Sidabrinis"),
        ("Prestizo lygis auksinis", "Auksinis"),
        ("Prestizo lygis Administratorius", "Administratorius"),
    )
    lygio_pavadinimas = models.CharField(choices=PASIRINKIMAI, max_length=40, blank=True, null=True)
    tasku_reikalavimas = models.IntegerField()
    ikona = models.ImageField(upload_to='prestizo_ikonai/', blank=True, null=True)

    def __str__(self):
        return f"{self.lygio_pavadinimas}"


class Profilis(models.Model):
    """
    Modelis Profilis apibrėžia duomenų struktūrą ir bei veikimą susijusį su vartotojų profiliais.
    """
    profilis = models.OneToOneField(User, on_delete=models.CASCADE)
    vardas = models.CharField(max_length=50)
    aprasas = models.TextField(max_length=2000)
    nuotrauka = models.ImageField(upload_to='profiliu_nuotraukos/', blank=True, default='default-user.png')
    prestizas = models.ForeignKey(Prestizas, on_delete=models.SET_NULL, null=True, blank=True)
    prestizo_taskai = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.vardas} Profilis"

    def save(self, *args, **kwargs):
        """
        Ši save() funkcija yra iškviečiama kiekvieną kartą ivykus pakeitimams Profilio modeliui.
        Ši funkcija egzistuoja dėl to, kad priskirtų defaultinę nuotrauką profiliui kuris jos neturi.
        """
        if not self.nuotrauka:
            self.nuotrauka = 'default-user.png'
        super().save(*args, **kwargs)

    def recalculate_prestige(self, recipe_id):
        """
        recalculate_prestige() yra iškviečiama vartotojui įvedus favoritą arba reitingą.
        Šios funkcijos darbas yra perskaičiuoti įvertinto recepto savininko prestižo lygį
        naudojantis jų visų receptų reitingais ir favoritais.
        """
        recipe = Receptas.objects.get(id=recipe_id)

        profile = recipe.profilis

        total_prestige = 0

        ratings = recipe.reitingai.all()

        for rating in ratings:
            if rating.favoritas:
                total_prestige += 4
            if rating.reitingas == 5:
                total_prestige += 6

        profile.prestizo_taskai = total_prestige
        profile.save()

        profile.update_prestige_level()

    def update_prestige_level(self):
        """
        update_prestige_level() yra iškviečiama vartotojui įvedus favoritą arba reitingą.
        (nes tai iškviečia recalculate_prestige, kuris iškviečia šią funkciją).

        Šios funkcijos darbas yra paskirti tinkamą prestižo lygį atsižvelgiant į profilio prestižo taškus
        ir prestižo lygio taškų reikalavimus.
        """
        prestige_levels = Prestizas.objects.all()

        for level in prestige_levels.order_by('-tasku_reikalavimas'):
            if self.prestizo_taskai >= level.tasku_reikalavimas:
                self.prestizas = level
                break

        self.save()


class Sablonas(models.Model):
    """
    Modelis Sablonas apibrėžia duomenų struktūrą apie šablonus ir jų aprašus.
    """
    pavadinimas = models.CharField(max_length=50)
    aprasas = models.TextField(max_length=2000)

    def __str__(self):
        return self.pavadinimas


class Receptas(models.Model):
    """
    Modelis Receptas apibrėžia duomenų struktūrą ir bei veikimą susijusį su įkeltais receptais,
    be to jame kaupiama informacija apie tai kuris vartotojas sukūrė receptą, bei kurį šabloną naudot vaizduojant jį.
    """
    titulas = models.CharField(max_length=50)
    aprasas = models.TextField(max_length=2000)
    ingridientai = models.TextField(max_length=2000)
    instrukcijos = models.TextField(max_length=2000)
    nuotrauka = models.ImageField(upload_to='receptai/', blank=True, null=True)
    gaminimo_laikas = models.FloatField()

    vidutinis_reitingas = models.FloatField(default=0)
    reitingu_kiekis = models.IntegerField(default=0)

    favoritu_kiekis = models.IntegerField(default=0)

    ar_vegetariskas = models.BooleanField(default=False)
    ar_veganiskas = models.BooleanField(default=False)

    data = models.DateTimeField(auto_now_add=True)

    sablonas = models.ForeignKey(Sablonas, on_delete=models.SET_NULL, null=True)
    profilis = models.ForeignKey(Profilis, related_name='receptai', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.titulas

    def start_counting(self):
        """
        Funkcija start_counting() yra iškviečiama pateikus pakeitimus reitinguose ir favorituose.
        Iškviesta, ši funkcija naujai suskaičiuoja favoritų ir reitingų kiekį, bei vidutinį recepto reitingą.
        """
        ratings = self.reitingai.all()

        self.reitingu_kiekis = ratings.count()

        total_rating = 0

        for rating in ratings:
            total_rating += rating.reitingas

        if self.reitingu_kiekis > 0:
            self.vidutinis_reitingas = total_rating / self.reitingu_kiekis
        else:
            self.vidutinis_reitingas = 0

        self.favoritu_kiekis = ratings.filter(favoritas=True).count()

        self.save()


class Reitingas(models.Model):
    """
    Modelis Reitingas apibrėžia duomenų struktūrą apie reitingus ir pasirūpina, kad būtų tik vienas reitingas per profilį,
    be to jame nusakoma kuriame recepte kuris profilis paliko reitingą arba favoritą.
    """
    receptas = models.ForeignKey(Receptas, related_name='reitingai', on_delete=models.CASCADE, null=True)
    profilis = models.ForeignKey(Profilis, related_name='reitingai', on_delete=models.CASCADE, null=True)

    favoritas = models.BooleanField(default=False)
    reitingas = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=1)

    class Meta:
        unique_together = ['receptas', 'profilis']

    def __str__(self):
        return f"Reitingas {self.receptas.titulas} nuo {self.profilis.vardas}"


class Komentaras(models.Model):
    """
    Modelis Komentaras apibrėžia duomenų struktūrą apie komentarus ir jų turinį,
    be to jame nusakoma kuriame recepte kuris profilis paliko komentarą.
    """
    receptas = models.ForeignKey(Receptas, related_name='komentarai', on_delete=models.CASCADE, null=True)
    profilis = models.ForeignKey(Profilis, related_name='komentarai', on_delete=models.CASCADE, null=True)

    data = models.DateTimeField(auto_now_add=True)

    turinys = models.TextField(max_length=2000)

    def __str__(self):
        return f"Komentaras {self.receptas.titulas} nuo {self.profilis.vardas}"


class Raktazodis(models.Model):
    """
    Modelis Sablonas apibrėžia duomenų struktūrą apie raktažodžius.
    """
    raktazodis = models.CharField(max_length=50)

    def __str__(self):
        return self.raktazodis


class ReceptoRaktazodis(models.Model):
    """
    Modelis ReceptoRaktazodis naudojamas tam, kad nusakytų kuris raktažodis nustatytas kuriame recepte.
    """
    receptas = models.ForeignKey(Receptas, related_name='raktazodziai_recepto', on_delete=models.CASCADE)
    raktazodis = models.ForeignKey(Raktazodis, related_name='raktazodziai_recepto', on_delete=models.CASCADE)

    def __str__(self):
        return f"Keyword {self.raktazodis.raktazodis} for {self.receptas.titulas}"
