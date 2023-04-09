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
            config = json.load(f)
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
