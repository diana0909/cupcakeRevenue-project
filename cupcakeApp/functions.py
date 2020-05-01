from django.shortcuts import render, redirect
from .models import Cupcakes
from django.utils import timezone
from datetime import datetime, date, timedelta
from django.core.exceptions import ObjectDoesNotExist
from sorted_months_weekdays import Month_Sorted_Month, Weekday_Sorted_Week

import json
import operator



def sum_data_year(data, y):
    data = [d[0] for d in data if d[1].year == y]
    return sum(data)

def sum_data_month(data, m, y):
    data = [d[0] for d in data if month_string_to_number(d[1].strftime("%b")) == month_string_to_number(m) and d[1].year == y]
    return sum(data)

def month_string_to_number(string):
    m = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr':4,
         'may':5,
         'jun':6,
         'jul':7,
         'aug':8,
         'sep':9,
         'oct':10,
         'nov':11,
         'dec':12
        }
    s = string.strip()[:3].lower()
    try:
        out = m[s]
        return out
    except:
        raise ValueError('Not a month')

def sum_data_week(datas, w, y):
    data = []
    for d in datas:
        if d[0] == y:
            if d[1] == w:
                data.append(d[3])
    return sum(data)

def get_week_details(iso_week):
    week_pair = [f'{w[0]}-W{w[1]}' for w in iso_week]
    return week_pair

def update_data_to_db(basic, delux, dates):
    cupcake = Cupcakes.objects.get(dates=dates)
    cupcake.basic = basic
    cupcake.delux = delux
    cupcake.save()

def add_data_to_db(basic, delux, dates):
    cupcake = Cupcakes()
    cupcake.setCupcake(basic, delux, dates)
    cupcake.save()

def add_update_db_data(basic, delux, dates, request):
    if dates:
        if basic == '':
            basic = 0
        if delux == '':
            delux = 0
        try:
            update_data_to_db(basic, delux, dates)
            return redirect('home')
        except ObjectDoesNotExist:
            add_data_to_db(basic, delux, dates)
            return redirect('home')
    else:
        return render(request, 'home.html', {'error': 'You must enter a date!'})

def get_list_of_elements_from_db(db_data, name):
    return [data[0] for data in db_data.all().values_list(name)]

def data_for_revenue():
    cupcakes = Cupcakes.objects
    basic_db = get_list_of_elements_from_db(cupcakes, 'basic')
    delux_db = get_list_of_elements_from_db(cupcakes, 'delux')
    totaly_db = [ 5*b + 6*d for (b,d) in zip(basic_db, delux_db)]
    dates_db = get_list_of_elements_from_db(cupcakes, 'dates')

    return {'basic_db': basic_db,
            'delux_db': delux_db,
            'totaly_db': totaly_db,
            'dates_db': dates_db}

def yearly_charts(data_for_charts):
    basic_data_for_chart = {
        'name': 'Basic cupcakes',
        'data': data_for_charts[0],
    }
    deluxe_data_for_chart= {
        'name': 'Deluxe cupcakes',
        'data': data_for_charts[1],
    }
    totaly_earned_data_for_chart = [{'name': year, 'y': t} for (year, t) in zip(data_for_charts[3], data_for_charts[2])]

    chart_data_for_basic_and_deluxe = {
        'chart': {'type': 'column'},
        'title': {'text': 'Basic and Deluxe Cupcakes sold'},
        'xAxis': {'title': {'text': 'Years'}, 'categories': data_for_charts[3]},
        'series': [basic_data_for_chart, deluxe_data_for_chart],
        'yAxis' : {'title': {'text': 'Number of cupcakes sold'}}
        }


    chart_data_totaly_earned = {
        'chart': {'type': 'pie'},
        'title': {'text': 'Yearly earnings'},
        'plotOptions': {'pie': {'allowPointSelect': True, 'cursor': 'pointer', 'dataLabels': {'enabled': False}, 'showInLegend': True}},
        'series': [{ 'name': '$', 'data': totaly_earned_data_for_chart}]
        }
    chart_for_basic_and_deluxe = json.dumps(chart_data_for_basic_and_deluxe)
    chart_totaly_earned = json.dumps(chart_data_totaly_earned)

    return {'chart_for_basic_and_deluxe': chart_for_basic_and_deluxe,
            'chart_totaly_earned': chart_totaly_earned}

