//获取apiList并，设置到下拉列表中
function getApiList(selectHtml, api_type, service_id) {
    getRequest({
        url: '/cmt/management/getApiList/',
        data: {'api_type': api_type, 'service_id': service_id},
        traditional: true,
        success: function (data) {
            setApiFieldChoices(
                selectHtml,
                data,
                true
            );
        },
        errorMessage: 'Get ApiList failed.',
    });
}

//获取getArrangeList并设置到下拉列表中
function getArrangeList(selectHtml, service_id) {
    getRequest({
        url: '/cmt/management/getArrangeList/',
        data: {'service_id': service_id},
        traditional: true,
        success: function (data) {
            setApiFieldChoices(
                selectHtml,
                data,
                true
            );
        },
        errorMessage: 'Get ArrangeList failed.',
    });
}

//获取getPublicDefList并设置到下拉列表中
function getPublicDefList(selectHtml, service_id) {
    getRequest({
        url: '/cmt/management/getPublicDefList/',
        data: {'service_id': service_id},
        traditional: true,
        success: function (data) {
            setApiFieldChoices(
                selectHtml,
                data,
                true
            );
        },
        errorMessage: 'Get ArrangeList failed.',
    });
}

function getPublicDataList(selectHtml, service_id) {
    getRequest({
        url: '/cmt/management/getPublicDataList/',
        data: {'service_id': service_id},
        traditional: true,
        sync: true,
        success: function (data) {
            setApiFieldChoices(
                selectHtml,
                data,
                true
            );
        },
        errorMessage: 'Get PublicDataList failed.',
    });
}

//获取某个api的输入输出，并添加到对应位置
function getApiDetail(inputHtml, passHtml, api_id) {
    getRequest({
        url: '/cmt/management/getApiDetail/',
        data: {'api_id': api_id},
        traditional: true,
        success: function (data) {
            setInputOrOutput(
                inputHtml,
                passHtml,
                data,
                'pass_rule__');
        },
        errorMessage: 'Get Api Info failed.',
    });
}

//获取某个api的输入输出，并添加到对应位置
function getArrangeInputAndOutput(inputHtml, passHtml, arrange_id) {
    getRequest({
        url: '/cmt/management/getArrangeInputAndOutPut/',
        data: {'arrange_id': arrange_id},
        traditional: true,
        success: function (data) {
            setInputOrOutput(
                inputHtml,
                passHtml,
                data,
                'pass_rule__');
        },
        errorMessage: 'Get Arrange Info failed.',
    });
}

//获取公共请求定义的输入输出，并添加到对应位置
function getPublicDataInputAndOutput(inputHtml, outputHtml, public_def_id) {
    getRequest({
        url: '/cmt/management/getPublicDefInputAndOutPut/',
        data: {'public_def_id': public_def_id},
        traditional: true,
        success: function (data) {
            setInputOrOutput(
                inputHtml,
                outputHtml,
                data,
                'output__');
        },
        errorMessage: 'Get Public Def Info failed.',
    });
}

//输入输出具体字段，添加到html中
function setInputOrOutput(opHtml, passHtml, data, out_prefix) {
    let html = "";
    let elem_id = 'input__'
    jQ.each(data.input, function (k, v) {
        elem_id = 'input__' + k;
        html += "<li>" +
            "<label for='" + elem_id + "'>" + k + "(" + v + "):</label> \n" +
            "<input id='" + elem_id + "' name='" + elem_id + "' style='width: 300px' value>" +
            "</li>\n";
    })
    opHtml.append(html);

    html = "";
    elem_id = out_prefix
    jQ.each(data.output, function (k, v) {
        elem_id = out_prefix + k;
        html += "<li>" +
            "<label for='" + elem_id + "'>" + k + "(" + v + "):</label> \n" +
            "<input id='" + elem_id + "' name='" + elem_id + "' style='width: 300px' value>" +
            "</li>\n";
    })
    passHtml.append(html)
}

//查询Api信息
function selectApiList() {
    getRequest({
        url: '/cmt/management/getApiList/',
        data: {'api_type': 1, 'service_id': service_id},
        traditional: true,
        sync: true,
        success: function (data) {
            api_list = data;
        },
        errorMessage: 'Get api_list failed.',
    });
}

//获取某个api的输入输出，并添加到对应位置
function findApiDataAndSetMapping(inputDom, outputDom, endpointDom, api_id, api_name) {
    getRequest({
        url: '/cmt/management/getApiDetail/',
        data: {'api_id': api_id},
        traditional: true,
        success: function (data) {
            setApiMappingInfo(
                inputDom,
                outputDom,
                endpointDom,
                data,
                api_name);
        },
        errorMessage: 'Get Api Info failed.',
    });
}
function setApiMappingInfo(inputDom, outputDom, endpointDom, data, api_name) {
    let inputHtml = "<span class='name summary strong'>input:</span><br/>";
    let sep = '___';
    let inputName = '';
    let add_img_url = "/static/images/add.jpeg";
    jQ.each(data.input, function (paramName, param_type) {
        inputName = api_name + sep + 'input' + sep + paramName + sep;
        inputHtml += "<div class='input_field_div'><label class='lab'>"+paramName+":</label>\n" +
                    "<input type='text' name='"+inputName+'value'+"' value='' style='width: 470px' placeholder='请输入字段的引用...'>\n" +
                    "<input type='hidden' name='"+inputName+'attr_type'+"' value='"+param_type+"'>\n" +
                    "<img src='" + add_img_url + "' class='increment_input_field' width='15px' height='15px'>" +
                    "</div>"
    });

    let outputHtml = "<span class='name summary strong'>output:</span><br/>";
    let outputName = '';
    jQ.each(data.output, function (paramName, param_type) {
        outputName = api_name + sep + 'output' + sep + paramName + sep;
        outputHtml += "<div class='output_field_div'><label class='lab' >"+paramName+":</label>" +
                    "是否共享:<input type='checkbox' name='"+outputName + 'to_share'+"' class='output_to_share'>"+
                    "是否检查:<input type='checkbox' name='"+outputName + 'to_check'+"' class='output_to_check'>"+
                    "检查标准:<input type='text' name='"+outputName + 'check_value'+"' value=''>" +
                    "<input type='hidden' name='"+outputName+'attr_type'+"' value='"+param_type+"'>"+
                    "<img src='" + add_img_url + "' class='increment_output_field' width='15px' height='15px'>" +
                    "</div>";
    });
    let endpointHtml = "<input type='hidden' name='"+api_name+'endpoint'+"' value='"+ data.endpoint+"'>"
    inputDom.append(inputHtml);
    outputDom.append(outputHtml);
    endpointDom.append(endpointHtml);
    // outputDom.after(endpointHtml);
}

