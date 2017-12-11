var prot = window.location.protocol;
var host = window.location.host;

function get_decode_url() {
    var url_target = '';
    $.ajax({
        async: false,
        url: "/hq/get_url",
        data: {"old_url": prot + "//" + host},
        success: function (data) {
            url_target = data.encode_url;
        },
        dataType: "json"
    });
    return url_target
}

var url = get_decode_url();
var qrcodeUrl = 'https://login.dingtalk.com/login/qrcode.htm?goto=' + url;
var obj = DDLogin({
    id: "login_container",
    goto: url,
    style: "",
    href: "",
    width: "200px",
    height: "200px"
});

function getUrlParam(name, url) {

    if (url.indexOf("?") == -1 || url.indexOf(name + '=') == -1) {
        return '';
    }
    var queryString = url.substring(url.indexOf("?") + 1);
    if (queryString.indexOf('#') > -1) {
        queryString = queryString.substring(0, queryString.indexOf('#'));
    }
    ;
    var parameters = queryString.split("&");
    var pos, paraName, paraValue;
    for (var i = 0; i < parameters.length; i++) {
        pos = parameters[i].indexOf('=');
        if (pos == -1) {
            continue;
        }
        paraName = parameters[i].substring(0, pos);
        paraValue = parameters[i].substring(pos + 1);
        if (paraName == name) {
            return decodeURIComponent(paraValue.replace("+", " "));
        }
    }
    return '';
}

var hanndleMessage = function (event) {
    var loginTmpCode = event.data;
    var origin = event.origin;
    window.location.href = getUrlParam("goto", qrcodeUrl) + "&loginTmpCode=" + loginTmpCode;
};
if (typeof window.addEventListener != 'undefined') {
    window.addEventListener('message', hanndleMessage, false);
} else if (typeof window.attachEvent != 'undefined') {
    window.attachEvent('onmessage', hanndleMessage);
}

