# -*- coding: utf-8 -*-

import datetime
import functools
import itertools
import json
import copy
import urllib
from operator import add, itemgetter
from typing import Optional

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django.views.generic import View
from django.views.generic.base import TemplateView
from uuslug import slugify
from tcms.cmt.forms import (
    NewApiForm,
    SearchApiForm,
    EditApiForm,
    ApiDataEditForm,
    NewCaseForm,
    SearchCaseForm,
    EditCaseForm,
    NewArrangeForm,
    SearchArrangeForm,
    EditArrangeForm,
    NewPublicDefForm,
    SearchPublicDefForm,
    EditPublicDefForm,
    NewPublicDataForm,
    SearchPublicDataForm,
    EditPublicDataForm,
)
from tcms.cmt.models import CmtApi, CmtService, CmtApiData, CmtCase, CmtArrange, CmtPublicDef, CmtPublicData

MODULE_NAME = "cmt"


class CreateNewApiView(PermissionRequiredMixin, View):
    sub_module_name = "new_api"
    template_name = "cmt/api/new.html"
    permission_required = (
        "testplans.add_testplan",
        "testplans.add_testplantext",
        "testplans.add_tcmsenvplanmap",
    )

    def make_response(self, form):
        return render(
            self.request,
            self.template_name,
            context={
                "module": MODULE_NAME,
                "sub_module": self.sub_module_name,
                "form": form,
            },
        )

    def get(self, request):
        form = NewApiForm(initial={"active_flag": True})
        return self.make_response(form)

    @method_decorator(csrf_protect)
    def post(self, request):
        form = NewApiForm(request.POST)

        if not form.is_valid():
            print(">>>> not is_valid")
            return self.make_response(form)

        ca = CmtApi.objects.create(
            description=form.cleaned_data["description"],
            service=form.cleaned_data["service"],
            api_type=form.cleaned_data["api_type"],
            active_flag=form.cleaned_data["active_flag"],
            endpoint=form.cleaned_data["endpoint"],
            run_way=form.cleaned_data["run_way"],
            input=form.cleaned_data["input"],
            output=form.cleaned_data["output"],
            tag=form.cleaned_data["tag"],
            author=request.user,
            create_date=datetime.datetime.now(),
        )
        return HttpResponseRedirect(reverse("api-get", args=[ca.api_id]))


def getApi(request, api_id, slug=None, template_name="cmt/api/get.html"):
    """Display the plan details."""
    SUB_MODULE_NAME = "apis"

    try:
        ca = CmtApi.objects.select_related().get(api_id=api_id)
    except ObjectDoesNotExist:
        raise Http404

    # redirect if has a cheated slug
    if slug != slugify(ca.description):
        return HttpResponsePermanentRedirect(ca.get_absolute_url())

    context_data = {
        "module": MODULE_NAME,
        "sub_module": SUB_MODULE_NAME,
        "cmt_api": ca,
    }
    return render(request, template_name, context=context_data)


class SimpleApisFilterView(TemplateView):
    template_name = ""

    def filter_apis(self):
        search_form = SearchApiForm(self.request.GET)

        apis = CmtApi.objects.none()

        if search_form.is_valid():
            author = self.request.GET.get("author__email__startswith")
            req_user = self.request.user

            if req_user.is_authenticated and author in (
                    req_user.username,
                    req_user.email,
            ):
                self.SUB_MODULE_NAME = "my_apis"

            apis = (
                CmtApi.search(search_form.cleaned_data)
                .select_related("service")
                .order_by("-create_date")
            )
        return search_form, apis

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_api_form"], context["apis"] = self.filter_apis()
        return context


class SearchApisView(SimpleApisFilterView):
    SUB_MODULE_NAME = "apis"
    template_name = "cmt/api/all.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "module": MODULE_NAME,
                "sub_module": self.SUB_MODULE_NAME,
                "object_list": context["apis"][0:20],
                "apis_count": context["apis"].count(),
            }
        )
        return context


