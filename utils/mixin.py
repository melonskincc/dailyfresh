from django.contrib.auth.decorators import login_required

class LoginRequiredMixin:
    @classmethod
    def as_view(cls,**initkwargs):
        # 使用super调用View类中的as_view()
        view=super().as_view()
        # 调用login_required装饰器验证是否登陆
        return login_required(view)