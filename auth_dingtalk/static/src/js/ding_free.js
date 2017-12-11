/**
 * Created by heqiauto on 17/10/23.
 */
var _config = 0;

    document.getElementsByClassName('btn-erp')[0].onclick = function(){
        var _config1,agentId;
        $.ajax({
            url:'/hq/get_ding_sign_config',
            type:"GET",
            dataType:'json',
            success: function (res) {
                _config = false;
                _config1 = res;
                if(_config1){
                    DingTalkPC.config({
                        agentId : _config1.agentId,
                        corpId : _config1.corpId,
                        timeStamp : _config1.timeStamp,
                        nonceStr : _config1.nonceStr,
                        signature : _config1.signature,
                        jsApiList : [
                            'runtime.permission.requestAuthCode',
                            'runtime.info',
                            'biz.contact.choose',
                            'device.notification.confirm',
                            'device.notification.alert',
                            'device.notification.prompt',
                            'biz.util.openLink',
                            'biz.user.get'
                        ]
                    });
                    DingTalkPC.runtime.permission.requestAuthCode({
                        corpId : _config1.corpId,
                        onSuccess : function(info) {
                            console.log('authcode: ' + info.code);

                            DingTalkPC.biz.util.openLink({
                                url : _config1.url + '?ding_app_code=' + info.code,
                                onSuccess : function(result){
                                    console.log('click event')
                                },
                                onFail : function(err){
                                    console.log(JSON.stringify(err));
                                }
                            })
                        },
                        onFail : function(err) {
                            console.log('fail: ' + JSON.stringify(err));
                        }
                    });
                }
            },
            error: function (error) {
                console.log(error);
            }
        })
    };
    if(_config){
        // document.getElementsByClassName('dingding-show')[0].style.display = 'block';
        // document.getElementsByClassName('login_container')[0].style.display = 'none';
        console.log(_config);
        DingTalkPC.config({//对参数进行验证
            agentId : _config.agentId,
            corpId : _config.corpId,
            timeStamp : _config.timeStamp,
            nonceStr : _config.nonceStr,
            signature : _config.signature,
            jsApiList : [//需要调用的借口列表
                'runtime.permission.requestAuthCode',
                'runtime.info',
                'biz.contact.choose',
                'device.notification.confirm',
                'device.notification.alert',
                'device.notification.prompt',
                'biz.util.openLink',
                'biz.user.get'
            ]
        });
        DingTalkPC.ready(function(){
            DingTalkPC.runtime.permission.requestAuthCode({
                corpId : _config.corpId,
                onSuccess : function(info) {
                    console.log('authcode: ' + info.code);

                    DingTalkPC.biz.util.openLink({
                        url : _config.url + '?ding_app_code=' + info.code,
                        onSuccess : function(result){
                            console.log('dingding')
                        },
                        onFail : function(err){
                            console.log(JSON.stringify(err));
                        }
                    })
                },
                onFail : function(err) {
                    console.log('fail: ' + JSON.stringify(err));
                }
            });
        });
        DingTalkPC.error(function(err){
            console.log('DDTalkPC error: ' + JSON.stringify(err));
        })
    }