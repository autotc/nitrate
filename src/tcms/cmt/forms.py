import logging
from django import forms
from django.forms import TextInput, widgets
from tcms.cmt.models import CmtService, ApiType, CmtCaseRelType, CmtCase, CmtApi, CmtArrange, CmtPublicDef, CmtPublicData
from tinymce.widgets import TinyMCE
# from splitjson.widgets import SplitJSONWidget
from tcms.cmt.widgets import SplitJSONWidget, SetDataWidget, ArrangApiWidget

log = logging.getLogger(__name__)

MIMETYPE_HTML = "text/html"
MIMETYPE_PLAIN = "text/plain"
MIMETYPE_OCTET_STREAM = "application/octet-stream"
MIMETYPE_OPENDOCUMENT = "application/vnd.oasis.opendocument.text"


class NewApiForm(forms.Form):
    description = forms.CharField(label="API名称", max_length=32)
    service = forms.ModelChoiceField(
        label=CmtService,
        queryset=CmtService.objects.all(),
        help_text="所属服务"
    )
    api_type = forms.ModelChoiceField(
        label=ApiType,
        queryset=ApiType.objects.all(),
        help_text="API类型"
    )
    active_flag = forms.BooleanField(label="是否有效", required=False)
    endpoint = forms.CharField(label="Url", max_length=64, required=False)
    tag = forms.CharField(label="Tag", required=False)
    run_way = forms.CharField(label="运行方式", widget=forms.Textarea, required=False)
    input = forms.CharField(label="入参", widget=SplitJSONWidget())
    output = forms.CharField(label="出参", widget=SplitJSONWidget())

    def clean_endpoint(self):
        api_type = self.cleaned_data["api_type"]
        if api_type == '1' and (len(self.cleaned_data["endpoint"].strip()) == 0):
            raise forms.ValidationError("非公共API必须输入endpoint")
        return self.cleaned_data["api_type"]


class SearchApiForm(forms.Form):
    description__startswith = forms.CharField(label="Description", required=False)
    service = forms.ModelChoiceField(
        label="Service",
        queryset=CmtService.objects.all(),
        required=False,
        help_text="所属服务"
    )
    api_type = forms.ModelChoiceField(
        label=ApiType,
        queryset=ApiType.objects.all(),
        help_text="API类型",
        required=False
    )
    endpoint__startswith = forms.CharField(label="Endpoint", required=False)
    author__username__startswith = forms.CharField(label="Author", required=False)
    create_date__gte = forms.DateTimeField(
        label="开始时间",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "vDateField"
            }
        )
    )
    create_date__lte = forms.DateTimeField(
        label="截止时间",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "vDateField"
            }
        )
    )


class EditApiForm(NewApiForm):
    pass


class ApiDataEditForm(forms.Form):
    api = forms.CharField(label="API", help_text="数据归属API")
    description = forms.CharField(label="API名称", max_length=32)
    service = forms.CharField(
        label="服务",
        help_text="所属服务",
    )
    use_flag = forms.BooleanField(label="是否有效", required=False)
    input = forms.CharField(label="入参", widget=SetDataWidget())
    output = forms.CharField(label="出参", widget=SetDataWidget())


class NewCaseForm(forms.Form):
    description = forms.CharField(label="案例名称", max_length=32)
    service = forms.ModelChoiceField(
        label="所属服务",
        queryset=CmtService.objects.all(),
        help_text="所属服务"
    )
    public_request = forms.ModelChoiceField(
        label="公共请求",
        queryset=CmtPublicData.objects.none(),
        required=False,
    )
    rel_type = forms.ModelChoiceField(
        label="关联类型",
        queryset=CmtCaseRelType.objects.all(),
        help_text="关联类型",
        blank=False,
        required=True,
        # empty_label=None,
    )
    api = forms.ModelChoiceField(
        label="关联的API",
        queryset=CmtApi.objects.none(),
        required=False,
    )
    arrange = forms.ModelChoiceField(
        label="关联的Arrange",
        queryset=CmtArrange.objects.none(),
        required=False,
    )

    active_flag = forms.BooleanField(label="是否有效", required=False)
    tag = forms.CharField(label="Tag", required=False)
    input = forms.CharField(label="入参", widget=SetDataWidget())
    # 通过配置的API或者ARR的output,来配置通过规则
    pass_rule = forms.CharField(label="通过规则", widget=SetDataWidget())

    def populate(self, service_id):
        if service_id:
            self.fields["api"].queryset = CmtApi.objects.filter(service_id=service_id)
            self.fields["arrange"].queryset = CmtArrange.objects.filter(service_id=service_id)
            self.fields["public_request"].queryset = CmtPublicData.objects.filter(service_id=service_id)
        else:
            self.fields["api"].queryset = CmtApi.objects.all()
            self.fields["arrange"].queryset = CmtArrange.objects.all()
            self.fields["public_request"].queryset = CmtPublicData.objects.all()

    def clean_api(self):
        rel_type = self.cleaned_data["rel_type"]
        if rel_type.id == 1 and (self.cleaned_data["api"] is None):
            raise forms.ValidationError("关联类型为API时，必须选择一个API")
        return self.cleaned_data["api"]

    def clean_arrange(self):
        rel_type = self.cleaned_data["rel_type"]
        if rel_type.id == 2 and (self.cleaned_data["arrange"] is None):
            raise forms.ValidationError("关联类型为Arrange时，必须选择一个Arrange")
        return self.cleaned_data["arrange"]


