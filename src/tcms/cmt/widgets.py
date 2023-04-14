# -*- coding: utf-8 -*-
import os

from django import get_version, forms
from django.forms import Widget
from django import utils
import copy
from distutils.version import StrictVersion

try:
    import simplejson as json
except ImportError:
    import json
if StrictVersion(get_version()) < StrictVersion('1.9.0'):
    from django.forms.util import flatatt
else:
    from django.forms.utils import flatatt


class SplitJSONWidget(forms.Widget):

    def __init__(self, attrs=None, options=('String', 'Map', 'List'), operation=None, sep='__', debug=False):
        self.operation = operation
        self.separator = sep
        self.debug = debug
        self.options = options
        Widget.__init__(self, attrs)

    def _as_text_field(self, name, key, value, level, is_sub=False):

        attrs = self.build_attrs(self.attrs, {"name": "%s%s%s" % (name, self.separator, key)})
        attrs['value'] = value
        attrs['id'] = attrs.get('name', None)

        ans = u"""字段名称：&nbsp;<input type="text" value="%s" placeholder="请输入字段名称" class="api_name"/>
            字段类型：&nbsp;<select%s > \n  
            <option value="" selected>--------请选择--------</option>\n""" % (key, flatatt(attrs))
        for option in self.options:
            if option == value:
                ans += u""" <option value="%s" selected>%s</option>\n""" % (option, option)
            else:
                ans += u""" <option value="%s">%s</option>\n""" % (option, option)
        ans += """</select> \n <img src="%s" class="%s increment_param" width="25px" height="25px">
        <img src="%s" class="%s decrement_param" width="25px" height="25px">""" % (
            os.path.join("/static", "images", "add.jpeg").replace("\\", "/"),
            "level_" + str(level),
            os.path.join("/static", "images", "delete.jpeg").replace("\\", "/"),
            "level_" + str(level))
        return ans

    def _to_build(self, name, json_obj, level):
        inputs = []
        if isinstance(json_obj, dict):
            title = name.rpartition(self.separator)[2]
            _l = []
            for key, value in json_obj.items():
                _l.extend(self._to_build("%s%s%s" % (name, self.separator, key), value, level + 1))
            info = [u"""<input type="button" value="添加字段" class="%s bottom_increment_param add_btn"> \n 
            <input type="hidden" value="%s" class="%s">""" % ("level" + str(level + 1), name, "button_next_hidden")]

            _l.extend(info)
            inputs.extend(_l)
        elif isinstance(json_obj, (str, int, float)):
            name, _, key = name.rpartition(self.separator)
            inputs.append(self._as_text_field(name, key, json_obj, level))
        elif json_obj is None:
            name, _, key = name.rpartition(self.separator)
            inputs.append(self._as_text_field(name, key, ''))
        return inputs

    def _prepare_as_ul(self, inputs):
        if inputs:
            result = ''
            for el in inputs:
                if isinstance(el, list):
                    result += '<li>'
                    result += '%s' % self._prepare_as_ul(el)
                    result += '</li>'
                else:
                    result += '<li>%s</li>' % el
            return result
        return ''

    def _to_pack_up(self, root_node, raw_data):
        result = {}
        for k, v in raw_data.items():
            if k.find(self.separator) != -1:
                apx, _, nk = k.rpartition(self.separator)
                if apx == root_node:
                    result.update({nk: v})
        return result

    def value_from_datadict(self, data, files, name):
        data_copy = copy.deepcopy(data)
        result = self._to_pack_up(name, data_copy)
        return json.dumps(result)

    def render(self, name, value, attrs=None):
        try:
            value = json.loads(value)
        except (TypeError, KeyError):
            pass
        inputs = self._to_build(name, value or {}, 0)
        result = self._prepare_as_ul(inputs)
        if self.debug:
            # render json as well
            source_data = u'<hr/>Source data: <br/>%s<hr/>' % str(value)
            result = '%s%s' % (result, source_data)
        return utils.safestring.mark_safe(result)


