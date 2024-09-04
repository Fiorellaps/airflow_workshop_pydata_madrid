
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import json

# Create a FastAPI instance
app = FastAPI()

# Load data from JSON file
#with open('data.json') as f:
#    data = json.load(f)['data']

# Convert the JSON data to a DataFrame

df = pd.read_json('data.json', orient ='split', compression = 'infer')
#print(df.head())
# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Home route
@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    countries = df['country'].unique()
    sports = df['sport'].unique()
    categories = df['category'].unique()
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "countries": countries, 
        "sports": sports, 
        "categories": categories
    })

@app.post("/filter", response_class=HTMLResponse)
async def filter_events(
    request: Request,
    country: str = Form(...),
    sport: str = Form(...),
    category: str = Form(...)
):
    # Filter DataFrame
    filtered_df = df[(df['country'] == country) & 
                     (df['sport'] == sport) & 
                     (df['category'] == category)]
    
    # Convert filtered events to a list of dictionaries
    events = filtered_df['events'].values[0] if not filtered_df.empty else []
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "countries": df['country'].unique(),
        "sports": df['sport'].unique(),
        "categories": df['category'].unique(),
        "filtered_events": events
    })
