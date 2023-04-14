api_create_on_load = function () {
    apiCommon();
    jQ('.js-cancel-button').on('click', function () {
        window.history.back();
    });
};

api_edit_on_load = function () {
    apiCommon();
    jQ('.js-back-button').on('click', function () {
        window.location.assign(this.dataset.actionUrl);
    });
};

function apiCommon() {
    jQ(document).on("change", "#id_api_type", function () {
        if (jQ(this).val() == '1') {
            jQ(".normal-api-elem").show();
        } else {
            jQ(".normal-api-elem").hide();
        }
    });
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