class SetDataWidget(forms.Widget):

    def __init__(self, attrs=None, sep='__', debug=False):
        self.separator = sep
        self.debug = debug
        Widget.__init__(self, attrs)

    def _as_text_field(self, name, key, value, level, is_sub=False):
        # key是由真正的key和字段类型使用'|'连接的
        key, _, type = key.rpartition('|')
        if key == '':
            key = type
        attrs = self.build_attrs(self.attrs, {"name": "%s%s%s" % (name, self.separator, key)})
        attrs['value'] = value
        attrs['id'] = attrs.get('name', None)
        if _ == '':
            ans = u""" <label for="%s">%s:</label> \n 
                    <input%s />""" % (attrs['id'], key, flatatt(attrs))
        else:
            ans = u""" <label for="%s">%s(%s):</label> \n 
                <input%s />""" % (attrs['id'], key, type, flatatt(attrs))
        return ans

    def _to_build(self, name, json_obj, level):
        inputs = []
        if isinstance(json_obj, dict):
            title = name.rpartition(self.separator)[2]
            _l = []
            for key, value in json_obj.items():
                _l.extend(self._to_build("%s%s%s" % (name, self.separator, key), value, level + 1))

            inputs.extend(_l)
        elif isinstance(json_obj, (str, int, float)):
            name, _, key = name.rpartition(self.separator)
            inputs.append(self._as_text_field(name, key, json_obj, level))
        elif json_obj is None:
            name, _, key = name.rpartition(self.separator)
            inputs.append(self._as_text_field(name, key, ''))

        return inputs

    def _prepare_as_ul(self, inputs):
        if inputs:
            result = ''
            for el in inputs:
                if isinstance(el, list):
                    result += '<li>'
                    result += '%s' % self._prepare_as_ul(el)
                    result += '</li>'
                else:
                    result += '<li>%s</li>' % el
            return result
        return ''

    def _to_pack_up(self, root_node, raw_data):
        result = {}
        for k, v in raw_data.items():
            if k.find(self.separator) != -1:
                apx, _, nk = k.rpartition(self.separator)
                if apx == root_node:
                    result.update({nk: v})
        return result

    def value_from_datadict(self, data, files, name):
        data_copy = copy.deepcopy(data)
        result = self._to_pack_up(name, data_copy)
        return json.dumps(result)

    def render(self, name, value, attrs=None):
        try:
            value = json.loads(value)
        except (TypeError, KeyError):
            pass
        inputs = self._to_build(name, value or {}, 0)
        result = self._prepare_as_ul(inputs)
        if self.debug:
            # render json as well
            source_data = u'<hr/>Source data: <br/>%s<hr/>' % str(value)
            result = '%s%s' % (result, source_data)
        return utils.safestring.mark_safe(result)


