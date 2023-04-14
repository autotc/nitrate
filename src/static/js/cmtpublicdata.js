public_data_create_on_load = function () {
    publicDataCommon();
    jQ('.js-cancel-button').on('click', function () {
        window.history.back();
    });
};

public_data_edit_on_load = function () {
    publicDataCommon();
    jQ('.js-back-button').on('click', function () {
        window.location.assign(this.dataset.actionUrl);
    });
};
function publicDataCommon() {
    // 归属服务变化,需要重新设置公共请求的定义
    jQ("#id_service").on('change', function () {
        jQ("#id_public_def").empty();
        jQ("#public_data_input").empty();
        jQ("#public_data_output").empty();
        getPublicDefList(jQ("#id_public_def"), jQ(this).val());
    })
    // 公共请求定义变化，需要重置输入与输出
    jQ("#id_public_def").on("change", function () {
        jQ("#public_data_input").empty();
        jQ("#public_data_output").empty();
        let public_def_id = jQ(this).val();
        getPublicDataInputAndOutput(jQ("#public_data_input"), jQ("#public_data_output"), public_def_id)
    });
}