@require_http_methods(["GET", "POST"])
@permission_required("testplans.change_testplan")
def edit(request, api_id, template_name="cmt/api/edit.html"):
    SUB_MODULE_NAME = "apis"

    try:
        ca = CmtApi.objects.select_related().get(api_id=api_id)
    except ObjectDoesNotExist:
        raise Http404

    # If the form is submitted
    if request.method == "POST":
        form = EditApiForm(request.POST)

        # FIXME: Error handle
        if form.is_valid():
            ca.description = form.cleaned_data["description"]
            ca.service = form.cleaned_data["service"]
            ca.api_type = form.cleaned_data["api_type"]
            ca.active_flag = form.cleaned_data["active_flag"]
            ca.endpoint = form.cleaned_data["endpoint"]
            ca.run_way = form.cleaned_data["run_way"]
            ca.input = form.cleaned_data["input"]
            ca.output = form.cleaned_data["output"]
            ca.tag = form.cleaned_data["tag"]
            ca.author = request.user
            ca.create_date = datetime.datetime.now()
            ca.save()
            return HttpResponseRedirect(reverse("api-get", args=[api_id, slugify(ca.description)]))
    else:
        form = EditApiForm(
            initial={
                "description": ca.description,
                "service": ca.service,
                "api_type": ca.api_type,
                "active_flag": ca.active_flag,
                "endpoint": ca.endpoint,
                "run_way": ca.run_way,
                "tag": ca.tag,
                "input": ca.input,
                "output": ca.output,
            }
        )

    context_data = {
        "module": MODULE_NAME,
        "sub_module": SUB_MODULE_NAME,
        "cmt_api": ca,
        "form": form,
    }
    return render(request, template_name, context=context_data)


@require_http_methods(["GET", "POST"])
@permission_required("testplans.change_testplan")
def apiDataEdit(request, api_id, template_name="cmt/api/api_data_edit.html"):
    SUB_MODULE_NAME = "api_data_edit"
    print(">>>>>>>>>api_id:{}".format(api_id))
    try:
        ca = CmtApi.objects.select_related().get(api_id=api_id)
    except ObjectDoesNotExist:
        raise Http404

    # If the form is submitted
    if request.method == "POST":
        form = ApiDataEditForm(request.POST)
        print(">>>>>>>>>POST:{}".format(request.POST))
        # FIXME: Error handle
        if form.is_valid():
            cad = CmtApiData()
            cad.api = ca
            cad.description = form.cleaned_data["description"]
            cad.service = ca.service
            cad.use_flag = form.cleaned_data["use_flag"]
            cad.input = form.cleaned_data["input"]
            cad.output = form.cleaned_data["output"]
            cad.author = request.user
            cad.create_date = datetime.datetime.now()
            cad.save()
            return HttpResponseRedirect(reverse("api-get", args=[api_id, slugify(cad.description)]))
    else:
        inputDict = {}
        for key, value in json.loads(ca.input).items():
            inputDict[key + '|' + value] = ''
        outputDict = {}

        object = json.loads(ca.output)
        for key, value in object.items():
            outputDict[key + '|' + value] = ''

        form = ApiDataEditForm(initial={
            "api": ca.description,
            "service": ca.service,
            "api_type": ca.api_type,
            "use_flag": True,
            "input": json.dumps(inputDict),
            "output": json.dumps(outputDict),
        })
    context_data = {
        "module": MODULE_NAME,
        "sub_module": SUB_MODULE_NAME,
        "cmt_api": ca,
        "form": form,
    }
    return render(request, template_name, context=context_data)


class CreateNewCaseView(PermissionRequiredMixin, View):
    sub_module_name = "new_case"
    template_name = "cmt/case/new.html"
    permission_required = (
        "testplans.add_testplan",
        "testplans.add_testplantext",
        "testplans.add_tcmsenvplanmap",
    )

    def make_response(self, form):
        return render(
            self.request,
            self.template_name,
            context={
                "module": MODULE_NAME,
                "sub_module": self.sub_module_name,
                "form": form,
            },
        )

    def get(self, request):
        form = NewCaseForm(initial={"active_flag": True})
        return self.make_response(form)

    @method_decorator(csrf_protect)
    def post(self, request):
        form = NewCaseForm(request.POST)
        form.populate(service_id=request.POST.get("service"))
        if not form.is_valid():
            return self.make_response(form)
        cc = CmtCase.objects.create(
            description=form.cleaned_data["description"],
            active_flag=form.cleaned_data["active_flag"],
            service=form.cleaned_data["service"],
            public_request=form.cleaned_data["public_request"],
            rel_type=form.cleaned_data["rel_type"],
            api=form.cleaned_data["api"],
            arrange=form.cleaned_data["arrange"],
            tag=form.cleaned_data["tag"],
            input=form.cleaned_data["input"],
            pass_rule=form.cleaned_data["pass_rule"],
            author=request.user,
            create_date=datetime.datetime.now(),
        )

        return HttpResponseRedirect(reverse("cmt-case-get", args=[cc.case_id]))


