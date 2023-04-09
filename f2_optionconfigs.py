import json
import codecs
import os.path as osp

default_config = {
    "选择同步设备":{
        "OBS 录像": True,
        "USV 超声": True,
        "小显微镜": True
    },
    "启用快捷键控制": True,
    "启用socket server控制": True,
    "启用倒计时": True
}

filename = osp.join(osp.dirname(__file__), '.f2_optionconfigs.json')


def load_config():
    if osp.exists(filename):
        with codecs.open(filename, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = default_config
        with codecs.open(filename, 'w', encoding='utf-8') as f: 	# write defaults to file to restore on next run
            json.dump(default_config, f, indent=2, ensure_ascii=False) 	# save defaults to file

    return config


def save_config(config):
    with codecs.open(filename, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)