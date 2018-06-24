from django.http import JsonResponse
from django.urls import reverse_lazy

from django.views.generic import TemplateView, FormView
from django.views.generic.base import View
from operator import itemgetter

from infection_tracker.forms import AddNewCityForm
from infection_tracker.models import City, Round, InfectionCard


class TableView(TemplateView):
    template_name = 'infection_tracker/overview.html'

    def get_context_data(self, **kwargs):
        total_cards = InfectionCard.objects.all().count()
        current_round = Round.objects.all().order_by('-round_number').first()

        data = []

        for city in City.objects.all():
            total_city_cards = InfectionCard.objects.filter(city=city).count()
            city_data = {'name': city.name, 'rounds': [], 'total': total_city_cards}
            for r in Round.objects.all():
                city_data['rounds'].append(r.cards.filter(city=city).count())

            if current_round.round_number == 1:
                drawn_cards = current_round.cards.filter(city=city).count()
                chance = ((total_city_cards - drawn_cards) / (
                            total_cards - current_round.cards.all().count())) * 100
                city_data['chance'] = chance
            else:
                previous_round = Round.objects.get(round_number=current_round.round_number - 1)
                previous_drawn_cards_count = previous_round.cards.all().count()
                if current_round.cards.all().count() < previous_drawn_cards_count:
                    previous_round_city_drawn_count = previous_round.cards.filter(city=city).count()
                    if previous_round_city_drawn_count > 0:
                        remaining_city_cards = previous_round_city_drawn_count - current_round.cards.filter(
                            city=city).count()
                        remaining_total_cards = previous_drawn_cards_count - current_round.cards.all().count()
                        chance = (remaining_city_cards / remaining_total_cards) * 100
                        city_data['chance'] = chance
                    else:
                        city_data['chance'] = 0
                else:
                    drawn_cards = current_round.cards.filter(city=city).count()
                    chance = ((InfectionCard.objects.filter(city=city).count() - drawn_cards) / (
                            total_cards - current_round.cards.all().count())) * 100
                    city_data['chance'] = chance

            data.append(city_data)

        sorted_data = sorted(data, key=itemgetter('name'))

        return super(TableView, self).get_context_data(
            data=sorted_data,
            rounds=Round.objects.all(),
            **kwargs
        )


class InfectCity(View):

    def post(self, request, *args, **kwargs):
        city_name = request.POST.get('city')
        current_round = Round.objects.all().order_by('-round_number').first()
        total_amount_for_city = InfectionCard.objects.filter(city__name=city_name).count()
        amount_for_city_in_current_round = current_round.cards.filter(city__name=city_name).count()

        if amount_for_city_in_current_round < total_amount_for_city:
            card = InfectionCard.objects.exclude(epidemic_rounds__cards__city__name=city_name,
                                             epidemic_rounds=current_round).filter(city__name=city_name).first()
            current_round.cards.add(card)
            return JsonResponse({'message': 'success'})
        else:
            return JsonResponse({'message': 'not possible'})


class NewRound(View):

    def post(self, request, *args, **kwargs):
        current_round = Round.objects.all().order_by('-round_number').first()
        Round.objects.create(round_number=current_round.round_number+1)
        return JsonResponse({'message': 'success'})


class AddCityView(FormView):
    template_name = 'infection_tracker/add_city.html'
    form_class = AddNewCityForm
    success_url = reverse_lazy('infection_tracker:list')

    def form_valid(self, form):
        form.save()
        return super(AddCityView, self).form_valid(form)