class SimpleCaseFilterView(TemplateView):
    template_name = ""

    def filter_cases(self):
        search_form = SearchCaseForm(self.request.GET)

        cases = CmtCase.objects.none()

        if search_form.is_valid():
            author = self.request.GET.get("author__email__startswith")
            req_user = self.request.user

            if req_user.is_authenticated and author in (
                    req_user.username,
                    req_user.email,
            ):
                self.SUB_MODULE_NAME = "my_cases"

            cases = (
                CmtCase.search(search_form.cleaned_data)
                .select_related("service", "rel_type", "public_request", "api", "author")
                .order_by("-create_date")
            )
        return search_form, cases

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_case_form"], context["cases"] = self.filter_cases()
        return context


class SearchCaseView(SimpleCaseFilterView):
    SUB_MODULE_NAME = "cases"
    template_name = "cmt/case/all.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "module": MODULE_NAME,
                "sub_module": self.SUB_MODULE_NAME,
                "object_list": context["cases"][0:20],
                "cases_count": context["cases"].count(),
            }
        )
        return context


@require_http_methods(["GET", "POST"])
@permission_required("testplans.change_testplan")
def caseEdit(request, case_id, template_name="cmt/case/edit.html"):
    SUB_MODULE_NAME = "cases"

    try:
        cc = CmtCase.objects.select_related().get(case_id=case_id)
    except ObjectDoesNotExist:
        raise Http404
    # If the form is submitted
    if request.method == "POST":
        form = EditCaseForm(request.POST)
        form.populate(service_id=request.POST.get("service"))
        # FIXME: Error handle
        if form.is_valid():
            cc.description = form.cleaned_data["description"]
            cc.service = form.cleaned_data["service"]
            cc.active_flag = form.cleaned_data["active_flag"]
            cc.public_request = form.cleaned_data["public_request"]
            cc.rel_type = form.cleaned_data["rel_type"]
            cc.api = form.cleaned_data["api"]
            cc.arrange = form.cleaned_data["arrange"]
            cc.input = form.cleaned_data["input"]
            cc.pass_rule = form.cleaned_data["pass_rule"]
            cc.tag = form.cleaned_data["tag"]
            cc.author = request.user
            cc.create_date = datetime.datetime.now()
            cc.save()
            return HttpResponseRedirect(reverse("cmt-case-get", args=[case_id, slugify(cc.description)]))
    else:
        form = EditCaseForm(
            initial={
                "description": cc.description,
                "service": cc.service,
                "active_flag": cc.active_flag,
                "public_request": cc.public_request,
                "rel_type": cc.rel_type,
                "api": cc.api,
                "arrange": cc.arrange,
                "input": cc.input,
                "pass_rule": cc.pass_rule,
                "tag": cc.tag,
            }
        )
        form.populate(service_id=request.POST.get("service"))

    context_data = {
        "module": MODULE_NAME,
        "sub_module": SUB_MODULE_NAME,
        "cmt_case": cc,
        "form": form,
    }
    return render(request, template_name, context=context_data)


def getCase(request, case_id, slug=None, template_name="cmt/case/get.html"):
    """Display the plan details."""
    SUB_MODULE_NAME = "cases"

    try:
        cc = CmtCase.objects.select_related().get(case_id=case_id)
    except ObjectDoesNotExist:
        raise Http404

    # redirect if has a cheated slug
    if slug != slugify(cc.description):
        return HttpResponsePermanentRedirect(cc.get_absolute_url())

    context_data = {
        "module": MODULE_NAME,
        "sub_module": SUB_MODULE_NAME,
        "cmt_case": cc,
    }
    return render(request, template_name, context=context_data)


