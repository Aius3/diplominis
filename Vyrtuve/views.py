from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q

from .forms import ProfileUpdateForm, UserUpdateForm, RecipeForm, RatingForm, CommentForm
from .models import User, Receptas, ReceptoRaktazodis, Komentaras, Reitingas, Profilis, Prestizas
from .utils import check_pasword


def index(request):
    """
    index() funkcija yra skirta suteikti teisingus duomenis index.html templateui.

    Ji ištraukia duomenis iš URL ir juos priskiria kintamiesiems kurie bus naudojami filtruose
    ir gražina prafiltruotus duomenis kurie bus naudojami index.html.

    Be to ši funkcija irgi pasirūpina index.html elementų rūšiavimu, puslapiavimu ir duplikatų panaikinimu.
    """

    query = request.GET.get('query', '')

    min_rating = request.GET.get('min_rating', None)

    vegetarian = request.GET.get('ar_vegetariskas', None)
    if vegetarian is not None:
        vegetarian = vegetarian == 'True'

    vegan = request.GET.get('ar_veganiskas', None)
    if vegan is not None:
        vegan = vegan == 'True'

    favoritas = request.GET.get('favoritas', None)
    if favoritas is not None:
        favoritas = favoritas == 'True'

    recipes = Receptas.objects.all().order_by('-vidutinis_reitingas')

    recipes = recipes.filter(
        Q(titulas__icontains=query) |
        Q(aprasas__icontains=query) |
        Q(ingridientai__icontains=query) |
        Q(raktazodziai_recepto__raktazodis__raktazodis__icontains=query)
    )

    if min_rating:
        recipes = recipes.filter(vidutinis_reitingas__gte=min_rating)

    if vegetarian is not None:
        recipes = recipes.filter(ar_vegetariskas=vegetarian)

    if vegan is not None:
        recipes = recipes.filter(ar_veganiskas=vegan)

    if favoritas is not None:
        favorite_ratings = Reitingas.objects.filter(profilis=request.user.profilis, favoritas=True)
        favorite_recipes = [rating.receptas for rating in favorite_ratings]

        if favoritas:
            recipes = recipes.filter(id__in=[recipe.id for recipe in favorite_recipes])
        else:
            recipes = recipes.exclude(id__in=[recipe.id for recipe in favorite_recipes])

    recipes = recipes.distinct()

    page = request.GET.get('page', 1)
    paginator = Paginator(recipes, 8)
    receptai = paginator.get_page(page)

    return render(request, 'index.html', {
        'receptai': receptai,
        'query': query,
        'min_rating': min_rating,
        'vegetarian': vegetarian,
        'vegan': vegan,
        'favoritas': favoritas,
    })


@csrf_protect
def register_user(request):
    """
    register_user() funkcija pasirūpina vartotojo registracijos registration.html template funkcionalumu.

    Ji pasirūpina kad į laukus įvesta tinkama informacija (ar vardo ilgis tinkamas, ar slaptažodžiai sutampa ir  t.t).

    Patvirtinus kad suteikta registracijos informacija teisinga - sukuriamas useris ir profilis.
    """
    if request.method == 'GET':
        return render(request, 'registration/registration.html')

    elif request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not check_pasword(password):
            return redirect('register')

        if password != password2:
            return redirect('register')

        if User.objects.filter(username=username).exists():
            return redirect('register')

        if User.objects.filter(email=email).exists():
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)

        default_prestizas = Prestizas.objects.first()

        profilis = Profilis.objects.create(profilis=user, prestizas=default_prestizas)

        return redirect('login')


@login_required()
def get_user_profile(request):
    """
    get_user_profile() funkcija pasirūpina prisijungusio vartotojo asmeninio profilio profile.html template funkcionalumu.

    Ji pasirūpina vartotojo asmeninio profilio duomenų atvaizdavimu ir redagavimu su įvairiomis formomis.
    """
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profilis)
        u_form = UserUpdateForm(request.POST, instance=request.user)

        if p_form.is_valid() and u_form.is_valid():
            p_form.save()
            u_form.save()
            return redirect('user-profile')

    else:
        p_form = ProfileUpdateForm(instance=request.user.profilis)
        u_form = UserUpdateForm(instance=request.user)

    context = {
        'p_form': p_form,
        'u_form': u_form,
    }

    return render(request, 'profile.html', context=context)


@login_required
def submit_recipe(request):
    """
    submit_recipe() funkcija pasirūpina prisijungusio vartotojo recepto publikavimo submit_recipe.html template funkcionalumu.

    Ji patikrina ar įvesti teisingi duomenys ir suteikia galimybę kiekvienam vartotojui įkelti savo receptą naudojantis įvairiomis formomis.
    """
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)

        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.profilis = request.user.profilis
            recipe.save()

            tags = form.cleaned_data['raktazodziai']
            for tag in tags:
                ReceptoRaktazodis.objects.create(receptas=recipe, raktazodis=tag)

            return redirect('index')

    else:
        form = RecipeForm()

    context = {'form': form}
    return render(request, 'submit_recipe.html', context)


