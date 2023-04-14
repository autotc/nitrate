case_create_on_load = function () {
    caseCommon();
    jQ('.js-cancel-button').on('click', function () {
        window.history.back();
    });
};

case_edit_on_load = function () {
    caseCommon();
    jQ('.js-back-button').on('click', function () {
        window.location.assign(this.dataset.actionUrl);
    });
};

function caseCommon() {
    // 归属服务变化，需要重新设置案例关联类型,并清空input和pass_rule
    jQ("#id_service").on('change', function () {
        jQ("#id_rel_type").val('');
        jQ("#id_public_request").empty();
        jQ("#id_api").empty();
        jQ("#id_arrange").empty();
        jQ("#case_input").empty();
        jQ("#pass_rule").empty();
        getPublicDataList(jQ("#id_public_request"), jQ(this).val())
    })
    // 案例关联类型变化，需要重新加载API或ARR,并清空input和pass_rule
    jQ("#id_rel_type").on("change", function () {
        jQ("#case_input").empty();
        jQ("#pass_rule").empty();
        if (jQ(this).val() == '1') {
            jQ("#id_api").parents("tr:first").show();
            jQ("#id_arrange").parents("tr:first").hide();
            let service_id = jQ("#id_service").val();
            getApiList(jQ("#id_api"), 1, service_id)
        } else {
            jQ("#id_api").parents("tr:first").hide();
            jQ("#id_arrange").parents("tr:first").show();
            jQ("#id_api").empty();
            let service_id = jQ("#id_service").val();
            getArrangeList(jQ("#id_arrange"), service_id)
        }
    });
    //根据api设置input和pass_rule
    jQ("#id_api").on("change", function () {
        let api_id = jQ(this).val();
        jQ("#case_input").empty();
        jQ("#pass_rule").empty();
        getApiDetail(jQ("#case_input"), jQ("#pass_rule"), api_id)
    });
    //根据arrange设置input和pass_rule
    jQ("#id_arrange").on("change", function () {
        let arrange_id = jQ(this).val();
        jQ("#case_input").empty();
        jQ("#pass_rule").empty();
        getArrangeInputAndOutput(jQ("#case_input"), jQ("#pass_rule"), arrange_id)
    });
}