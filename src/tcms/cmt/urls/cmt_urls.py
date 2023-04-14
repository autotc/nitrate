# -*- coding: utf-8 -*-

from django.urls import path

from .. import views, ajax

urlpatterns = [
    path("apis/", views.SearchApisView.as_view(), name="apis-all"),
    path("api/new/", views.CreateNewApiView.as_view(), name="api-new"),
    path("api/<int:api_id>/", views.getApi, name="api-get"),
    path("api/<int:api_id>/<slug:slug>", views.getApi, name="api-get"),
    path("api/<int:api_id>/edit/", views.edit, name="api-edit"),

    path("api/<int:api_id>/data-edit/", views.apiDataEdit, name="api-data-edit"),


    path("management/getApiField/", ajax.getApiFieldType, name="ajax-getApiFieldType"),
    path("management/getApiList/", ajax.getApiList, name="ajax-getApiList"),
    path("management/getArrangeList/", ajax.getArrangeList, name="ajax-getArrangeList"),
    path("management/getPublicDefList/", ajax.getPublicDefList, name="ajax-getPublicDefList"),
    path("management/getPublicDataList/", ajax.getPublicDataList, name="ajax-getPublicDataList"),
    path("management/getApiDetail/", ajax.getApiDetail, name="ajax-getApiDetail"),
    path("management/getArrangeInputAndOutPut/", ajax.getArrangeInputAndOutPut, name="ajax-getArrangeInputAndOutPut"),
    path("management/getPublicDefInputAndOutPut/", ajax.getPublicDefInputAndOutPut, name="ajax-getPublicDefInputAndOutPut"),


    path("case/new/", views.CreateNewCaseView.as_view(), name="case-new"),
    path("case/<int:case_id>/", views.getCase, name="cmt-case-get"),
    path("case/<int:case_id>/<slug:slug>", views.getCase, name="cmt-case-get"),
    path("cases/", views.SearchCaseView.as_view(), name="cmt-cases-all"),
    path("case/<int:case_id>/edit/", views.caseEdit, name="cmt-case-edit"),

    path("arrange/new/", views.CreateNewArrangeView.as_view(), name="cmt-arrange-new"),
    path("arrange/<int:arrange_id>/", views.getArrange, name="cmt-arrange-get"),
    path("arrange/<int:arrange_id>/<slug:slug>", views.getArrange, name="cmt-arrange-get"),
    path("arranges/", views.SearchArrangeView.as_view(), name="cmt-arranges-all"),
    path("arrange/<int:arrange_id>/edit/", views.arrangeEdit, name="cmt-arrange-edit"),

    path("public_def/new/", views.CreateNewPublicDefView.as_view(), name="cmt-public-def-new"),
    path("public_def/<int:public_def_id>/", views.getPublicDef, name="cmt-public-def-get"),
    path("public_def/<int:public_def_id>/<slug:slug>", views.getPublicDef, name="cmt-public-def-get"),
    path("public_defs/", views.SearchPublicDefView.as_view(), name="cmt-public-def-all"),
    path("public_def/<int:public_def_id>/edit/", views.publicDefEdit, name="cmt-public-def-edit"),

    path("public_data/new/", views.CreateNewPublicDataView.as_view(), name="cmt-public-data-new"),
    path("public_data/<int:public_data_id>/", views.getPublicData, name="cmt-public-data-get"),
    path("public_data/<int:public_data_id>/<slug:slug>", views.getPublicData, name="cmt-public-data-get"),
    path("public_datas/", views.SearchPublicDataView.as_view(), name="cmt-public-data-all"),
    path("public_data/<int:public_data_id>/edit/", views.publicDataEdit, name="cmt-public-data-edit"),
]
