from flask import Flask, render_template, jsonify, request, Response
from flask.ext.sqlalchemy import SQLAlchemy
from decimal import Decimal
from collections import OrderedDict
import pandas_datareader.data as web
import os
import config
import numpy
import pandas
import datetime
import json
import math

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

import models

@app.route('/')
def index():
    symbols = models.Symbol.query.all()
    return render_template("index.html", symbols=symbols)

@app.route('/all_betas')
def all_betas():
    symbols = models.Symbol.query.all()
    return render_template("all_betas.html", symbols=symbols)

@app.route('/symbol_list')
def symbol_list():
    symbols = models.Symbol.query.all()
    return render_template("symbol_list.html", symbols=symbols)

def format_date_for_yahoo(date):
    return date.strftime("%Y-%m-%d")

def generate_date_range(start_date, end_date):
    day_count = (end_date - start_date).days + 1
    return [start_date + datetime.timedelta(n) for n in range(day_count)]

def data_exists(symbol, start_date, end_date):
    date_range = generate_date_range(start_date, end_date)
    data = []
    for day in [date for date in date_range]:
        d = models.HistoricValue.query\
                                   .filter_by(symbol_id=symbol.id)\
                                   .filter_by(date=day).first()
        if d is None:
            if (day.weekday() > 5):
                #ignore missing weekends from the cache
                continue
            else:
                return False
        else:
            data.append(d)
    return data
        

def maybe_fetch_ticker_data(symbol, start_date, end_date):
    maybe_data = data_exists(symbol, start_date, end_date)
    if maybe_data is not False:
        return maybe_data
    else:
        print "Complete data for %s not found in db for %s - %s. Fetching from Yahoo" % (symbol.name,
                                                                                          start_date,
                                                                                          end_date)
        data = web.DataReader(symbol.name, 'yahoo', start_date, end_date)
        all_historic_data = []
        date_and_data_dict = {}
        for i_d in generate_date_range(start_date, end_date):
            try:
                data_point = data.ix[format_date_for_yahoo(i_d)]
            except KeyError:
                data_point = None
            if data_point is not None:
                date_and_data_dict[i_d] = data_point
        for historic_date, d in date_and_data_dict.iteritems():
            historic = models.HistoricValue.query\
                                            .filter_by(symbol_id=symbol.id)\
                                            .filter_by(date=historic_date)\
                                            .first()
            if historic is None:
                historic = models.HistoricValue()
                historic.symbol = symbol
                historic.date = historic_date
                historic.closing_price = Decimal(d['Close'])
                db.session.add(historic)
                db.session.commit()
            all_historic_data.append(historic)
        return all_historic_data

def fetch_ticker_data(symbol, start_date, end_date):
    return maybe_fetch_ticker_data(symbol, start_date, end_date)

def transform_ticker_data_to_close_list(datalist):
    close_list = []
    for d in datalist:
       close_list.append({'date': d.date,
                          'closing_price': float(d.closing_price)})
    return close_list

def generate_dataframe(dictionary, index='date'):
    df = pandas.DataFrame(dictionary)
    df.index = df[index]
    del df[index]
    return df

def compute_returns(df):
    df[['symbol_returns', 'comparator_returns']] = df[['symbol_close','comparator_close']] /\
                                                   df[['symbol_close','comparator_close']].shift(1) -1
    return df

def compute_beta(symbol_close_list, comparator_close_list):
    symbol_df = generate_dataframe(symbol_close_list)
    comparator_df = generate_dataframe(comparator_close_list)
    main_dataframe = pandas.DataFrame({'symbol_close': symbol_df['closing_price'],
                                       'comparator_close': comparator_df['closing_price']},
                                      index=symbol_df.index)
    
    main_dataframe = compute_returns(main_dataframe)
    main_dataframe = main_dataframe.dropna()

    covariance = numpy.cov(main_dataframe['symbol_returns'].astype(float), main_dataframe['comparator_returns'].astype(float))

    beta = covariance[0,1]/covariance[1,1]
    
    return beta

def sort_close_list(close_list):
    return sorted(close_list, key=lambda x: x['date'])

def compute_betas(symbol_close_list, comparator_close_list):
    scl = sort_close_list(symbol_close_list)
    ccl = sort_close_list(comparator_close_list)
    s_acc = []
    c_acc = []
    beta_acc = OrderedDict()
    for s, c in zip(scl, ccl):
        s_acc.append(s)
        c_acc.append(c)
        beta_acc[s['date']] = compute_beta(s_acc, c_acc)
    return beta_acc

def parse_arg_date(maybe_date, bias=0):
    #allow a bias so we have more data to compute a beta with on the first day
    if maybe_date is None:
        return None
    return datetime.datetime.strptime(maybe_date, "%Y-%m-%d").date() - datetime.timedelta(bias)

def transform_response_date(date):
    return date.strftime("%m/%d/%Y")
    
@app.route('/api/v1/fetch-new-data', methods=['GET'])
def get_new_data():
    # Endpoint takes optional args for fetching just one symbol and/or alternate comparator
    symbol_id_string = request.args.get("symbol_id")
    if symbol_id_string is not None:
        symbols = [models.Symbol.query.get(int(symbol_id_string))]
    else:
        symbols = models.Symbol.query.all()
    comparator_id_string = request.args.get("comparator_id")
    if comparator_id_string is not None:
        comparator = models.Symbol.query.get(int(comparator_id_string))
    else:
        comparator = models.Symbol.query.filter_by(name="^GSPC").first()

    start_date = parse_arg_date(request.args.get("start_date"), 2)
    end_date = parse_arg_date(request.args.get("end_date"))
    
    comparator_tick_data = fetch_ticker_data(comparator, start_date, end_date)
    transformed_comparator_data = transform_ticker_data_to_close_list(comparator_tick_data)
    betas_to_return = OrderedDict()
    for s in symbols:
        if s.id == comparator.id:
            # handle the case where we query all symbols. Don't need to re-query for the baseline
            continue
        else:
            symbol_tick_data = fetch_ticker_data(s, start_date, end_date)
        symbol_betas = compute_betas(transformed_comparator_data,
                                     transform_ticker_data_to_close_list(symbol_tick_data))

        betas = OrderedDict()
        for k, v in symbol_betas.iteritems():
            betas[transform_response_date(k)] = v if not(math.isnan(v)) else None # clean up NaNs
        betas_to_return[s.name] = betas
            
    resp = Response(json.dumps({'status': 'OK',
                                'data': betas_to_return}),
                    mimetype='application/json')
    
    return resp

if __name__ == '__main__':
    app.run(debug=True)
