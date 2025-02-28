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
from .views.member import MemberViewSet, MemberRetrieveView, MemberDeleteView
from .views.merchant import MerchantViewSet
from .views.payment_methods import PaymentMethodListCreateView, CreateTokenView, VerifyCard, CardDetailsByToken, \
    CardDetailsByMember
from .views.transaction import TransactionCreateView, TransactionOrderUpdateView, TransactionOrderCaptureView, \
    TransactionOrderCancelView, TransactionOrderInqueryView, Finalize3dsPaymentView

urlpatterns = [
    path('members', MemberViewSet.as_view(), name='member-list'),
    path('members/delete', MemberDeleteView.as_view(), name='member-delete'),

    path('members/inquiry', MemberRetrieveView.as_view(), name='member-retrieve'),

    path('merchants', MerchantViewSet.as_view(), name='merchant-list'),

    path('verify-card', VerifyCard.as_view(), name='verify-card'),
    path('create-token', CreateTokenView.as_view(), name='create-token'),
    path('store-card', PaymentMethodListCreateView.as_view(), name='payment-method'),
    path('card-details/token', CardDetailsByToken.as_view(), name='card-details-token'),
    path('card-details/member', CardDetailsByMember.as_view(), name='card-details-token'),

    path('transactions/credit/charge', TransactionCreateView.as_view(), name='transaction-create'),
    path('tds2/finalize-charge', Finalize3dsPaymentView.as_view(), name='transaction-finalize'),
    path('order/update', TransactionOrderUpdateView.as_view(), name='transaction-update'),
    path('order/capture', TransactionOrderCaptureView.as_view(), name='transaction-capture'),
    path('order/cancel', TransactionOrderCancelView.as_view(), name='transaction-cancel'),
    path('order/inquiry', TransactionOrderInqueryView.as_view(), name='transaction-inquiry'),
]

