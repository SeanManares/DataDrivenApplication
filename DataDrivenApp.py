# -*- coding: utf-8 -*-
"""
Created on Thu Jan  8 09:51:54 2026

@author: steph
"""

import tkinter as tk
import requests
from PIL import Image, ImageTk
from io import BytesIO  #for converting image bytes to image object

db_url = "https://www.themealdb.com/api/json/v1/1/"

bg_color = "black"        
frame_color = "#1e1e1e"
text_color = "#ffffff" #white text
accent_color = "#00ffcc"    
list_bg = "#1a1a1a"    #listbox background
text_bg = "#101010" #text widget background

# Default font settings for readability
DETAIL_FONT = ("Arial", 11)
HEADER_FONT = ("Arial", 11, "bold")
#api
class MealAPI:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def dbcategories(self):
        try:                                   
            r = requests.get(self.base_url + "categories.php", timeout=30) #wait 30seconds for response
            if r.status_code != 200:                        
                return []        #prevent crashing
            return [c["strCategory"] for c in r.json()["categories"]]
        except requests.exceptions.RequestException:   #catch all network errors
            return []        # Fail safely
    
    def fetch_areas(self):
        try:
            r = requests.get(self.base_url + "list.php?a=list", timeout=30)
            if r.status_code != 200:
                return []
            return [a["strArea"] for a in r.json()["meals"]]
        except requests.exceptions.RequestException:
            return []
    
    def search_by_ingredient(self, ingredient):
        try:
            r = requests.get(self.base_url + f"filter.php?i={ingredient}", timeout=30)
            return r.json()["meals"] if r.status_code == 200 else []
        except requests.exceptions.RequestException:
            return []
    
    def search_by_category(self, category):
        try:
            r = requests.get(self.base_url + f"filter.php?c={category}", timeout=30)
            return r.json()["meals"] if r.status_code == 200 else []
        except requests.exceptions.RequestException:
            return []
    
    def search_by_area(self, area):
        try:
            r = requests.get(self.base_url + f"filter.php?a={area}", timeout=30)
            return r.json()["meals"] if r.status_code == 200 else []
        except requests.exceptions.RequestException:
            return []
    
    def get_meal_details(self, meal_id):
        try:
            r = requests.get(self.base_url + f"lookup.php?i={meal_id}", timeout=30)
            if r.status_code != 200:
                return None
            return r.json()["meals"][0]
        except requests.exceptions.RequestException:
            return None
api = MealAPI(db_url)

#function for gui
def clear_ui():
    results_listbox.delete(0, tk.END) #clears the listbox
    details_text.config(state=tk.NORMAL)  #enable editing temporarily
    details_text.delete("1.0", tk.END)  #clears the text area
    details_text.config(state=tk.DISABLED)  #disable editing
    image_label.config(image="")         
    image_label.image = None              
    status_label.config(text="Ready", fg=accent_color)    

def update_list(meals):
    clear_ui()   #clears the previous data
    if meals is None:        #error
        status_label.config(text="There's an error. no meal or no internet connection",fg="red")
        return

    if not meals: #if no meals
        status_label.config(text="No meals found for this search.",fg="orange")
        return

    for meal in meals:      #add on meal box
        results_listbox.insert(tk.END, meal["strMeal"])

    global current_meals   #store meals list
    current_meals = meals
    status_label.config(text=f"{len(meals)} meals loaded successfully.",fg="lightgreen")

def ingredient_search():
    ingredient = ingredient_entry.get().strip()         # Read input
    if not ingredient:
        status_label.config(text="Enter an ingredient.", fg="red")
        return
    update_list(api.search_by_ingredient(ingredient))

def category_search():
    category = category_var.get()   #get the dropdown value
    if category == "Select Category":
        status_label.config(text="Select a category.", fg="red")
        return
    update_list(api.search_by_category(category))

def area_search():
    area = area_var.get() 
    if area == "Select Country":
        status_label.config(text="Select a country.", fg="red")
        return
    update_list(api.search_by_area(area))

def chef_commentary(meal):
    meal_name = meal["strMeal"].lower()
    category = meal["strCategory"].lower()

    if category == "dessert":
        return "Dessert time! Sweet choice"
    #name based rule
    if "beef" in meal_name:
        return "A tender beef is always satisfyinggg"
    if "chicken" in meal_name:
        return "I love chickenz!"
    if any(fish in meal_name for fish in ["fish", "salmon", "tuna", "prawns", "squid"]):
        return "i really don't like fish but it's healthy"
    
    ingredients = [
        meal[f"strIngredient{i}"].lower()
        for i in range(1, 21)
        if meal[f"strIngredient{i}"] and isinstance(meal[f"strIngredient{i}"], str)]
    if any("beef" in ing for ing in ingredients):
        return "Beef dishes are always so satisfying."
    if any("chicken" in ing for ing in ingredients):
        return "Gooood choice, i love chicken"
    if any(fish in ing for fish in ["fish", "salmon", "tuna"] for ing in ingredients):
        return "I really dont like fish.. but it's healthy"
    return "Let's start coooking!"
    
