from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from saas_core.models import PageTutorial
from .models import Client
from .forms import ClientForm
from saas_core.models import PageTutorial # মডেলটি ইম্পোর্ট করুন

@login_required(login_url='/admin/login/')
def client_create(request):
    workspace = getattr(request, 'workspace', None)
    
    if not workspace:
        messages.error(request, "No active workspace found.")
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.workspace = workspace
            client.save()
            messages.success(request, f"Client '{client.name}' has been added successfully.")
            return redirect('client_create')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ClientForm()

    # ---> নতুন কোড: এই পেজের জন্য ভিডিও টিউটোরিয়াল খোঁজা <---
    tutorial = PageTutorial.objects.filter(page_identifier='add_client', is_active=True).first()

    context = {
        'form': form,
        'tutorial': tutorial, # ভিডিওটি টেমপ্লেটে পাঠানো হলো
        'page_title': 'Add New Client'
    }
    return render(request, 'finance/client_form.html', context)

@login_required(login_url='/admin/login/')
def client_list(request):
    workspace = getattr(request, 'workspace', None)
    if not workspace:
        return redirect('tenant_dashboard')

    # সার্চ লজিক: নাম বা কোম্পানি দিয়ে সার্চ করা যাবে
    query = request.GET.get('q')
    clients = Client.objects.filter(workspace=workspace).order_by('-created_at')
    
    if query:
        clients = clients.filter(
            Q(name__icontains=query) | 
            Q(company_name__icontains=query) | 
            Q(email__icontains=query)
        )

    # টিউটোরিয়াল লজিক
    tutorial = PageTutorial.objects.filter(page_identifier='client_list', is_active=True).first()

    context = {
        'clients': clients,
        'tutorial': tutorial,
        'query': query
    }
    return render(request, 'finance/client_list.html', context)