def yearly_revenue():
    data = data_for_revenue()
    basic_db = data['basic_db']
    delux_db = data['delux_db']
    totaly_db = data['totaly_db']
    dates_db = data['dates_db']

    years = list({y.year for y in dates_db})
    basic_yearly = []
    delux_yearly = []
    totaly_yearly = []

    for y in years:
        basic = zip(basic_db, dates_db)
        delux =zip (delux_db, dates_db)
        totaly =zip (totaly_db, dates_db)
        basic_yearly.append(sum_data_year(basic, y))
        delux_yearly.append(sum_data_year(delux, y))
        totaly_yearly.append(sum_data_year(totaly, y))

    return {'years': years,
            'basic_yearly': basic_yearly,
            'delux_yearly': delux_yearly,
            'totaly_yearly': totaly_yearly}

def monthly_revenue():
    data = data_for_revenue()
    basic_db = data['basic_db']
    delux_db = data['delux_db']
    totaly_db = data['totaly_db']
    dates_db = data['dates_db']

    years = list({y.year for y in dates_db})
    months = Month_Sorted_Month(list({m.strftime("%B") for m in dates_db}))
    basic_monthly= []
    delux_monthly = []
    totaly_monthly = []

    for y in years:
        for m in months:
            basic = zip(basic_db, dates_db)
            delux =zip (delux_db, dates_db)
            totaly =zip (totaly_db, dates_db)
            basic_monthly.append(sum_data_month(basic, m, y))
            delux_monthly.append(sum_data_month(delux, m, y))
            totaly_monthly.append(sum_data_month(totaly, m, y))
    basic_monthly = [basic_monthly[i:i+12] for i in range(0, len(basic_monthly), 12)]
    delux_monthly = [delux_monthly[i:i+12] for i in range(0, len(delux_monthly), 12)]
    totaly_monthly = [totaly_monthly[i:i+12] for i in range(0, len(totaly_monthly), 12)]

    return {'years': years,
            'months': months,
            'basic_monthly': basic_monthly,
            'delux_monthly': delux_monthly,
            'totaly_monthly': totaly_monthly}

def monthly_charts(data_for_charts):
    charts_data_for_basic_and_deluxe = []
    num_of_charts = len(data_for_charts[3])

    for i in range(num_of_charts):
        basic_cht = {
            'name': 'Basic cupcakes',
            'data': data_for_charts[0][i],
        }
        deluxe_cht = {
            'name': 'Deluxe cupcakes',
            'data': data_for_charts[1][i],
        }

        charts_data_for_basic_and_deluxe.append({
            'chart': {'type': 'column'},
            'title': {'text': f'Monthly Cupcake revenue for year {data_for_charts[3][i]}.'},
            'xAxis': {'categories': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 'crosshair': True},
            'yAxis': {'min': 0, 'title': {'text': 'Number of sold cupcakes'}},
            'plotOptions': {'column': {'pointPadding': 0.2, 'borderWidth': 0}},
            'series':[basic_cht, deluxe_cht],
            })

    chart_data_for_totaly_earned = {
        'chart': {'type': 'column'},
        'title': {'text': f'Earnings'},
        'xAxis': {'categories': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 'crosshair': True},
        'yAxis': {'min': 0, 'title': {'text': 'Earned'}},
        'plotOptions': {'column': {'pointPadding': 0.2, 'borderWidth': 0}},
        'series': [{'name': data_for_charts[3][i], 'data': data_for_charts[2][i]} for i in range(num_of_charts)]
        }

    charts_basic_and_deluxe = [json.dumps(charts_data_for_basic_and_deluxe[i]) for i in range(num_of_charts)]
    chart_totaly_earned = json.dumps(chart_data_for_totaly_earned)

    return {'charts_basic_and_deluxe': charts_basic_and_deluxe,
            'chart_totaly_earned': chart_totaly_earned}

