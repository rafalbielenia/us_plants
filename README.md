Running the app:
=============
- `$ virtualenv venv && source venv/bin/activate`
- `$ pip install -r requirements.txt`
- `$ export FLASK_APP=app.py`
- `$ python -m flask run`


Usage example & API documentation:
=============
- Available endpoints: `/` and `/top_plants_by_annual_generation`;
- Type in your browser:
`http://localhost:5000/top_plants_by_annual_generation?n=5&state='CA'&raw_data=True`;
- You can manipulate `n` (int), `state` (string) and `raw_data` (boolean) arguments;
- Allowed method: `GET`;
- First load just after the server start might be a bit slower as the data needs to be loaded.
