"""
URL configuration for GMOPayment project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path
from .views.member import MemberViewSet, MemberRetrieveView
from .views.merchant import MerchantViewSet
from .views.payment_methods import PaymentMethodListCreateView, CreateTokenView, VerifyCard, CardDetails
from .views.transaction import TransactionListCreateView

urlpatterns = [
    path('members', MemberViewSet.as_view(), name='member-list'),
    path('members/inquiry', MemberRetrieveView.as_view(), name='member-retrieve'),

    path('merchants', MerchantViewSet.as_view(), name='merchant-list'),

    path('verify-card', VerifyCard.as_view(), name='verify-card'),
    path('create-token', CreateTokenView.as_view(), name='create-token'),
    path('store-card', PaymentMethodListCreateView.as_view(), name='payment-method'),
    path('card-details', CardDetails.as_view(), name='card-details'),

    path('transactions', TransactionListCreateView.as_view(), name='transaction-list'),
]
