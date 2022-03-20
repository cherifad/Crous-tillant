import pickle
import sys
from datetime import date, timedelta, datetime
from bs import Menu, day_of_week_FR, GenerateJson

sys.path.append(".")


def importData(name):
    success = True

    list_food = []

    try:
        with open(name, 'rb') as inp:
            list_food = pickle.load(inp)

    except:

        success = False

    return list_food


def update(url):
    name = GenerateJson(url)

    return name


def customToString(menuObject: Menu) -> str:
    return_string = ''

    for food in menuObject.food:
        if str(food).upper().find("ENTR") != -1:
            return_string += "\n**{}**\n".format(food)
        if str(food).upper().find("PLAT") != -1:
            return_string += "\n**{}**\n".format(food)
        elif str(food).upper().find("DESSERT") != -1:
            return_string += "\n**{}**\n".format(food)
        else:
            return_string += "{}\n".format(str(food))

    return return_string


def search(query, list_p: list, day=None, date_p=None):
    return_list = []

    base = datetime.today()
    date_list = [base + timedelta(days=x + 1) for x in range(7)]
    formated_date =[]

    for date in date_list:
        formated_date.append(date.strftime('%Y-%m-%d'))

    seven_day_date = (date.today() + timedelta(days=7)).strftime("%Y-%d-%m")

    if query == 'today':
        for food in list_p:
            if date.today() == food.date:
                return_list.append(food)

    if query == 'week':
        for food in list_p:
            if datetime.strptime(seven_day_date, '%Y-%d-%m').date() >= food.date:
                return_list.append(food)

    if query == 'day':
        for food in list_p:
            if str(food.day).upper() == day.upper() and str(food.date) in formated_date:
                return_list.append(food)

    if query == 'date':
        for food in list_p:
            if str(food.date) == date_p:
                return_list.append(food)

    return return_list


def days():
    list_days = []

    base = datetime.today()
    date_list = [base + timedelta(days=x + 1) for x in range(7)]

    for day in date_list:
        try:
            list_days.append(day_of_week_FR[day.weekday()])
        except:
            pass

    return list_days


def availableDays(list_p: list):
    available_days = []

    for food in list_p:
        if food.day not in available_days:
            available_days.append(food.day)

    return available_days