class SearchCaseForm(forms.Form):
    description__startswith = forms.CharField(label="Description", required=False)
    service = forms.ModelChoiceField(
        label="所属服务",
        queryset=CmtService.objects.all(),
        required=False,
        help_text="所属服务"
    )
    rel_type = forms.ModelChoiceField(
        label="案例关联类型",
        queryset=CmtCaseRelType.objects.all(),
        help_text="案例关联类型",
        required=False
    )
    api = forms.ModelChoiceField(
        label="API",
        queryset=CmtApi.objects.all(),
        required=False,
    )
    author__username__startswith = forms.CharField(label="Author", required=False)
    create_date__gte = forms.DateTimeField(
        label="开始时间",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "vDateField"
            }
        )
    )
    create_date__lte = forms.DateTimeField(
        label="截止时间",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "vDateField"
            }
        )
    )


class EditCaseForm(NewCaseForm):
    pass


class NewArrangeForm(forms.Form):
    description = forms.CharField(label="编排描述", max_length=32)
    service = forms.ModelChoiceField(
        label="所属服务",
        queryset=CmtService.objects.all(),
        help_text="所属服务"
    )
    active_flag = forms.BooleanField(label="是否有效", required=False)
    apis = forms.CharField(label="编排的API", widget=ArrangApiWidget(queryset=CmtApi.objects.all()))
    input = forms.CharField(label="入参", widget=SplitJSONWidget())
    output = forms.CharField(label="出参", widget=SplitJSONWidget())

    def populate(self, service_id):
        if service_id:
            self.fields["apis"].queryset = CmtApi.objects.filter(service_id=service_id)
        else:
            self.fields["apis"].queryset = CmtApi.objects.all()


class SearchArrangeForm(forms.Form):
    description__startswith = forms.CharField(label="Description", required=False)
    service = forms.ModelChoiceField(
        label="所属服务",
        queryset=CmtService.objects.all(),
        required=False,
        help_text="所属服务"
    )
    author__username__startswith = forms.CharField(label="Author", required=False)
    create_date__gte = forms.DateTimeField(
        label="开始时间",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "vDateField"
            }
        )
    )
    create_date__lte = forms.DateTimeField(
        label="截止时间",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "vDateField"
            }
        )
    )


class EditArrangeForm(NewArrangeForm):
    pass


class NewPublicDefForm(forms.Form):
    description = forms.CharField(label="API名称", max_length=32)
    service = forms.ModelChoiceField(
        label=CmtService,
        queryset=CmtService.objects.all(),
        help_text="所属服务"
    )
    active_flag = forms.BooleanField(label="是否有效", required=False)
    input = forms.CharField(label="入参", widget=SplitJSONWidget())
    output = forms.CharField(label="出参", widget=SplitJSONWidget())


class SearchPublicDefForm(forms.Form):
    description__startswith = forms.CharField(label="Description", required=False)
    service = forms.ModelChoiceField(
        label="Service",
        queryset=CmtService.objects.all(),
        required=False,
        help_text="所属服务"
    )
    author__username__startswith = forms.CharField(label="Author", required=False)
    create_date__gte = forms.DateTimeField(
        label="开始时间",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "vDateField"
            }
        )
    )
    create_date__lte = forms.DateTimeField(
        label="截止时间",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "vDateField"
            }
        )
    )


class EditPublicDefForm(NewPublicDefForm):
    pass


class NewPublicDataForm(forms.Form):
    description = forms.CharField(label="案例名称", max_length=32)
    service = forms.ModelChoiceField(
        label="所属服务",
        queryset=CmtService.objects.all(),
        help_text="所属服务"
    )
    active_flag = forms.BooleanField(label="是否有效", required=False)
    public_def = forms.ModelChoiceField(
        label="关联的公共请求定义",
        queryset=CmtPublicDef.objects.all(),
        required=False,
    )
    input = forms.CharField(label="入参", widget=SetDataWidget())
    output = forms.CharField(label="出参", widget=SetDataWidget())

    def populate(self, service_id):
        if service_id:
            self.fields["public_def"].queryset = CmtPublicDef.objects.filter(service_id=service_id)
        else:
            self.fields["public_def"].queryset = CmtPublicDef.objects.all()

class SearchPublicDataForm(forms.Form):
    description__startswith = forms.CharField(label="Description", required=False)
    service = forms.ModelChoiceField(
        label="所属服务",
        queryset=CmtService.objects.all(),
        required=False,
        help_text="所属服务"
    )
    public_def = forms.ModelChoiceField(
        label="关联的公共请求定义",
        queryset=CmtPublicDef.objects.all(),
        required=False,
    )
    author__username__startswith = forms.CharField(label="Author", required=False)
    create_date__gte = forms.DateTimeField(
        label="开始时间",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "vDateField"
            }
        )
    )
    create_date__lte = forms.DateTimeField(
        label="截止时间",
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "vDateField"
            }
        )
    )


class EditPublicDataForm(NewPublicDataForm):
    pass
