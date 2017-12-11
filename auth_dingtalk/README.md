# Auth Dingtalk
#### 基于钉钉扫码的odoo登录 \n
#### 使用前需要在钉钉管理员配置;将扫码跳转地址配置为---http://baseurl/web/action_login
#### 在钉钉后台获取到appid, appsecret,corpid, corpsecret配置到odoo配置文件；
#### 将模块放到odoo模块中安装；
#### 配置获取token认证信息定时任务，token两小时失效，所以两小时运行一次；
#### 对象：ir.config_parameter	
#### 方法：get_ding_token
#### 原login页面替换为扫码页面；原login页面在/web/login/debug

