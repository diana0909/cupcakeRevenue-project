from django.shortcuts import render
from . import functions

def home(request):
    if request.method == 'POST':
        # Getting data from form
        basic = request.POST['basic']
        delux = request.POST['delux']
        dates = request.POST['dates']

        functions.add_update_db_data(basic, delux, dates, request)
    return render(request, 'home.html', {})

def yearly(request):
    revenue_data = functions.yearly_revenue()

    data_for_charts = [revenue_data['basic_yearly'], revenue_data['delux_yearly'], revenue_data['totaly_yearly'], revenue_data['years']]
    charts = functions.yearly_charts(data_for_charts)

    context = zip(revenue_data['years'], revenue_data['basic_yearly'], revenue_data['delux_yearly'], revenue_data['totaly_yearly'])

    return render(request, 'yearly.html', {'context': context, 'chart': charts['chart_for_basic_and_deluxe'], 'chart_tot' : charts['chart_totaly_earned']})

def monthly(request):
    revenue_data = functions.monthly_revenue()

    data_for_charts = [revenue_data['basic_monthly'], revenue_data['delux_monthly'], revenue_data['totaly_monthly'], revenue_data['years']]
    charts = functions.monthly_charts(data_for_charts)

    return render(request, 'monthly.html', {'years': revenue_data['years'],
                                            'basic_monthly': revenue_data['basic_monthly'],
                                            'deluxe_monthly': revenue_data['delux_monthly'],
                                            'totaly_monthly': revenue_data['totaly_monthly'],
                                            'months': revenue_data['months'],
                                            'charts': charts['charts_basic_and_deluxe'],
                                            'chart_tot': charts['chart_totaly_earned'],
                                            })

def weekly(request):
    revenue_data = functions.weekly_revenue()

    context = zip(revenue_data['weeks'], revenue_data['basic_weekly'], revenue_data['delux_weekly'], revenue_data['totaly_weekly'])

    return render(request, 'weekly.html', {'context': context})

def daily(request):
    revenue_data = functions.daily_revenue()

    context = zip(revenue_data['dates_db'], revenue_data['basic_db'], revenue_data['delux_db'], revenue_data['totaly_db'])

    return render(request, 'daily.html', {'context':context})
