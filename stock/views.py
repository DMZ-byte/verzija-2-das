from django.http import HttpResponse
from django.shortcuts import render, redirect
import pandas as pd
from .models import Stock, StockData
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator
import csv
from django.shortcuts import render
from .utils import calculate_indicators, determine_signals, filter_data_by_period, load_csv
from .utils import normalize_numeric

companies = ['ADIN', 'ALK', 'ALKB', 'AMBR', 'AMEH', 'APTK', 'ATPP', 'AUMK', 'BANA', 'BGOR', 'BIKF', 'BIM', 'BLTU',
             'CBNG', 'CDHV', 'CEVI', 'CKB', 'CKBKO', 'DEBA', 'DIMI', 'EDST', 'ELMA', 'ELNC', 'ENER', 'ENSA', 'EUHA',
             'EUMK', 'EVRO', 'FAKM', 'FERS', 'FKTL', 'FROT', 'FUBT', 'GALE', 'GDKM', 'GECK', 'GECT', 'GIMS', 'GRDN',
             'GRNT', 'GRSN', 'GRZD', 'GTC', 'GTRG', 'IJUG', 'INB', 'INDI', 'INEK', 'INHO', 'INOV', 'INPR', 'INTP', 'JAKO',
             'JULI', 'JUSK', 'KARO', 'KDFO', 'KJUBI', 'KKFI', 'KKST', 'KLST', 'KMB', 'KMPR', 'KOMU', 'KONF', 'KONZ', 'KORZ',
             'KPSS', 'KULT', 'KVAS', 'LAJO', 'LHND', 'LOTO', 'LOZP', 'MAGP', 'MAKP', 'MAKS', 'MB', 'MERM', 'MKSD', 'MLKR', 'MODA',
             'MPOL', 'MPT', 'MPTE', 'MTUR', 'MZHE', 'MZPU', 'NEME', 'NOSK', 'OBPP', 'OILK', 'OKTA', 'OMOS', 'OPFO', 'OPTK', 'ORAN',
             'OSPO', 'OTEK', 'PELK', 'PGGV', 'PKB', 'POPK', 'PPIV', 'PROD', 'PROT', 'PTRS', 'RADE', 'REPL', 'RIMI', 'RINS', 'RZEK',
             'RZIT', 'RZIZ', 'RZLE', 'RZLV', 'RZTK', 'RZUG', 'RZUS', 'SBT', 'SDOM', 'SIL', 'SKON', 'SKP', 'SLAV', 'SNBT', 'SNBTO',
             'SOLN', 'SPAZ', 'SPAZP', 'SPOL', 'SSPR', 'STB', 'STBP', 'STIL', 'STOK', 'TAJM', 'TASK', 'TBKO', 'TEAL', 'TEHN', 'TEL',
             'TETE', 'TIGA', 'TIKV', 'TKPR', 'TKVS', 'TNB', 'TRDB', 'TRPS', 'TRUB', 'TSMP', 'TSZS', 'TTK', 'UNI', 'USJE', 'VARG', 'VFPM',
             'VITA', 'VROS', 'VSC', 'VTKS', 'ZAS', 'ZILU', 'ZILUP', 'ZIMS', 'ZKAR', 'ZPKO', 'ZPOG', 'ZSIL', 'ZUAS']
#
@cache_page(60 * 15)
# def home(request):
#   with open(file="media/uploads/mk_stock_data.csv",newline="",encoding="utf-8") as file:
#       stock_data = csv.DictReader(file)
#       data = [data for data in stock_data]

#   paginator = Paginator(data,25)
#   page_number = request.GET.get("page")
#  page_object = paginator.get_page(page_number)

#   return render(request, 'home.html', {'page_object': page_object})

def home_page(request):
    if StockData.objects.exists():
        print("Exists")

        data = StockData.objects.all()
        #latest_file = Stock.objects.last().file.path


        paginator = Paginator(data, 25)
        page_number = request.GET.get("page")
        page_object = paginator.get_page(page_number)
    else:
        page_object = "<p>No data uploaded</p>"
    return render(request, 'home.html', {'page_obj': page_object})


def upload_csv(request):
    if request.method == 'POST':
        file = request.FILES['csv_file']
        Stock.objects.create(file=file)
        return redirect('')
    return render(request, 'upload.html')


def upload_data(request):
    # View for upload page
    if request.method == 'POST':
        file = request.FILES['csv_file']
        data = pd.read_csv(file)
        Stock.objects.create(file=file)
        # Assuming data columns match your model fields
        for _, row in data.iterrows():
            last_transaction_price = normalize_numeric(row['Цена на последна трансакција'])
            if last_transaction_price is None:
                continue
            StockData.objects.create(
                company_code=row['Шифра на компанија'],
                date=pd.to_datetime(row['Датум'], format='%d.%m.%Y'),
                last_transaction_price=normalize_numeric(row['Цена на последна трансакција']),
                max_price=normalize_numeric(row.get('Мак.', None)),
                min_price=normalize_numeric(row.get('Мин.', None)),
                average_price=normalize_numeric(row.get('Просечна цена', None)),
                trading_volume_best=normalize_numeric(row.get('Промет во БЕСТ во денари', None)),
                total_trading_volume=normalize_numeric(row.get('Вкупен промет во денари', None)),
            )
        return render(request, 'home.html')
    return render(request, 'upload.html')


def data_visualization(request):
    return render(request, 'data_visualization.html')


def analyze_stock(request):
    # View for stock analysis page
    selected_company = request.GET.get('company')
    selected_timeframe = request.GET.get("timeframe", "daily")
    resample_map = {
        "daily": "D",
        "weekly": "W",
        "monthly": "M"
    }
    #StockData.objects.all().values()
    if selected_company is None:
        selected_company = "ADIN"
    data = pd.DataFrame(list(StockData.objects.filter(company_code=selected_company).values()))
    numeric_columns = ['last_transaction_price', 'max_price', 'min_price', 'average_price', 'trading_volume_best',
                       'total_trading_volume']
    print(data.columns)
    print(data.head())
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors='coerce')

    # Drop rows with any NaN values
    data = data.dropna(subset=numeric_columns)
    data = data.fillna(0)

    if not data.empty:
        data['date'] = pd.to_datetime(data['date'])
        data.set_index('date',inplace=True)
        #uses selected timeframe
        print(data.head())  # Debug: Inspect the data
        print(data.dtypes)  # Debug: Check column types

        try:
            # Select only numeric columns for resampling
            numeric_data = data.select_dtypes(include=['number'])
            resample = numeric_data.resample(resample_map[selected_timeframe]).mean()
        except Exception as e:
            print(f"Error during resampling: {e}")
            return HttpResponse(f"An error occurred: {e}", status=500)
        resample = calculate_indicators(resample)
        resample = determine_signals(resample)

        resample.reset_index(inplace=True)
    else:
        resample = pd.DataFrame()

    return render(request,
                  'data_analysis.html',
                  {"data": resample.to_dict('records'),
                   "selected_timeframe": selected_timeframe,
                   "companies": companies,
                   "selected_company": selected_company
                   }

                  )


csv_file = "media/uploads/mk_stock_data.csv"


def Stock_view(request, period, company):
    data = load_csv(csv_file)
    filtered_data = filter_data_by_period(data, period, company)
    context = {
        "company": company,
        "date": period,
        "stocks": filtered_data
    }
    return render(request, 'stock_view.html', context)
