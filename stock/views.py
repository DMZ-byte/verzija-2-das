from django.shortcuts import render, redirect
import pandas as pd
from .models import Stock, StockData
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator
import csv
from django.shortcuts import render
from .utils import calculate_indicators, generate_signals, filter_data_by_period,load_csv
import utils
from .utils import normalize_numeric


# Create your views here.
@cache_page(60 * 15)
def home(request):
    with open(file="media/uploads/mk_stock_data.csv",newline="",encoding="utf-8") as file:
        stock_data = csv.DictReader(file)
        data = [data for data in stock_data]

    paginator = Paginator(data,25)
    page_number = request.GET.get("page")
    page_object = paginator.get_page(page_number)

    return render(request, 'home.html', {'page_object': page_object})


def upload_csv(request):
    if request.method == 'POST':
        file = request.FILES['csv_file']
        Stock.objects.create(file=file)
        return redirect('home')
    return render(request, 'upload.html')


def upload_data(request):
    if request.method == 'POST':
        file = request.FILES['csv_file']
        data = pd.read_csv(file)

        # Assuming data columns match your model fields
        for _, row in data.iterrows():
            last_transaction_price = normalize_numeric(row['Цена на последна трансакција'])
            if last_transaction_price is None:
                continue
            StockData.objects.create(
                company_code=row['Шифра на компанија'],
                date=pd.to_datetime(row['Датум'], format='%d.%m.%Y'),
                last_transaction_price=normalize_numeric(row['Цена на последна трансакција']) ,
                max_price=normalize_numeric(row.get('Мак.', None)) ,
                min_price=normalize_numeric(row.get('Мин.', None)) ,
                average_price=normalize_numeric(row.get('Просечна цена', None)) ,
                trading_volume_best=normalize_numeric(row.get('Промет во БЕСТ во денари', None)) ,
                total_trading_volume=normalize_numeric(row.get('Вкупен промет во денари', None)) ,
            )
        return redirect('home')
    return render(request, 'upload.html')

def data_visualization(request):
    return render(request, 'data_visualization.html')




def analyze_stock(request):
    data = pd.DataFrame(list(StockData.objects.all().values()))
    if not data.empty:
        data = calculate_indicators(data)
        data = generate_signals(data)
    return render(request, 'data_analysis.html', {'data': data.to_dict('records')})

csv_file = "media/uploads/mk_stock_data.csv"
def Stock_view(request,period,company):
    data = load_csv(csv_file)
    filtered_data = filter_data_by_period(data,period,company)
    context = {
        "company":company,
        "date":period,
        "stocks":filtered_data
    }
    return render(request,'stock_view.html',context)