class ArrangApiWidget(forms.Widget):

    def __init__(self, queryset=None, sep1='__', sep2='___', debug=False):
        self.separator1 = sep1
        self.separator2 = sep2
        self.debug = debug
        self.queryset = queryset
        Widget.__init__(self)

    def _as_text_field(self, name, value):
        attrs = self.build_attrs(self.attrs, {"name": "%s" % name})
        attrs['value'] = value
        attrs['id'] = attrs.get('name', None)

        ans = u"""<select%s  class="api_selector"> \n  
                    <option value="" selected>--------请选择--------</option>\n""" % (flatatt(attrs))
        for api in self.queryset:
            if api.api_id == int(value):
                ans += u""" <option value="%s" selected>%s</option>\n""" % (api.api_id, api.description)
            else:
                ans += u""" <option value="%s" >%s</option>\n""" % (api.api_id, api.description)
        ans += """</select> \n <img src="%s" class="increment_api" width="25px" height="25px">
                <img src="%s" class="decrement_api" width="25px" height="25px">""" % (
            os.path.join("/static", "images", "add.jpeg").replace("\\", "/"),
            os.path.join("/static", "images", "delete.jpeg").replace("\\", "/"))
        return ans

    def _to_build(self, name, json_obj):
        result = """"""
        # 遍历出每个api进行设置
        for api in json_obj:
            result += """<li><br/>"""
            nameAttr = name + self.separator1 + str(api.get('pk'))
            result += self._as_text_field(nameAttr, api.get('pk'))
            # 设置Input
            if api.get('input') is not None:
                result += """<div style="margin-left: 3%" class="input_attr field_attr">
                            <span class="name summary strong">input:</span><br/>"""
                for fieldName, fieldAttrs in api.get('input').items():
                    inputName = nameAttr + self.separator2 + 'input' + self.separator2 + fieldName + self.separator2
                    result += """<div class="input_field_div"><label class="lab">%s:</label>
                            <input type="text" name="%s" value="%s" style="width: 470px" placeholder="请输入字段的引用...">
                            <input type="hidden" name="%s" value="%s">
                            <img src="%s" class="increment_input_field" width="15px" height="15px">
                            </div>""" % (fieldName, inputName + 'value', fieldAttrs.get("value"),
                                              inputName + 'attr_type', fieldAttrs.get('attr_type'),
                                         os.path.join("/static", "images", "add.jpeg").replace("\\", "/"))
                result += """</div>"""
            # 设置Output
            if api.get('output') is not None:
                result += """<div style="margin-left: 3%" class="output_attr field_attr">
                                        <span class="name summary strong">output:</span><br/>"""
                for fieldName, fieldAttrs in api.get('output').items():
                    outputName = nameAttr + self.separator2 + 'output' + self.separator2 + fieldName + self.separator2
                    isShare = 'checked' if fieldAttrs.get('to_share') == '1' else ''
                    isCheck = 'checked' if fieldAttrs.get('to_check') == '1' else ''
                    result += """<div class="output_field_div"><label class="lab" >%s:</label>
                            是否共享:<input type="checkbox" name="%s" class="output_to_share" %s>
                            是否检查:<input type="checkbox" name="%s" class="output_to_check" %s>
                            检查标准:<input type="text" name="%s" value="%s">
                            <input type="hidden" name="%s" value="%s">
                            <img src="%s" class="increment_output_field" width="15px" height="15px">
                            </div>
                            """ % (fieldName,
                                   outputName + 'to_share', isShare,
                                   outputName + 'to_check', isCheck,
                                   outputName + 'check_value', fieldAttrs.get('check_value'),
                                   outputName + 'attr_type', fieldAttrs.get('attr_type'),
                                   os.path.join("/static", "images", "add.jpeg").replace("\\", "/"))
                result += """</div>"""
                # 设置endpoint
                result += """<div class="api_endpoint_div"><input type="hidden" name="%s" value="%s"></div>""" % \
                          (nameAttr + self.separator2 + 'endpoint', api.get('endpoint'))
            result += """</li>"""
        # 设置最后的添加按钮
        result += """<li>
                        <input type="button" value="添加API" class="bottom_increment_api add_btn" style="width: %s"> \n
                        <input type="hidden" value="%s" class="%s"> </li>""" % ("25%", name, "button_next_hidden")
        return result

    def _to_pack_up(self, root_node, raw_data):
        print(">>>>>>>>>>>>_to_pack_up:  root_node:{} raw_data:{} ".format(root_node, raw_data))
        result = []

        # 给parent_node补充属性
        def _to_parse_key_left(parent_node, key_str, value):
            if key_str.find(self.separator2) != -1:
                cur_node, _, apx = key_str.partition(self.separator2)
                if parent_node.get(cur_node) is None:
                    parent_node[cur_node] = _to_parse_key_left({}, apx, value)
                else:
                    parent_node[cur_node] = _to_parse_key_left(parent_node[cur_node], apx, value)
                return parent_node
            else:
                # 转化复选框的值
                if key_str in ("to_share", "to_check") and value == "on":
                    value = "1"
                # 由于复选框没选，该字段就不上送，需要补一下
                if key_str == "check_value":
                    if parent_node.get("to_share") is None:
                        parent_node["to_share"] = "0"
                    if parent_node.get("to_check") is None:
                        parent_node["to_check"] = "0"
                parent_node[key_str] = value
                return parent_node

        def getApiObject(arr, api_id):
            api_item = arr[1]
            if root_node == arr[0] and len(arr) == 2 and api_item not in api_set:
                api_object = {"pk": api_id}
                result.append(api_object)
                api_set.add(api_item)
            else:
                api_object = result[-1]
            return api_object

        api_set = set()
        for k, v in raw_data.items():
            # to transform value from list to string
            if k.find(self.separator1) != -1:
                v = v[0] if isinstance(v, list) and len(v) == 1 else v
                spiltArr = k.split(self.separator1)
                cmt_api = getApiObject(spiltArr, v)
                if k.find(self.separator2) != -1:
                    _, _, apx = k.partition(self.separator2)
                    _to_parse_key_left(cmt_api, apx, v)
        return result

    def value_from_datadict(self, data, files, name):
        print(">>>>上送数据：{}".format(data))
        result = self._to_pack_up(name, data)
        return json.dumps(result)

    def render(self, name, value, attrs=None):
        print(">>>>>name:{} >value:{}".format(name, value))
        try:
            value = json.loads(value)
        except (TypeError, KeyError):
            pass
        result = self._to_build(name, value or [])
        return utils.safestring.mark_safe(result)

