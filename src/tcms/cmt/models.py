# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from textwrap import dedent
from typing import Any, Optional, Union

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Max, QuerySet
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from uuslug import slugify
from tcms.core.models import TCMSActionModel
from django.db.models import Q

log = logging.getLogger(__name__)


class CmtService(TCMSActionModel):
    service_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, verbose_name="服务器名称")
    env_type = models.CharField(max_length=8, verbose_name="环境")
    address = models.TextField(db_column="address", verbose_name="ip:port")
    create_date = models.DateTimeField(db_column="create_date", auto_now_add=True, verbose_name="创建时间")

    class Meta:

        db_table = "cmt_service"

    def __str__(self):
        return self.name

    @classmethod
    def search(self, query: Optional[dict[str, Any]] = None) -> QuerySet:
        new_query: dict[str, Any] = {}
        query_criteria = query or {}
        for k, v in query_criteria.items():
            if v and k not in ["action", "a", "t", "f"]:
                new_query[k] = hasattr(v, "strip") and v.strip() or v

        filter_args: list[Q] = []
        if search_keyword := new_query.get("search"):
            filter_args.append(
                Q(id__icontains=search_keyword) | Q(name__icontains=search_keyword)
            )
            del new_query["search"]
        return self.objects.filter(*filter_args, **new_query).distinct()


class ApiType(TCMSActionModel):
    type_code = models.CharField(max_length=8, verbose_name="类型代码")
    type_desc = models.CharField(max_length=16, verbose_name="类型描述")

    class Meta:
        db_table = "cmt_api_type"

    def __str__(self):
        return self.type_desc


class CmtApi(TCMSActionModel):
    api_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=32, verbose_name="api描述")
    service = models.ForeignKey(
        CmtService,
        related_name="apis",
        on_delete=models.CASCADE
    )
    api_type = models.ForeignKey(
        ApiType,
        related_name="apis",
        on_delete=models.CASCADE,
        default='1'
    )
    endpoint = models.CharField(max_length=64, null=True, verbose_name="url")
    active_flag = models.BooleanField(default=True)
    run_way = models.TextField(null=True, verbose_name="运行方式")
    input = models.TextField(null=True, blank=True, verbose_name="请求信息")
    output = models.TextField(null=True, blank=True, verbose_name="返回信息")
    tag = models.CharField(max_length=32, null=True)
    author = models.ForeignKey(
        "auth.User",
        blank=True,
        null=True,
        related_name="myapis",
        on_delete=models.CASCADE,
    )
    create_date = models.DateTimeField(db_column="create_date", auto_now_add=True)

    class Meta:
        db_table = "cmt_api"

    def __str__(self):
        return self.description

    @classmethod
    def search(cls, query: Optional[dict[str, Any]] = None) -> QuerySet:
        """Search apis"""

        new_query: dict[str, Any] = {}
        query_criteria = query or {}
        for k, v in query_criteria.items():
            if v and k not in ["action", "t", "f", "a"]:
                new_query[k] = hasattr(v, "strip") and v.strip() or v

        filter_args: list[Q] = []
        if search_keyword := new_query.get("search"):
            filter_args.append(
                Q(api_id__icontains=search_keyword) | Q(description__icontains=search_keyword)
            )
            del new_query["search"]

        return cls.objects.filter(*filter_args, **new_query).distinct()

    def get_absolute_url(self):
        return reverse(
            "api-get",
            kwargs={
                "api_id": self.api_id,
                "slug": slugify(self.description),
            },
        )

