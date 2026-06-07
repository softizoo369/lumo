from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.db import transaction

from saas_core.models import PageTutorial
from .models import Client, Invoice
from .forms import ClientForm, InvoiceForm, InvoiceItemFormSet

# ============================================================================
# 1. CLIENT MODULE (CRUD & ADVANCED LISTING)
# ============================================================================

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
            return redirect('client_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ClientForm()

    tutorial = PageTutorial.objects.filter(page_identifier='add_client', is_active=True).first()

    context = {
        'form': form,
        'tutorial': tutorial,
        'page_title': 'Add New Client'
    }
    return render(request, 'finance/client_form.html', context)


@login_required(login_url='/admin/login/')
def client_list(request):
    workspace = getattr(request, 'workspace', None)
    if not workspace:
        return redirect('tenant_dashboard')

    clients = Client.objects.filter(workspace=workspace).order_by('-created_at')
    
    # --- INLINE CONDITIONAL FILTERS ---
    query = request.GET.get('q', '')
    vat_query = request.GET.get('vat', '')
    email_query = request.GET.get('email', '')

    if query:
        clients = clients.filter(
            Q(name__icontains=query) | 
            Q(company_name__icontains=query) | 
            Q(phone__icontains=query)
        )
    if vat_query:
        clients = clients.filter(tax_number__iexact=vat_query)
    
    if email_query:
        clients = clients.filter(email__iexact=email_query)

    # --- DATA FOR 'SELECT & SEARCH' DROPDOWNS ---
    all_workspace_clients = Client.objects.filter(workspace=workspace)
    filter_names = all_workspace_clients.values_list('name', flat=True).distinct()
    filter_vats = all_workspace_clients.exclude(tax_number__isnull=True).exclude(tax_number__exact='').values_list('tax_number', flat=True).distinct()
    filter_emails = all_workspace_clients.exclude(email__isnull=True).exclude(email__exact='').values_list('email', flat=True).distinct()

    # --- EXPORT LOGIC ---
    export_type = request.GET.get('export')
    if export_type in ['excel', 'pdf']:
        messages.info(request, f"{clients.count()} rows exported to {export_type.upper()}! (Module coming soon)")
        return redirect('client_list')

    # --- PAGINATION ---
    paginator = Paginator(clients, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    tutorial = PageTutorial.objects.filter(page_identifier='client_list', is_active=True).first()

    # --- AJAX RESPONSE FOR TABLE UPDATES ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'finance/partials/client_table_body.html', {'page_obj': page_obj})

    context = {
        'page_obj': page_obj,
        'tutorial': tutorial,
        'total_clients': paginator.count,
        'filter_names': filter_names,
        'filter_vats': filter_vats,
        'filter_emails': filter_emails,
    }
    return render(request, 'finance/client_list.html', context)


@login_required(login_url='/admin/login/')
def client_update(request, pk):
    workspace = getattr(request, 'workspace', None)
    if not workspace:
        return redirect('tenant_dashboard')

    client = get_object_or_404(Client, pk=pk, workspace=workspace)

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, f"Client '{client.name}' updated successfully.")
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)

    context = {
        'form': form,
        'page_title': 'Edit Client'
    }
    return render(request, 'finance/client_form.html', context)


@login_required(login_url='/admin/login/')
def client_delete(request, pk):
    workspace = getattr(request, 'workspace', None)
    if not workspace:
        return redirect('tenant_dashboard')

    client = get_object_or_404(Client, pk=pk, workspace=workspace)
    
    if request.method == 'POST':
        client_name = client.name
        client.delete()
        messages.success(request, f"Client '{client_name}' has been permanently deleted.")
        
    return redirect('client_list')


# ============================================================================
# 2. INVOICE MODULE
# ============================================================================

@login_required(login_url='/admin/login/')
def invoice_create(request):
    workspace = getattr(request, 'workspace', None)
    if not workspace:
        return redirect('tenant_dashboard')

    if request.method == 'POST':
        form = InvoiceForm(request.POST, workspace=workspace)
        formset = InvoiceItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    invoice = form.save(commit=False)
                    invoice.workspace = workspace
                    invoice.save()

                    formset.instance = invoice
                    formset.save()

                    invoice.sub_total = sum(item.total for item in invoice.items.all())
                    tax = (invoice.sub_total * invoice.tax_percentage) / 100
                    invoice.tax_amount = tax
                    invoice.grand_total = (invoice.sub_total + tax) - invoice.discount_amount
                    invoice.save()

                messages.success(request, f"Awesome! Invoice {invoice.invoice_number} has been generated.")
                return redirect('client_list') 
            
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = InvoiceForm(workspace=workspace)
        formset = InvoiceItemFormSet()

    last_invoice = Invoice.objects.filter(workspace=workspace).order_by('-created_at').first()
    next_number = "INV-0001"
    if last_invoice and last_invoice.invoice_number.startswith('INV-'):
        try:
            last_num = int(last_invoice.invoice_number.split('-')[1])
            next_number = f"INV-{(last_num + 1):04d}"
        except:
            pass

    form.initial['invoice_number'] = next_number

    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'finance/invoice_form.html', context)