def sorted_week_numbers(years, year_week_day_format_data):
    #week[] is list of lists that contains week numbers for each year
    week = []
    for y in years:
        w = list({x[1] for x in year_week_day_format_data if x[0] == y})
        week.append(sorted(w))

    return week

def get_date_range_from_week(year,week):

    firstdayofweek = datetime.strptime(f'{year}-W{int(week )- 1}-1', "%Y-W%W-%w").date()
    lastdayofweek = firstdayofweek + timedelta(days=6.9)
    return f'{firstdayofweek.strftime("%d %b %Y")} - {lastdayofweek.strftime("%d %b %Y")}'

def get_week_dates_list(years, week):
    week_dates = []

    for i in range(len(years)):
        for w in week[i]:
            week_dates.append(get_date_range_from_week(years[i], w))
    return week_dates

def reverse_list(l):
    return l[::-1]

def combine_data_for_daily_revenue(data, year_week_day_format_data):
    combined_data = []
    for i in range(len(data)):
        combined_data.append(year_week_day_format_data[i] + (data[i],))

    return combined_data

def calculate_weekly_revenue(weekly_revenue_data, years, week, year_week_day_format_data):
    basic_weekly = []
    delux_weekly = []
    totaly_weekly = []

    combined_data_basic = combine_data_for_daily_revenue(weekly_revenue_data[0], year_week_day_format_data)
    combined_data_delux = combine_data_for_daily_revenue(weekly_revenue_data[1], year_week_day_format_data)
    combined_data_totaly = combine_data_for_daily_revenue(weekly_revenue_data[2], year_week_day_format_data)
    for i in range(len(years)):
        for w in week[i]:
            basic_weekly.append(sum_data_week(combined_data_basic, w, years[i]))
            delux_weekly.append(sum_data_week(combined_data_delux, w, years[i]))
            totaly_weekly.append(sum_data_week(combined_data_totaly, w, years[i]))

    return {'basic_weekly': basic_weekly,
            'delux_weekly': delux_weekly,
            'totaly_weekly': totaly_weekly}

def weekly_revenue():
    data = data_for_revenue()
    basic_db = data['basic_db']
    delux_db = data['delux_db']
    totaly_db = data['totaly_db']
    dates_db = data['dates_db']
    year_week_day_format_data = [d.isocalendar() for d in dates_db]

    years = list({y[0] for y in year_week_day_format_data})
    week = sorted_week_numbers(years, year_week_day_format_data)

    weekly_revenue_data = [basic_db, delux_db, totaly_db]

    revenue_data = calculate_weekly_revenue(weekly_revenue_data, years, week, year_week_day_format_data)

    week_dates = get_week_dates_list(years, week)

    return {'weeks': reverse_list(week_dates),
            'basic_weekly': reverse_list(revenue_data['basic_weekly']),
            'delux_weekly': reverse_list(revenue_data['delux_weekly']),
            'totaly_weekly': reverse_list(revenue_data['totaly_weekly'])}

def daily_data_list(daily_data, index):
    return [d[index] for d in daily_data]

def daily_revenue():
    data = data_for_revenue()
    basic_db = data['basic_db']
    delux_db = data['delux_db']
    totaly_db = data['totaly_db']
    dates_db = data['dates_db']

    daily_data = ((day, b, d, t) for (day, b, d, t) in zip(dates_db, basic_db, delux_db, totaly_db))
    daily_data = sorted(daily_data, key=operator.itemgetter(0))

    dates_db = reverse_list(daily_data_list(daily_data, 0))
    basic_db = reverse_list(daily_data_list(daily_data, 1))
    delux_db = reverse_list(daily_data_list(daily_data, 2))
    totaly_db = reverse_list(daily_data_list(daily_data, 3))

    return {'dates_db': dates_db,
            'basic_db': basic_db,
            'delux_db': delux_db,
            'totaly_db': totaly_db}
