from django.shortcuts import render, redirect
from gym.forms import *
from django.contrib import messages
import requests

def home(request):
    lat = request.GET.get('lat') 
    lng = request.GET.get('lng')   
    
    retrieved = request.GET.get("retrieved")
    
    if retrieved == "true":
        locationRetrieved = True
    else:  
        locationRetrieved = False
        
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?' 
    params = {
        'location': f'{lat},{lng}',   
        'radius': 5000,   
        'type': 'gym',    
        'key': 'AIzaSyBS2ButcwA-Kr8IPPJ0ejaO7EdyyblTrnU',   
        'img': True,
        'fields': 'name,opening_hours,opening_hours/weekday_text,opening_hours/open_now', 
    }
    
    response = requests.get(url, params=params)
    gyms = response.json()['results']
    
    for gym in gyms:
        gym['name'] = gym['name'] 
        gym['address'] = gym['vicinity']
        gym['description'] = generate_description(gym)
        gym['rating_stars'] = generate_rating_stars(gym.get('rating'))  # Add this line for star icons
        gym['opening_hours'] = gym.get('opening_hours')
        gym['opening_status'] = 'Open' if gym.get('opening_hours/open_now') else 'Closed'
        
        if 'photos' in gym:
            gym['img'] = gym['photos'][0]['photo_reference']
        else:
            gym['img'] = None
            
    context = {
        'gyms': gyms,
        "locationRetrieved": locationRetrieved, 
    }   
    return render(request, 'gyms/find-gym2.html', context)

def finder(request):
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')

    retrieved = request.GET.get("retrieved")

    if retrieved == "true":
        locationRetrieved = True
    else:
        locationRetrieved = False

    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
    params = {
        'location': f'{lat},{lng}',
        'radius': 5000,
        'type': 'gym',
        'key': 'AIzaSyBS2ButcwA-Kr8IPPJ0ejaO7EdyyblTrnU',
        'img': True
    }

    response = requests.get(url, params=params)
    gyms = response.json()['results']

    # Sort gyms based on their ratings (if ratings exist)
    gyms = sorted(gyms, key=lambda gym: gym.get('rating', 0), reverse=True)

    # Keep only the top 5 gyms
    top_5_gyms = gyms[:5]

    for gym in top_5_gyms:
        gym['name'] = gym['name']
        gym['address'] = gym['vicinity']
        gym['description'] = generate_description(gym)
        gym['rating_stars'] = generate_rating_stars(gym.get('rating'))  # Add this line for star icons

        if 'photos' in gym:
            gym['img'] = gym['photos'][0]['photo_reference']
        else:
            gym['img'] = None

    context = {
        'gyms': top_5_gyms,
        "locationRetrieved": locationRetrieved,
    }
    return render(request, 'gyms/index.html', context)

def generate_description(gym):
    description = ""
    
    if "types" in gym and "gym" in gym["types"]:
        description += "A fitness facility "
        
    if "rating" in gym:
        description += f"with a {gym['rating']} star rating. "
        
    if "price_level" in gym:
        description += f"It has a {gym['price_level']} price level. "
        
    if "opening_hours" in gym:
        description += "It is currently open. "
        
    if "reviews" in gym and len(gym["reviews"]) > 0:
        description += f"Based on {len(gym['reviews'])} reviews. "
        
    return description.strip()

def generate_rating_stars(rating):
    if rating is None:
        return "No ratings yet."

    full_stars = int(rating)
    half_star = 1 if (rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    stars_html = ""
    for _ in range(full_stars):
        stars_html += '<small class="fa fa-star text-primary"></small> '
    if half_star:
        stars_html += '<small class="fa fa-star-half text-primary"></small> '
    for _ in range(empty_stars):
        stars_html += '<small class="fa fa-star-o text-primary"></small> '

    return stars_html

