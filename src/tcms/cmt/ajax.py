# -*- coding: utf-8 -*-
import datetime
import json
import logging
import operator
from collections.abc import Iterable
from functools import reduce
from typing import Any, Callable, Optional, Union

from django import forms
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import QuerySet
from django.dispatch import Signal
from django.http import HttpResponse, JsonResponse, QueryDict
from django.http.request import HttpRequest
from django.shortcuts import render
from django.views import View
from django.views.decorators.http import require_GET, require_http_methods

from tcms.core.mailto import mailto
from tcms.cmt.models import CmtApi, CmtArrange, CmtPublicDef, CmtPublicData


@require_GET
def getApiFieldType(request):
    public_apis = CmtApi.objects.filter(api_type_id=2)
    ans = [['String', 'String'], ['Map', 'Map'], ['List', 'List']]
    for api in public_apis:
        ans.append([api.description, api.description])

    return JsonResponse(ans, safe=False)


@require_GET
def getApiList(request):
    api_type = request.GET.get("api_type")
    service_id = request.GET.get("service_id")
    if service_id == '':
        apis = CmtApi.objects.filter(api_type_id=api_type, active_flag=1)
    else:
        apis = CmtApi.objects.filter(api_type_id=api_type, service_id=service_id)
    ans = [[api.api_id, api.description] for api in apis]
    return JsonResponse(ans, safe=False)


@require_GET
def getArrangeList(request):
    service_id = request.GET.get("service_id")
    if service_id == '':
        arranges = CmtArrange.objects.all()
    else:
        arranges = CmtArrange.objects.filter(service_id=service_id)
    ans = [[arrange.arrange_id, arrange.description] for arrange in arranges]
    return JsonResponse(ans, safe=False)


@require_GET
def getPublicDefList(request):
    service_id = request.GET.get("service_id")
    if service_id == '':
        public_def = CmtPublicDef.objects.all()
    else:
        public_def = CmtPublicDef.objects.filter(service_id=service_id)
    ans = [[elem.public_def_id, elem.description] for elem in public_def]
    return JsonResponse(ans, safe=False)


@require_GET
def getPublicDataList(request):
    service_id = request.GET.get("service_id")
    if service_id == '':
        public_data = CmtPublicData.objects.all()
    else:
        public_data = CmtPublicData.objects.filter(service_id=service_id)
    ans = [[elem.public_data_id, elem.description] for elem in public_data]
    return JsonResponse(ans, safe=False)


@require_GET
def getApiDetail(request):
    api_id = request.GET.get("api_id")
    if api_id == "":
        return JsonResponse({}, safe=False)
    api = CmtApi.objects.get(api_id=api_id)
    ans = {'input': json.loads(api.input), 'output': json.loads(api.output), 'endpoint': api.endpoint}
    return JsonResponse(ans, safe=False)


@require_GET
def getArrangeInputAndOutPut(request):
    arrange_id = request.GET.get("arrange_id")
    if arrange_id == "":
        return JsonResponse({}, safe=False)
    arrange = CmtArrange.objects.get(arrange_id=arrange_id)
    ans = {'input': json.loads(arrange.input), 'output': json.loads(arrange.output)}
    return JsonResponse(ans, safe=False)


@require_GET
def getPublicDefInputAndOutPut(request):
    public_def_id = request.GET.get("public_def_id")
    if public_def_id == "":
        return JsonResponse({}, safe=False)
    cpd = CmtPublicDef.objects.get(public_def_id=public_def_id)
    ans = {'input': json.loads(cpd.input), 'output': json.loads(cpd.output)}
    return JsonResponse(ans, safe=False)


def object2Map(obj: object):
    """对象转Dict"""
    m = obj.__dict__
    for k in m.keys():
        v = m[k]
        if hasattr(v, "__dict__"):
            m[k] = object2Map(v)
    return m
