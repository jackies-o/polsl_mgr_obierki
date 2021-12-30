from django.conf.urls import url
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from users import views
from users.views import RegisterView, LoginView

urlpatterns = [
    path(r'^api/users/getAllUsers', views.UserList.as_view()),
    path(r'^api/users/addUser/', views.UserList.as_view()),
    path(r'^api/users/getUser/<int:pk>', views.UserDetail.as_view()),
    url(r'^api/users/modifyUser/<int:pk>', views.UserDetail.as_view()),
    url(r'^api/users/deleteUser/<int:pk>', views.UserDetail.as_view()),
    path('api/register', RegisterView.as_view()),
    path('api/login', LoginView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
