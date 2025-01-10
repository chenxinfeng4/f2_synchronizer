from wechat_push import WechatPush
push = WechatPush("wwddfxxx", "1000003", "z68xxx")
push.send_text('Hello!\n文本支持换行\n<a href="https://github.com">文本支持超链接</a>')
