from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.services import DashboardService


@login_required
def dashboard(request):
    stats = DashboardService.get_stats()
    return render(request, "core/dashboard.html", {"stats": stats})