class CreateNewArrangeView(PermissionRequiredMixin, View):
    sub_module_name = "new_arrange"
    template_name = "cmt/arrange/new.html"
    permission_required = (
        "testplans.add_testplan",
        "testplans.add_testplantext",
        "testplans.add_tcmsenvplanmap",
    )

    def make_response(self, form):
        return render(
            self.request,
            self.template_name,
            context={
                "module": MODULE_NAME,
                "sub_module": self.sub_module_name,
                "form": form,
            },
        )

    def get(self, request):
        form = NewArrangeForm(initial={"active_flag": True})
        return self.make_response(form)

    @method_decorator(csrf_protect)
    def post(self, request):
        form = NewArrangeForm(request.POST)
        if not form.is_valid():
            return self.make_response(form)
        print(">>>>>!!!<<service:{}".format(form.cleaned_data["service"]))
        print(">>>>>!!!<<apis:{}".format(form.cleaned_data["apis"]))
        cc = CmtArrange.objects.create(
            description=form.cleaned_data["description"],
            service=form.cleaned_data["service"],
            active_flag=form.cleaned_data["active_flag"],
            apis=form.cleaned_data["apis"],
            input=form.cleaned_data["input"],
            output=form.cleaned_data["output"],
            author=request.user,
            create_date=datetime.datetime.now(),
        )

        return HttpResponseRedirect(reverse("cmt-arrange-get", args=[cc.arrange_id]))


class SimpleArrangeFilterView(TemplateView):
    template_name = ""

    def filter_arranges(self):
        search_form = SearchArrangeForm(self.request.GET)

        arranges = CmtArrange.objects.none()

        if search_form.is_valid():
            author = self.request.GET.get("author__email__startswith")
            req_user = self.request.user

            if req_user.is_authenticated and author in (
                    req_user.username,
                    req_user.email,
            ):
                self.SUB_MODULE_NAME = "my_cases"

            arranges = (
                CmtArrange.search(search_form.cleaned_data)
                .select_related("service", "author")
                .order_by("-create_date")
            )
        return search_form, arranges

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_arrange_form"], context["arranges"] = self.filter_arranges()
        return context


class SearchArrangeView(SimpleArrangeFilterView):
    SUB_MODULE_NAME = "arranges"
    template_name = "cmt/arrange/all.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "module": MODULE_NAME,
                "sub_module": self.SUB_MODULE_NAME,
                "object_list": context["arranges"][0:20],
                "arranges_count": context["arranges"].count(),
            }
        )
        return context


@require_http_methods(["GET", "POST"])
@permission_required("testplans.change_testplan")
def arrangeEdit(request, arrange_id, template_name="cmt/arrange/edit.html"):
    SUB_MODULE_NAME = "arranges"

    try:
        arrange = CmtArrange.objects.select_related().get(arrange_id=arrange_id)
    except ObjectDoesNotExist:
        raise Http404
    # If the form is submitted
    if request.method == "POST":
        form = EditArrangeForm(request.POST)
        # form.populate(service_id=request.POST.get("service"))
        # FIXME: Error handle
        if form.is_valid():
            arrange.description = form.cleaned_data["description"]
            arrange.service = form.cleaned_data["service"]
            arrange.active_flag = form.cleaned_data["active_flag"]
            arrange.apis = form.cleaned_data["apis"]
            arrange.input = form.cleaned_data["input"]
            arrange.output = form.cleaned_data["output"]
            arrange.author = request.user
            arrange.create_date = datetime.datetime.now()
            arrange.save()
            return HttpResponseRedirect(reverse("cmt-arrange-get", args=[arrange_id, slugify(arrange.description)]))
    else:
        form = EditArrangeForm(
            initial={
                "description": arrange.description,
                "service": arrange.service,
                "active_flag": arrange.active_flag,
                "apis": arrange.apis,
                "input": arrange.input,
                "output": arrange.output,
            }
        )
        # form.populate(service_id=request.POST.get("service"))

    context_data = {
        "module": MODULE_NAME,
        "sub_module": SUB_MODULE_NAME,
        "cmt_arrange": arrange,
        "form": form,
    }
    return render(request, template_name, context=context_data)


def getArrange(request, arrange_id, slug=None, template_name="cmt/arrange/get.html"):
    """Display the plan details."""
    SUB_MODULE_NAME = "arranges"

    try:
        arrange = CmtArrange.objects.select_related().get(arrange_id=arrange_id)
    except ObjectDoesNotExist:
        raise Http404

    # redirect if has a cheated slug
    if slug != slugify(arrange.description):
        return HttpResponsePermanentRedirect(arrange.get_absolute_url())

    context_data = {
        "module": MODULE_NAME,
        "sub_module": SUB_MODULE_NAME,
        "cmt_arrange": arrange,
    }
    return render(request, template_name, context=context_data)