class ReceptasDetail(FormMixin, DetailView):
    """
    ReceptasDetail() yra klasė kuri pagrinde dirba su visais esamais recipe_detail template ir Receptas modeliu.

    Šioje klasėje yra talpinamos funkcijos apdorojančios ir perteikiančios Receptas klasės informaciją receptų template.
    """
    model = Receptas
    context_object_name = 'recipe'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        """
        get_context_data() funkcija pasirūpina visų recepto template funkcionalumu. (recipe detail)

        Pagrinde ši funkcija surenka visą reikalingą informaciją (kontekstą) pavaizdavimui template.
        Be to, ji suteikia formas komentarų, reitingų ir favoritų įkėlimui.
        """
        context = super().get_context_data(**kwargs)

        context['comment_form'] = CommentForm()
        context['rating_form'] = RatingForm()

        current_user = self.request.user

        if current_user.is_authenticated:
            user_profile = current_user.profilis
        else:
            user_profile = None

        context['current_user'] = current_user

        if self.object.profilis:
            context['recipe_user'] = self.object.profilis.profilis
        else:
            context['recipe_user'] = None

        context['comments'] = Komentaras.objects.filter(receptas=self.object).order_by('-data')

        recipe_tags = self.object.raktazodziai_recepto.all()
        if recipe_tags.exists():
            recommended_recipes = Receptas.objects.filter(
                raktazodziai_recepto__raktazodis__in=recipe_tags.values_list('raktazodis', flat=True)).exclude(
                id=self.object.id)[:4]
            context['recommended_recipes'] = recommended_recipes
        else:
            context['recommended_recipes'] = []

        if user_profile:
            user_rating = Reitingas.objects.filter(receptas=self.object, profilis=user_profile).first()

            if user_rating:
                context['user_rating'] = user_rating.reitingas
                context['is_favorite'] = user_rating.favoritas
            else:
                context['user_rating'] = None
                context['is_favorite'] = False
        else:
            context['user_rating'] = None
            context['is_favorite'] = False

        context['rating_form'] = RatingForm(initial={
            'reitingas': context['user_rating'],
            'favoritas': context['is_favorite']
        })

        return context

    def get_template_names(self):
        """
        get_template_names() funkcija gražina tinkamą template pagal recepto parinktą šabloną.
        """
        sablonas = self.object.sablonas

        if sablonas.pavadinimas == 'Paprastas':
            return ['recipe_detail_template_1.html']
        elif sablonas.pavadinimas == 'Horizontalus':
            return ['recipe_detail_template_2.html']
        elif sablonas.pavadinimas == 'Dvi nuotraukos':
            return ['recipe_detail_template_3.html']
        else:
            return ['recipe_detail.html']

    def post(self, request, *args, **kwargs):
        """
        post() funkcija pasirūpina visų vartotojo įkeliamais duomenimis recepto (recipe_detai.html) puslapyje.

        Ši funkcija dirba su komentarų, reitingų ir favoritų įkėlimu ir iškviečia funkcijas kurios skaičiuoja
        reitingų ir favoritų kiekį bei vykdo prestižo taškų skaičiavimus.
        """
        self.object = self.get_object()
        comment_form = self.get_form()
        rating_form = RatingForm(request.POST)

        if 'comment' in request.POST:
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.receptas = self.object
                comment.profilis = request.user.profilis
                comment.save()
                return redirect('Receptas', recipe_id=self.object.id)

        elif 'rating' in request.POST:
            if rating_form.is_valid():
                user_profile = request.user.profilis
                user_rating = Reitingas.objects.filter(receptas=self.object, profilis=user_profile).first()

                if user_rating:
                    user_rating.reitingas = rating_form.cleaned_data['reitingas']
                    user_rating.favoritas = rating_form.cleaned_data['favoritas']
                    user_rating.save()
                else:
                    Reitingas.objects.create(
                        receptas=self.object,
                        profilis=user_profile,
                        reitingas=rating_form.cleaned_data['reitingas'],
                        favoritas=rating_form.cleaned_data['favoritas']
                    )

                self.object.start_counting()

                user_profile.recalculate_prestige(recipe_id=self.object.id)

                return redirect('Receptas', recipe_id=self.object.id)

        return self.render_to_response(self.get_context_data(comment_form=comment_form, rating_form=rating_form))

    def form_valid(self, form):
        """
        form_valid() funkcija tvarko teisingą komentaro įkėlimo bandymą.
        """
        form.instance.receptas = self.object
        form.instance.profilis = self.request.user.profilis
        form.save()

        return redirect('Receptas', recipe_id=self.object.pk)

    def form_invalid(self, form):
        """
        form_invalid() funkcija tvarko neteisingą komentaro įkėlimo bandymą.
        """
        return self.render_to_response(self.get_context_data(form=form))


def view_other_profile(request, username):
    """
    view_other_profile() funkcija pasirūpina visų vartotojų viešo profilio profile_view_other.html template funkcionalumu.

    Pagrinde ši funkcija tiesiog surenka visą reikalingą informaciją (kontekstą) pavaizdavimui template.
    """
    profile = Profilis.objects.get(profilis__username=username)

    favorite_ratings = Reitingas.objects.filter(profilis=profile, favoritas=True)

    favorite_recipes = [rating.receptas for rating in favorite_ratings if rating.receptas is not None]

    uploaded_recipes = Receptas.objects.filter(profilis=profile)

    favorite_recipes = favorite_recipes[:4]

    context = {
        'profile': profile,
        'favorite_recipes': favorite_recipes,
        'uploaded_recipes': uploaded_recipes,
    }

    return render(request, 'profile_view_other.html', context)


@login_required
def mano_receptai(request):
    """
    mano_receptai() funkcija pasirūpina visų vartotojų asmenino mano_receptai.html template funkcionalumu.

    Pagrinde ši funkcija tiesiog surenka visą reikalingą informaciją (kontekstą) pavaizdavimui template.
    """
    user_profile = request.user.profilis

    uploaded_recipes = user_profile.receptai.all()

    favorited_recipes = Receptas.objects.filter(
        reitingai__profilis=user_profile,
        reitingai__favoritas=True
    ).distinct()

    context = {
        'uploaded_recipes': uploaded_recipes,
        'favorited_recipes': favorited_recipes,
    }
    return render(request, 'mano_receptai.html', context)
