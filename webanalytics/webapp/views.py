from datetime import date

from django.http import HttpResponse
from django.shortcuts import render_to_response

from webanalytics.mongologger.logger import MongoLogger, MongoFetcher
from webanalytics.settings import MONGODB_SETTINGS


def home(request):
    return render_to_response("home.html")


def content(request, page=None):
    logger = MongoLogger(**MONGODB_SETTINGS)

    logger.log(id=page, data="access")

    return render_to_response("content.html", { "page_id" : page })


def metrics(request):
    fetcher = MongoFetcher(**MONGODB_SETTINGS)

    summary = fetcher.fetch(id=1, start_date=(date(2011, 9, 1)), end_date=date.today())

    return render_to_response("metrics.html", { "actions" : summary["action_types"], "summary" : summary["summary"] })


def asynchronous_metrics(request):
    id = request.GET.get("id")
    start = request.GET.get("start").split("-")
    end = request.GET.get("end").split("-")

    start_date = date(int(start[0]), int(start[1]), int(start[2]))
    end_date = date(int(end[0]), int(end[1]), int(end[2]))
    
    fetcher = MongoFetcher(**MONGODB_SETTINGS)

    summary = fetcher.fetch(id=id, start_date=start_date, end_date=end_date)

    return render_to_response("table.html", { "actions" : summary["action_types"], "summary" : summary["summary"] })


def log(request, id=None, action=None):
    logger = MongoLogger(**MONGODB_SETTINGS)

    logger.log(id=id, data=action)

    return HttpResponse()