class CmtApiData(TCMSActionModel):
    api_data_id = models.AutoField(primary_key=True)
    api = models.ForeignKey(
        CmtApi,
        related_name="apiData",
        on_delete=models.CASCADE
    )
    service = models.ForeignKey(
        CmtService,
        related_name="apiData",
        on_delete=models.CASCADE
    )
    description = models.CharField(max_length=32, verbose_name="api描述")
    use_flag = models.BooleanField(default=True)
    input = models.TextField(null=True, blank=True, verbose_name="请求信息")
    output = models.TextField(null=True, blank=True, verbose_name="返回信息")
    author = models.ForeignKey(
        "auth.User",
        blank=True,
        null=True,
        related_name="apiData",
        on_delete=models.CASCADE,
    )
    create_date = models.DateTimeField(db_column="create_date", auto_now_add=True)

    class Meta:
        db_table = "cmt_api_data"

    def __str__(self):
        return self.description + '数据'

    @classmethod
    def search(cls, query: Optional[dict[str, Any]] = None) -> QuerySet:
        """Search apis"""

        new_query: dict[str, Any] = {}
        query_criteria = query or {}
        for k, v in query_criteria.items():
            if v and k not in ["action", "t", "f", "a"]:
                new_query[k] = hasattr(v, "strip") and v.strip() or v

        filter_args: list[Q] = []
        if search_keyword := new_query.get("search"):
            filter_args.append(
                Q(api_data_id__icontains=search_keyword) | Q(description__icontains=search_keyword)
            )
            del new_query["search"]

        return cls.objects.filter(*filter_args, **new_query).distinct()

    # def get_absolute_url(self):
    #     return reverse(
    #         "api-get",
    #         kwargs={
    #             "api_id": self.api_id,
    #             "slug": slugify(self.description),
    #         },
    #     )


class CmtCaseRelType(TCMSActionModel):
    type_desc = models.CharField(max_length=16, verbose_name="关联类型描述")

    class Meta:
        db_table = "cmt_case_rel_type"

    def __str__(self):
        return self.type_desc


class CmtCase(TCMSActionModel):
    case_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=32, verbose_name="案例描述")
    service = models.ForeignKey(
        CmtService,
        related_name="cases",
        on_delete=models.CASCADE,
    )
    public_request = models.ForeignKey(
        "CmtPublicData",
        related_name="cases",
        on_delete=models.CASCADE,
        null=True,
    )
    rel_type = models.ForeignKey(
        CmtCaseRelType,
        related_name="cases",
        on_delete=models.CASCADE,
    )
    api = models.ForeignKey(
        CmtApi,
        related_name="cases",
        on_delete=models.CASCADE,
        null=True,
    )
    arrange = models.ForeignKey(
        "CmtArrange",
        related_name="arranges",
        on_delete=models.CASCADE,
        null=True,
    )

    # arrange = models.CharField(max_length=64, verbose_name="关联的编排", null=True)
    tag = models.CharField(max_length=32, null=True, verbose_name="Tag")
    active_flag = models.BooleanField(default=True)
    input = models.TextField(null=True, blank=True, verbose_name="请求信息")
    output = models.TextField(null=True, blank=True, verbose_name="返回信息")
    pass_rule = models.CharField(max_length=64, null=True, verbose_name="通过规则")
    author = models.ForeignKey(
        "auth.User",
        blank=True,
        null=True,
        related_name="mycases",
        on_delete=models.CASCADE,
    )
    create_date = models.DateTimeField(db_column="create_date", auto_now_add=True)

    class Meta:
        db_table = "cmt_case"

    def __str__(self):
        return self.description

    @classmethod
    def search(cls, query: Optional[dict[str, Any]] = None) -> QuerySet:
        new_query: dict[str, Any] = {}
        query_criteria = query or {}
        for k, v in query_criteria.items():
            if v and k not in ["action", "t", "f", "a"]:
                new_query[k] = hasattr(v, "strip") and v.strip() or v

        filter_args: list[Q] = []
        if search_keyword := new_query.get("search"):
            filter_args.append(
                Q(api_id__icontains=search_keyword) | Q(description__icontains=search_keyword)
            )
            del new_query["search"]

        return cls.objects.filter(*filter_args, **new_query).distinct()

    def get_absolute_url(self):
        return reverse(
            "cmt-case-get",
            kwargs={
                "case_id": self.case_id,
                "slug": slugify(self.description),
            },
        )


