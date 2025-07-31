from app import app

# Vercel需要這個作為入口點
def handler(request):
    return app(request.environ, request.start_response)

# 也可以直接導出app
application = app
