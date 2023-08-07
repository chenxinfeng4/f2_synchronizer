#%%
import logging


logger = logging.getLogger("XX科技公司")
logger.setLevel(logging.DEBUG)
# 第二步：定义处理器。控制台和文本输出两种方式
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler("D:/f2_sync.log",mode='a',encoding='utf-8')
# 第三步：设置的不同的输入格式
console_fmt = "%(asctime)s %(message)s"
file_fmt = "%(asctime)s %(message)s"
# 第三步：格式
fmt1 = logging.Formatter(fmt=console_fmt)
fmt2 = logging.Formatter(fmt=file_fmt)
# 第四步:把格式传给处理器
console_handler.setFormatter(fmt1)
file_handler.setFormatter(fmt2)
# 第五步:把处理器传个日志器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

logprint = logger.info