# class ArrangApiWidget_bak(forms.Widget):
#
#     def __init__(self, queryset=None, sep='__', debug=False):
#         self.separator = sep
#         self.debug = debug
#         self.queryset = queryset
#         Widget.__init__(self)
#
#     def _as_text_field(self, name, value, level, is_sub=False):
#         attrs = self.build_attrs(self.attrs, {"name": "%s" % name})
#         attrs['value'] = value
#         attrs['id'] = attrs.get('name', None)
#
#         ans = u"""<select%s  class="api_selector"> \n
#                     <option value="" selected>--------请选择--------</option>\n""" % (flatatt(attrs))
#         for api in self.queryset:
#             if api.api_id == int(value):
#                 ans += u""" <option value="%s" selected>%s</option>\n""" % (api.api_id, api.description)
#             else:
#                 ans += u""" <option value="%s" >%s</option>\n""" % (api.api_id, api.description)
#         ans += """</select> \n <img src="%s" class="%s increment_api" width="25px" height="25px">
#                 <img src="%s" class="%s decrement_api" width="25px" height="25px">""" % (
#             os.path.join("/static", "images", "add.jpeg").replace("\\", "/"),
#             "level_" + str(level),
#             os.path.join("/static", "images", "delete.jpeg").replace("\\", "/"),
#             "level_" + str(level))
#         return ans
#
#     def _to_build(self, name, json_obj, level):
#         inputs = []
#         # if isinstance(json_obj, dict):
#         #     title = name.rpartition(self.separator)[2]
#         #     _l = []
#         #     for key, value in json_obj.items():
#         #         _l.extend(self._to_build("%s%s%s" % (name, self.separator, key), value, level+1))
#         #     info = [u"""<input type="button" value="添加API" class="%s bottom_increment_api add_btn"> \n
#         #                 <input type="hidden" value="%s" class="%s">""" % (
#         #     "level" + str(level + 1), name, "button_next_hidden")]
#         #     _l.extend(info)
#         #     inputs.extend(_l)
#         if isinstance(json_obj, list):
#             title = name.rpartition(self.separator)[2]
#             _l = []
#             index = 0
#             for elem in json_obj:
#                 print(">>>>>index:{} >elem:{}".format(index, elem))
#                 _l.extend(self._to_build("%s%s%s" % (name, self.separator, index), elem, level + 1))
#                 index += 1
#             info = [u"""<input type="button" value="添加API" class="%s bottom_increment_api add_btn" style="width: %s"> \n
#                         <input type="hidden" value="%s" class="%s">""" % (
#                 "level" + str(level + 1), "25%", name, "button_next_hidden")]
#             _l.extend(info)
#             inputs.extend(_l)
#         elif isinstance(json_obj, (str, int, float)):
#             # name, _, key = name.rpartition(self.separator)
#             inputs.append(self._as_text_field(name, json_obj, level))
#         elif json_obj is None:
#             name, _, key = name.rpartition(self.separator)
#             inputs.append(self._as_text_field(name, key, ''))
#         return inputs
#
#     def _prepare_as_ul(self, inputs):
#         if inputs:
#             result = ''
#             for el in inputs:
#                 if isinstance(el, list):
#                     result += '<li>'
#                     result += '%s' % self._prepare_as_ul(el)
#                     result += '</li>'
#                 else:
#                     result += '<li>%s</li>' % el
#             return result
#         return ''
#
#     def _to_pack_up(self, root_node, raw_data):
#         # result = {}
#         # for k, v in raw_data.items():
#         #     if k.find(self.separator) != -1:
#         #         apx, _, nk = k.rpartition(self.separator)
#         #         if apx == root_node:
#         #             result.update({nk: v})
#         result = []
#         for k, v in raw_data.items():
#             if k.find(self.separator) != -1:
#                 apx, _, nk = k.rpartition(self.separator)
#                 if apx == root_node:
#                     result.append(v)
#         return result
#
#     def value_from_datadict(self, data, files, name):
#         data_copy = copy.deepcopy(data)
#         result = self._to_pack_up(name, data_copy)
#         return json.dumps(result)
#
#     def render(self, name, value, attrs=None):
#         print(">>>>>name:{} >value:{}".format(name, value))
#         try:
#             value = json.loads(value)
#         except (TypeError, KeyError):
#             pass
#         inputs = self._to_build(name, value or [], 0)
#         result = self._prepare_as_ul(inputs)
#         if self.debug:
#             # render json as well
#             source_data = u'<hr/>Source data: <br/>%s<hr/>' % str(value)
#             result = '%s%s' % (result, source_data)
#         return utils.safestring.mark_safe(result)