def show_details(event):
    if not results_listbox.curselection():    #if nothing is selected
        return

    index = results_listbox.curselection()[0]  #tkinter listbox method
    meal_id = current_meals[index]["idMeal"]   #get the meal id
    meal = api.get_meal_details(meal_id)     #get meal details

    if not meal:
        status_label.config(text="Failed to load details.", fg="red")
        return
    comm= chef_commentary(meal)
    details_text.config(state=tk.NORMAL)  #enable editing
    details_text.delete("1.0", tk.END)  #clears the textbox

    # Clear, readable formatting for meal details
    details_text.insert(tk.END, f"{meal['strMeal']}\n", "title")
    details_text.insert(tk.END, f"Category: {meal['strCategory']}\n")
    details_text.insert(tk.END, f"Country: {meal['strArea']}\n")
    details_text.insert(tk.END, f"Chef AI says: {comm}\n\n", "chef")

    details_text.insert(tk.END, "Ingredients\n", "header")
    for i in range(1, 21):  #loop the ingredients
        ing = meal[f"strIngredient{i}"]
        meas = meal[f"strMeasure{i}"]
        if ing and ing.strip():
            details_text.insert(tk.END, f"- {ing} {meas}\n")

    details_text.insert(tk.END, "\nInstructions\n", "header")
    details_text.insert(tk.END, meal["strInstructions"])
    details_text.config(state=tk.DISABLED)  #lock the text box
    try:
        img_data = requests.get(meal["strMealThumb"], timeout=30).content
        img = Image.open(BytesIO(img_data)).resize((250, 250))
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.image = photo
    except requests.exceptions.RequestException:
        image_label.config(image="")
        image_label.image = None
    status_label.config(text="Meal details loaded.", fg=accent_color)

#GUI 
root = tk.Tk()
root.title("Be a Chef")       
root.geometry("950x650") #window size
root.config(bg=bg_color)  #apply dark background

current_meals = []  #store the meals globally

tk.Label(root, text="Be a Chef!", font=("Arial", 20, "bold"), bg=bg_color, fg=text_color).pack(pady=10)

search_frame = tk.LabelFrame(root, text="Search Meals", padx=10, pady=10, bg=frame_color, fg=text_color)
search_frame.pack(fill=tk.X, padx=10)

ingredient_entry = tk.Entry(search_frame, width=20)
ingredient_entry.grid(row=0, column=0, padx=5)
ingredient_entry.bind("<Return>", lambda event: ingredient_search())
tk.Button(search_frame, text="Ingredient", command=ingredient_search).grid(row=0, column=1)

category_var = tk.StringVar(value="Select Category")
tk.OptionMenu(search_frame, category_var,
              *api.dbcategories()).grid(row=0, column=2, padx=5)
tk.Button(search_frame, text="Category",
          command=category_search).grid(row=0, column=3)

area_var = tk.StringVar(value="Select Country")
tk.OptionMenu(search_frame, area_var,
              *api.fetch_areas()).grid(row=0, column=4, padx=5)
tk.Button(search_frame, text="Country",
          command=area_search).grid(row=0, column=5)

main_frame = tk.Frame(root, bg=bg_color)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

list_frame = tk.LabelFrame(main_frame, text="Meals",bg=frame_color, fg=text_color)
list_frame.pack(side=tk.LEFT, fill=tk.Y)

results_listbox = tk.Listbox(list_frame, width=30,height=25,
    bg=list_bg, fg=text_color,selectbackground=accent_color)
results_listbox.pack(side=tk.LEFT)
results_listbox.bind("<<ListboxSelect>>", show_details)
                        #virtual event
scroll = tk.Scrollbar(list_frame, command=results_listbox.yview)
scroll.pack(side=tk.RIGHT, fill=tk.Y)
results_listbox.config(yscrollcommand=scroll.set)

details_frame = tk.LabelFrame(main_frame, text="Meal Details", bg=frame_color,fg=text_color)
details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

image_label = tk.Label(details_frame, bg=frame_color)
image_label.pack(pady=5)

details_text = tk.Text(details_frame, wrap=tk.WORD, bg=text_bg, fg=text_color, font=DETAIL_FONT)
details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

#much better text
details_text.tag_config("title", font=("Arial", 14, "bold"))
details_text.tag_config("header", font=HEADER_FONT, foreground=accent_color)
details_text.tag_config("chef",foreground="#00ffcc",font=("Arial", 11, "italic"),justify="right",background="#202020")

text_scroll = tk.Scrollbar(details_frame, command=details_text.yview)
text_scroll.pack(side=tk.RIGHT, fill=tk.Y)   #fills full height of the listbox
details_text.config(yscrollcommand=text_scroll.set, state=tk.DISABLED)

status_label = tk.Label(root, text="Ready", anchor='se', bg=bg_color, fg=accent_color)
status_label.pack(fill=tk.X, padx=10, pady=5)

root.mainloop()   #start the application
