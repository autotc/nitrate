public_def_create_on_load = function () {
    publicDefCommon();
    jQ('.js-cancel-button').on('click', function () {
        window.history.back();
    });
};

public_def_edit_on_load = function () {
    publicDefCommon();
    jQ('.js-back-button').on('click', function () {
        window.location.assign(this.dataset.actionUrl);
    });
};

function publicDefCommon() {
    //设置输入 输出使用
    jQ(document).on("blur", ".api_name", function () {
        let value = jQ(this).val();
        const next = jQ(this).next();
        let old_attr = next.attr("name");
        let newVal = getNewAttrVal(old_attr, value);
        next.attr("name", newVal)
    });
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