class CmtArrange(TCMSActionModel):
    arrange_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=32, verbose_name="编排描述")
    service = models.ForeignKey(
        CmtService,
        related_name="arranges",
        on_delete=models.CASCADE
    )
    active_flag = models.BooleanField(default=True)

    apis = models.TextField(verbose_name="编排API")
    input = models.TextField(null=True, blank=True, verbose_name="请求信息")
    output = models.TextField(null=True, blank=True, verbose_name="返回信息")
    author = models.ForeignKey(
        "auth.User",
        blank=True,
        null=True,
        related_name="myarranges",
        on_delete=models.CASCADE,
    )
    create_date = models.DateTimeField(db_column="create_date", auto_now_add=True)

    class Meta:
        db_table = "cmt_arrange"

    def __str__(self):
        return self.description

    @classmethod
    def search(cls, query: Optional[dict[str, Any]] = None) -> QuerySet:
        new_query: dict[str, Any] = {}
        query_criteria = query or {}
        for k, v in query_criteria.items():
            if v and k not in ["action", "t", "f", "a"]:
                new_query[k] = hasattr(v, "strip") and v.strip() or v

        filter_args: list[Q] = []
        if search_keyword := new_query.get("search"):
            filter_args.append(
                Q(api_id__icontains=search_keyword) | Q(description__icontains=search_keyword)
            )
            del new_query["search"]

        return cls.objects.filter(*filter_args, **new_query).distinct()

    def get_absolute_url(self):
        return reverse(
            "cmt-arrange-get",
            kwargs={
                "arrange_id": self.arrange_id,
                "slug": slugify(self.description),
            },
        )


class CmtPublicDef(TCMSActionModel):
    public_def_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=32, verbose_name="公共请求定义描述")
    service = models.ForeignKey(
        CmtService,
        related_name="public_def",
        on_delete=models.CASCADE
    )
    active_flag = models.BooleanField(default=True)
    input = models.TextField(null=True, blank=True, verbose_name="请求信息")
    output = models.TextField(null=True, blank=True, verbose_name="返回信息")
    author = models.ForeignKey(
        "auth.User",
        blank=True,
        null=True,
        related_name="mine_public_def",
        on_delete=models.CASCADE,
    )
    create_date = models.DateTimeField(db_column="create_date", auto_now_add=True)

    class Meta:
        db_table = "cmt_public_def"

    def __str__(self):
        return self.description

    @classmethod
    def search(cls, query: Optional[dict[str, Any]] = None) -> QuerySet:
        new_query: dict[str, Any] = {}
        query_criteria = query or {}
        for k, v in query_criteria.items():
            if v and k not in ["action", "t", "f", "a"]:
                new_query[k] = hasattr(v, "strip") and v.strip() or v

        filter_args: list[Q] = []
        if search_keyword := new_query.get("search"):
            filter_args.append(
                Q(api_id__icontains=search_keyword) | Q(description__icontains=search_keyword)
            )
            del new_query["search"]

        return cls.objects.filter(*filter_args, **new_query).distinct()

    def get_absolute_url(self):
        return reverse(
            "cmt-public-def-get",
            kwargs={
                "public_def_id": self.public_def_id,
                "slug": slugify(self.description),
            },
        )


class CmtPublicData(TCMSActionModel):
    public_data_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=32, verbose_name="公共请求数据描述")
    service = models.ForeignKey(
        CmtService,
        related_name="public_data",
        on_delete=models.CASCADE,
    )
    active_flag = models.BooleanField(default=True)
    public_def = models.ForeignKey(
        CmtPublicDef,
        related_name="public_data",
        on_delete=models.CASCADE,
    )
    input = models.TextField(null=True, blank=True, verbose_name="请求信息")
    output = models.TextField(null=True, blank=True, verbose_name="返回信息")
    author = models.ForeignKey(
        "auth.User",
        blank=True,
        null=True,
        related_name="mine_public_data",
        on_delete=models.CASCADE,
    )
    create_date = models.DateTimeField(db_column="create_date", auto_now_add=True)

    class Meta:
        db_table = "cmt_public_data"

    def __str__(self):
        return self.description

    @classmethod
    def search(cls, query: Optional[dict[str, Any]] = None) -> QuerySet:
        new_query: dict[str, Any] = {}
        query_criteria = query or {}
        for k, v in query_criteria.items():
            if v and k not in ["action", "t", "f", "a"]:
                new_query[k] = hasattr(v, "strip") and v.strip() or v

        filter_args: list[Q] = []
        if search_keyword := new_query.get("search"):
            filter_args.append(
                Q(api_id__icontains=search_keyword) | Q(description__icontains=search_keyword)
            )
            del new_query["search"]

        return cls.objects.filter(*filter_args, **new_query).distinct()

    def get_absolute_url(self):
        return reverse(
            "cmt-public-data-get",
            kwargs={
                "public_data_id": self.public_data_id,
                "slug": slugify(self.description),
            },
        )