class CreateNewPublicDefView(PermissionRequiredMixin, View):
    sub_module_name = "new_public_def"
    template_name = "cmt/public_def/new.html"
    permission_required = (
        "testplans.add_testplan",
        "testplans.add_testplantext",
        "testplans.add_tcmsenvplanmap",
    )

    def make_response(self, form):
        return render(
            self.request,
            self.template_name,
            context={
                "module": MODULE_NAME,
                "sub_module": self.sub_module_name,
                "form": form,
            },
        )

    def get(self, request):
        form = NewPublicDefForm(initial={"active_flag": True})
        return self.make_response(form)

    @method_decorator(csrf_protect)
    def post(self, request):
        form = NewPublicDefForm(request.POST)

        if not form.is_valid():
            return self.make_response(form)

        cpf = CmtPublicDef.objects.create(
            description=form.cleaned_data["description"],
            service=form.cleaned_data["service"],
            active_flag=form.cleaned_data["active_flag"],
            input=form.cleaned_data["input"],
            output=form.cleaned_data["output"],
            author=request.user,
            create_date=datetime.datetime.now(),
        )
        return HttpResponseRedirect(reverse("cmt-public-def-get", args=[cpf.public_def_id]))


def getPublicDef(request, public_def_id, slug=None, template_name="cmt/public_def/get.html"):
    SUB_MODULE_NAME = "public_def"

    try:
        cpf = CmtPublicDef.objects.select_related().get(public_def_id=public_def_id)
    except ObjectDoesNotExist:
        raise Http404

    if slug != slugify(cpf.description):
        return HttpResponsePermanentRedirect(cpf.get_absolute_url())

    context_data = {
        "module": MODULE_NAME,
        "sub_module": SUB_MODULE_NAME,
        "cmt_public_def": cpf
    }
    return render(request, template_name, context=context_data)


class SimplePublicDefFilterView(TemplateView):
    template_name = ""

    def filter_public_def(self):
        search_form = SearchPublicDefForm(self.request.GET)

        cpf = CmtPublicDef.objects.none()

        if search_form.is_valid():
            author = self.request.GET.get("author__email__startswith")
            req_user = self.request.user

            if req_user.is_authenticated and author in (
                    req_user.username,
                    req_user.email,
            ):
                self.SUB_MODULE_NAME = "my_public_def"

            cpf = (
                CmtPublicDef.search(search_form.cleaned_data)
                .select_related("service", "author")
                .order_by("-create_date")
            )
        return search_form, cpf

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_public_def_form"], context["cmt_public_def"] = self.filter_public_def()
        return context


class SearchPublicDefView(SimplePublicDefFilterView):
    SUB_MODULE_NAME = "public_def"
    template_name = "cmt/public_def/all.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "module": MODULE_NAME,
                "sub_module": self.SUB_MODULE_NAME,
                "object_list": context["cmt_public_def"][0:20],
                "public_def_count": context["cmt_public_def"].count(),
            }
        )
        return context


@require_http_methods(["GET", "POST"])
@permission_required("testplans.change_testplan")
def publicDefEdit(request, public_def_id, template_name="cmt/public_def/edit.html"):
    SUB_MODULE_NAME = "public_def"

    try:
        cpf = CmtPublicDef.objects.select_related().get(public_def_id=public_def_id)
    except ObjectDoesNotExist:
        raise Http404

    # If the form is submitted
    if request.method == "POST":
        form = EditPublicDefForm(request.POST)

        # FIXME: Error handle
        if form.is_valid():
            cpf.description = form.cleaned_data["description"]
            cpf.service = form.cleaned_data["service"]
            cpf.active_flag = form.cleaned_data["active_flag"]
            cpf.input = form.cleaned_data["input"]
            cpf.output = form.cleaned_data["output"]
            cpf.author = request.user
            cpf.create_date = datetime.datetime.now()
            cpf.save()
            return HttpResponseRedirect(reverse("cmt-public-def-get", args=[public_def_id, slugify(cpf.description)]))
    else:
        form = EditPublicDefForm(
            initial={
                "description": cpf.description,
                "service": cpf.service,
                "active_flag": cpf.active_flag,
                "input": cpf.input,
                "output": cpf.output,
            }
        )

    context_data = {
        "module": MODULE_NAME,
        "sub_module": SUB_MODULE_NAME,
        "cmt_public_def": cpf,
        "form": form,
    }
    return render(request, template_name, context=context_data)


