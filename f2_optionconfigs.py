import json
import codecs
import os.path as osp

default_config = {
    "选择同步设备":{
        "OBS 录像": True,
        "USV 超声": True,
        "小显微镜": True,
        "ArControl": True
    },
    "启用快捷键控制": True,
    "启用socket server控制": True,
    "启用倒计时": True,
    "倒计时秒数": 15*60+1,
    "启用微信推送": False,
    "微信推送密钥": [
        "<corp_id>", #corp_id
        "<secret>", #secret key
        "<agent_id>" #agent_id
    ],
    "微信推送中继代理服务器":{
        "http_proxy": None,
        "https_proxy": None
    },
    "微信推送内容": "[行为间2] 结束录制",
}

filenames = [osp.join(osp.dirname(__file__), '.f2_config'), #high priority first
            osp.join(osp.expanduser("~"), '.f2_config')]   #low priority last

filereal = None

def load_config():
    global filereal
    if filereal is None:
        for filename in filenames:
            if osp.exists(filename):
                filereal = filename
                break
        else:
            filereal = filenames[-1]

    if osp.exists(filereal):
        with codecs.open(filereal, 'r', encoding='utf-8') as f:
            config_tmp = json.load(f)
            config = default_config.copy()
            config.update(config_tmp)  # update with config file values, but keep default values for keys not in config file.  (This
    
    else:
        config = default_config
        with codecs.open(filereal, 'w', encoding='utf-8') as f: 	# write defaults to file to restore on next run
            json.dump(default_config, f, indent=2, ensure_ascii=False) 	# save defaults to file

    return config


def save_config(config):
    if filereal is None:
        load_config()

    with codecs.open(filereal, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)