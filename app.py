import pandas as pd
import numpy as np
from distutils.util import strtobool
from flask import Flask, jsonify, request


def _header_cleanup(df):
    df.columns = df.iloc[0]

    return df[1:]


def _get_state_annual_generation(state, df):
    return df[df['PSTATABB'] == state]['PLNGENAN'].sum()


def _get_state_dataframe(state, df):
    return df[df['PSTATABB'] == state] if state else df


def _get_top_n_plants_by_annual_generation_dataframe(df, n):
    df = df.sort_values(by=['PLNGENAN'], ascending=False)

    return df[:n] if n > 0 else df


def _get_raw_data_results_as_dicts(df, n):
    return df.apply(lambda x: x.to_dict(), axis=1).to_list() if n > 0 else []


def _build_results_from_raw_data(raw_data_results, raw_data, state_annual_generation):
    results = []

    for raw_data_result in raw_data_results:
        result = {
            'state': raw_data_result['PSTATABB'],
            'plant_name': raw_data_result['PNAME'],
            'oris_code': raw_data_result['ORISPL'],
            'latitude': raw_data_result['LAT'],
            'longitude': raw_data_result['LON'],
            'plant_annual_generation': raw_data_result['PLNGENAN'],
            'state_annual_generation': state_annual_generation[raw_data_result['PSTATABB']]
        }

        result['plant_annual_generation_as_percentage_of_state'] = round(
            float(result['plant_annual_generation']) / float(result['state_annual_generation']), 2)

        if raw_data:
            result['raw_data'] = raw_data_result

        results.append(result)

    return results


def _load_data(filename):
    egrid2018_data_plants = pd.read_excel(filename, sheet_name = None)['PLNT18']
    egrid2018_data_plants = _header_cleanup(egrid2018_data_plants)

    states = set(egrid2018_data_plants['PSTATABB'].to_list())
    state_annual_generation = {state: _get_state_annual_generation(state, egrid2018_data_plants) for state in states}

    return egrid2018_data_plants, state_annual_generation


egrid2018_data_plants, state_annual_generation = _load_data('egrid2018_data_v2.xlsx')


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


@app.route('/', methods=['GET'])
def index():
    return 'Read README.md'


@app.route('/top_plants_by_annual_generation', methods=['GET'])
def top_plants_by_annual_generation():
    n = int(request.args.get('n')) if 'n' in request.args else 0
    state = request.args.get('state').strip("\'\"") if 'state' in request.args else None
    raw_data = bool(strtobool(request.args.get('raw_data'))) if 'raw_data' in request.args else False

    df = _get_top_n_plants_by_annual_generation_dataframe(
        _get_state_dataframe(state, egrid2018_data_plants), n)
    df = df.replace(np.nan, "", regex=True)
    raw_data_results = _get_raw_data_results_as_dicts(df, n)

    return jsonify({
        "data": _build_results_from_raw_data(raw_data_results, raw_data, state_annual_generation)
    })