class CreateNewPublicDataView(PermissionRequiredMixin, View):
    sub_module_name = "new_public_data"
    template_name = "cmt/public_data/new.html"
    permission_required = (
        "testplans.add_testplan",
        "testplans.add_testplantext",
        "testplans.add_tcmsenvplanmap",
    )

    def make_response(self, form):
        return render(
            self.request,
            self.template_name,
            context={
                "module": MODULE_NAME,
                "sub_module": self.sub_module_name,
                "form": form,
            },
        )

    def get(self, request):
        form = NewPublicDataForm(initial={"active_flag": True})
        return self.make_response(form)

    @method_decorator(csrf_protect)
    def post(self, request):
        form = NewPublicDataForm(request.POST)
        if not form.is_valid():
            return self.make_response(form)
        cpd = CmtPublicData.objects.create(
            description=form.cleaned_data["description"],
            active_flag=form.cleaned_data["active_flag"],
            service=form.cleaned_data["service"],
            public_def=form.cleaned_data["public_def"],
            input=form.cleaned_data["input"],
            output=form.cleaned_data["output"],
            author=request.user,
            create_date=datetime.datetime.now(),
        )

        return HttpResponseRedirect(reverse("cmt-public-data-get", args=[cpd.public_data_id]))


class SimplePublicDataFilterView(TemplateView):
    template_name = ""

    def filter_public_data(self):
        search_form = SearchPublicDataForm(self.request.GET)

        public_data = CmtPublicData.objects.none()

        if search_form.is_valid():
            author = self.request.GET.get("author__email__startswith")
            req_user = self.request.user

            if req_user.is_authenticated and author in (
                    req_user.username,
                    req_user.email,
            ):
                self.SUB_MODULE_NAME = "my_public_data"

            public_data = (
                CmtPublicData.search(search_form.cleaned_data)
                .select_related("service", "public_def", "author")
                .order_by("-create_date")
            )
        return search_form, public_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_public_data_form"], context["public_data"] = self.filter_public_data()
        return context


class SearchPublicDataView(SimplePublicDataFilterView):
    SUB_MODULE_NAME = "public_data"
    template_name = "cmt/public_data/all.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "module": MODULE_NAME,
                "sub_module": self.SUB_MODULE_NAME,
                "object_list": context["public_data"][0:20],
                "public_data_count": context["public_data"].count(),
            }
        )
        return context


@require_http_methods(["GET", "POST"])
@permission_required("testplans.change_testplan")
def publicDataEdit(request, public_data_id, template_name="cmt/public_data/edit.html"):
    SUB_MODULE_NAME = "public_data"

    try:
        cpd = CmtPublicData.objects.select_related().get(public_data_id=public_data_id)
    except ObjectDoesNotExist:
        raise Http404
    # If the form is submitted
    if request.method == "POST":
        form = EditPublicDataForm(request.POST)
        form.populate(service_id=request.POST.get("service"))
        # FIXME: Error handle
        if form.is_valid():
            cpd.description = form.cleaned_data["description"]
            cpd.service = form.cleaned_data["service"]
            cpd.active_flag = form.cleaned_data["active_flag"]
            cpd.public_def = form.cleaned_data["public_def"]
            cpd.input = form.cleaned_data["input"]
            cpd.output = form.cleaned_data["output"]
            cpd.author = request.user
            cpd.create_date = datetime.datetime.now()
            cpd.save()
            return HttpResponseRedirect(reverse("cmt-public-data-get", args=[public_data_id, slugify(cpd.description)]))
    else:
        form = EditPublicDataForm(
            initial={
                "description": cpd.description,
                "service": cpd.service,
                "active_flag": cpd.active_flag,
                "public_def": cpd.public_def,
                "input": cpd.input,
                "output": cpd.output,
            }
        )

    context_data = {
        "module": MODULE_NAME,
        "sub_module": SUB_MODULE_NAME,
        "cmt_public_data": cpd,
        "form": form,
    }
    return render(request, template_name, context=context_data)


def getPublicData(request, public_data_id, slug=None, template_name="cmt/public_data/get.html"):
    """Display the plan details."""
    SUB_MODULE_NAME = "public_data"

    try:
        cpd = CmtPublicData.objects.select_related().get(public_data_id=public_data_id)
    except ObjectDoesNotExist:
        raise Http404

    if slug != slugify(cpd.description):
        return HttpResponsePermanentRedirect(cpd.get_absolute_url())

    context_data = {
        "module": MODULE_NAME,
        "sub_module": SUB_MODULE_NAME,
        "cmt_public_data": cpd,
    }
    return render(request, template_name, context=context_data)
