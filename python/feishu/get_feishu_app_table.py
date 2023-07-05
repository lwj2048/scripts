# -*- coding: UTF-8 -*-
import logging
from larksuiteoapi import Config, AppSettings,Logger, DefaultLogger, MemoryStore, LEVEL_DEBUG, LEVEL_INFO, LEVEL_WARN,\
LEVEL_ERROR,DOMAIN_FEISHU, DOMAIN_LARK_SUITE
from larksuiteoapi import ACCESS_TOKEN_TYPE_APP, ACCESS_TOKEN_TYPE_TENANT, ACCESS_TOKEN_TYPE_USER
from larksuiteoapi.api import Request


# 参数说明：
# AppID、AppSecret: "开发者后台" -> "凭证与基础信息" -> 应用凭证（App ID、App Secret）
# VerificationToken、EncryptKey："开发者后台" -> "事件订阅" -> 事件订阅（Verification Token、Encrypt Key）（可以不添加）
# HelpDeskID、HelpDeskToken：服务台设置中心 -> ID、令牌  （可以不添加）
app_settings = Config.new_internal_app_settings(app_id="cli_a429411924fd900b", app_secret="jmPEXSMQBlMrfsssddf80msrf7PoVDUfUwx",
                                                verification_token="tGc06kACKuLGFWmHoFxdewfeaSMzovK6kd", encrypt_key="iT8OFDciCsj3drfrcfVAdScuxISEeupfn",
                                                help_desk_id="7252164345214451716", help_desk_token="ht-585796c0-affe-1adc-df40-b7028179ee18")


conf = Config(DOMAIN_FEISHU, app_settings, logger=DefaultLogger(), log_level=LEVEL_ERROR, store=MemoryStore())
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

# 参数说明：
# app_token https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/get_node  返回的obj_token就是的app_token，如果表格不在知识库就不用通过此步骤获取app_token
# table_id  多维表格的url中获取
# view_id   多维表格的url中获取

app_token = "CXfgbsYTqaM4KUsyIdJcjrNNnFf"
table_id = "tbldgbEUA72j5jQQ"
view_id = "vewXxBNTOK"

http_path = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records?page_size=20&view_id={view_id}"
request_body = None
req = Request(http_path, "GET", ACCESS_TOKEN_TYPE_TENANT, request_body, request_opts=None)

resp = req.do(conf)

print(resp)