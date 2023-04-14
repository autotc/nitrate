arrange_create_on_load = function () {
    arrangeCommon();
    jQ('.js-cancel-button').on('click', function () {
        window.history.back();
    });
};

arrange_edit_on_load = function () {
    arrangeCommon();
    jQ('.js-back-button').on('click', function () {
        window.location.assign(this.dataset.actionUrl);
    });
};

function arrangeCommon() {
    //服务变化后，修改api的下拉列表
    jQ("#id_service").on('change', function () {
        service_id = jQ(this).val();
        selectApiList();

        jQ(".api_selector").empty();
        let options_html = "";
        jQ.each(api_list, function (index, elem) {
            options_html += "<option value='" + elem[0] + "'>" + elem[1] + "</option> \n";
        })
        jQ(".api_selector").append(options_html);
    })
    //增加api
    jQ(document).on("click", ".bottom_increment_api", function () {
        let service_id = jQ("#id_service").val();
        let myID = "param" + new Date().getTime()
        jQ(this).parent().before(assembleApiHtml(jQ(this).next().val() + '__' + myID, api_list))
    });
    //行级增加api
    jQ(document).on("click", ".increment_api", function () {
        let up_dom = jQ(this).parent();
        let origin_name = up_dom.find("select:first").attr("name")
        let myID = "param" + new Date().getTime();
        let new_val = getNewAttrVal(origin_name, myID)
        up_dom.after(assembleApiHtml(new_val, api_list))
    });
    //行级删除api
    jQ(document).on("click", ".decrement_api", function () {
        jQ(this).parent().remove();
    });
    //选择api之后，修改对应的输入输出
    jQ(document).on("change", ".api_selector", function () {
        let api_id = jQ(this).val();
        let api_name = jQ(this).attr('name');
        let inputDom = jQ(this).nextAll(".input_attr")
        let outputDom = jQ(this).nextAll(".output_attr")
        let endpointDom = jQ(this).nextAll(".api_endpoint_div")
        inputDom.empty();
        outputDom.empty();
        endpointDom.empty();
        findApiDataAndSetMapping(inputDom, outputDom, endpointDom, api_id, api_name);
    })
    //将api的输入字段增加到编排的输入
    jQ(document).on("click", ".increment_input_field", function () {
        let fieldName = jQ(this).parent().find("label:first").text();
        fieldName = fieldName.substring(0, fieldName.length-1);
        let fieldType = jQ(this).prev().val();
        generateDomInBefore(jQ(".bottom_increment_param").eq(0), fieldName, fieldType)
        jQ(this).parent().find("input[type='text']:first").val("input."+fieldName);
    });
    //将api的输出字段增加到编排的输出
    jQ(document).on("click", ".increment_output_field", function () {
        let fieldName = jQ(this).parent().find("label:first").text();
        fieldName = fieldName.substring(0, fieldName.length-1);
        let fieldType = jQ(this).prev().val();
        generateDomInBefore(jQ(".bottom_increment_param").eq(1), fieldName, fieldType)
    });

    //设置整个编排 输入/输出使用
    jQ(document).on("blur", ".api_name", function () {
        let value = jQ(this).val();
        const next = jQ(this).next();
        let old_attr = next.attr("name");
        let newVal = getNewAttrVal(old_attr, value);
        next.attr("name", newVal)
        if (value == "$include") {
            getApiFiledType(next);
        }
    });
    //设置整个编排 输入/输出使用
    jQ(document).on("click", ".bottom_increment_param", function () {
        generateDomInBefore(jQ(this))
    });
    jQ(document).on("click", ".increment_param", function () {
        generateDomInBack(jQ(this).parent())
    });
    jQ(document).on("click", ".decrement_param", function () {
        jQ(this).parent().remove();
    });
}