//组装Api的html
function assembleApiHtml(new_val, data) {
    let add_img_url = "/static/images/add.jpeg";
    let del_img_url = "/static/images/delete.jpeg";
    let html = "";
    html += "<li>" +
        "<select id='" + new_val + "' name='" + new_val + "' value='' class='api_selector'>" +
        "<option value='' selected>--------请选择--------</option>";
    jQ.each(data, function (index, elem) {
        html += "<option value='" + elem[0] + "'>" + elem[1] + "</option> \n";
    })
    html += "</select> \n" +
        "<img src='" + add_img_url + "' class='level1 increment_api' width='25px' height='25px'> \n" +
        "<img src='" + del_img_url + "' class='level1 decrement_api' width='25px' height='25px'> \n" +
        "<div style='margin-left: 3%' class='input_attr field_attr'></div>" +
        "<div style='margin-left: 3%' class='output_attr field_attr'></div>" +
        "<div style='margin-left: 3%' class='api_endpoint_div field_attr'></div>" +
        "</li>";
    return html;
}

//计算添加到html中的元素的id
function getNewAttrVal(old_attr, value) {
    const array = old_attr.split("__");
    let new_attr = "";
    for (let i = 0; i < array.length - 1; i++) {
        new_attr += array[i] + "__"
    }
    new_attr += value;
    return new_attr;
}

//设置下拉列表
function setApiFieldChoices(elemSelect, values, addBlankOption) {
    elemSelect.find("option").remove();
    if (addBlankOption) {
        elemSelect.append("<option value=''>--------请选择--------</option>");
    }
    values.forEach(function (item) {
        let optionValue = item[0], optionText = item[1];
        elemSelect.append("<option value='" + optionValue + "'>" + optionText + "</option>");
    });
}

//在某个dom,后面添加元素
function generateDomInBack(pre_dom) {
    let origin_name = pre_dom.find("select:first").attr("name")
    let myID = "param" + new Date().getTime();
    let new_val = getNewAttrVal(origin_name, myID)
    pre_dom.after(assembleFieldHtml(new_val))
}

//在某个dom,前面添加元素
function generateDomInBefore(back_dom, filedName, fieldType) {
    let prefix = back_dom.next().val();
    let myID = filedName == null || filedName == undefined ? "autoGenerateParam" : filedName;
    let new_val = prefix + "__" + myID
    back_dom.parent().before(assembleFieldHtml(new_val, filedName, fieldType))
}

//组装输入输出类型的html
function assembleFieldHtml(new_val, fieldName, fieldType) {
    let add_img_url = "/static/images/add.jpeg"
    let del_img_url = "/static/images/delete.jpeg"
    if(fieldName == null || fieldName == undefined) fieldName = '';
    if(fieldType == null || fieldType == undefined) fieldType = '';
    let html = "";
    html += "<li>" +
        "字段名称：&nbsp;<input type='text' value='"+fieldName+"' placeholder='请输入字段名称' class='api_name'/>\n" +
        "字段类型：&nbsp;<select id='" + new_val + "' name='" + new_val + "' value='"+fieldType+"' >" +
        "<option value='' "+isSelected('',fieldType)+">--------请选择--------</option>" +
        // "<option value='__PUBLIC_RESPONSE_DEFS__'>__PUBLIC_RESPONSE_DEFS__</option>"+
        "<option value='String' "+isSelected('String',fieldType)+">String</option>" +
        "<option value='Map' "+isSelected('Map',fieldType)+">Map</option>" +
        "<option value='List' "+isSelected('List',fieldType)+">List</option>" +
        "</select> \n" +
        "<img src='" + add_img_url + "' class='level1 increment_param' width='25px' height='25px'> \n" +
        "<img src='" + del_img_url + "' class='level1 decrement_param' width='25px' height='25px'> \n" +
        "</li>";
    return html;
}
function isSelected(value, compVal) {
    return value === compVal ? 'selected' : '';
}

//获取公共接口以及常规的三个，并设置到下拉列表中
function getApiFiledType(selectHtml) {
    getRequest({
        url: '/cmt/management/getApiField/',
        data: {},
        traditional: true,
        success: function (data) {
            setApiFieldChoices(
                selectHtml,
                data,
                true
            );
        },
        errorMessage: 'Update FieldType failed.',
    });
}
