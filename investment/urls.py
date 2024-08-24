from django.urls import path
from investment.views import *

urlpatterns = [
    path('trading-plan/create', TradingPlanCreateView.as_view(), name='trading_plan_create'),
    path('trading-plan/index', TradingPlanListView.as_view(), name='trading_plan_index'),
    path('trading-plan/<int:pk>/detail', TradingPlanDetailView.as_view(), name='trading_plan_detail'),
    path('trading-plan/<int:pk>/edit', TradingPlanUpdateView.as_view(), name='trading_plan_edit'),
    path('trading-plan/<int:pk>/delete', TradingPlanDeleteView.as_view(), name='trading_plan_delete'),
    
    path('signal-plan/create', SignalPlanCreateView.as_view(), name='signal_plan_create'),
    path('signal-plan/index', SignalPlanListView.as_view(), name='signal_plan_index'),
    path('signal-plan/<int:pk>/detail', SignalPlanDetailView.as_view(), name='signal_plan_detail'),
    path('signal-plan/<int:pk>/edit', SignalPlanUpdateView.as_view(), name='signal_plan_edit'),
    path('signal-plan/<int:pk>/delete', SignalPlanDeleteView.as_view(), name='signal_plan_delete'),
    
    path('mining-plan/create', MiningPlanCreateView.as_view(), name='mining_plan_create'),
    path('mining-plan/index', MiningPlanListView.as_view(), name='mining_plan_index'),
    path('mining-plan/<int:pk>/detail', MiningPlanDetailView.as_view(), name='mining_plan_detail'),
    path('mining-plan/<int:pk>/edit', MiningPlanUpdateView.as_view(), name='mining_plan_edit'),
    path('mining-plan/<int:pk>/delete', MiningPlanDeleteView.as_view(), name='mining_plan_delete'),

    path('signal-plan/index', SignalPlanListView.as_view(), name='signal_plan_index'),

]

