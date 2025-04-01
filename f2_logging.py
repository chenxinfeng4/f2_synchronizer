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



#%%
# 第一步：创建日志器
logger = logging.getLogger("CIBR2")
logger.setLevel(logging.INFO)  # 设置日志级别为DEBUG

# 第二步：定义处理器，控制台和文本输出两种方式
console_handler = logging.StreamHandler()  # 控制台处理器
file_handler = logging.FileHandler("D:/f2_sync_start.log", mode='a', encoding='utf-8')  # 文件处理器，追加模式

# 第三步：设置不同的日志格式
file_fmt = "%(asctime)s.%(msecs)03d: %(message)s"  # 文件日志格式

# 第四步：创建格式器
fmt2 = logging.Formatter(fmt=file_fmt, datefmt="%Y-%m-%d_%H-%M-%S")  # 文件日志格式器

# 第五步：将格式器设置到处理器
file_handler.setFormatter(fmt2)

# 第六步：将处理器添加到日志器
logger.addHandler(file_handler)

# 测试日志输出
logprint2 = logger.info