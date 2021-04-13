from django.core.files.base import ContentFile
from django.forms.models import modelformset_factory
from django.shortcuts import render, redirect
from . import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect
from django.contrib import messages
from .forms import CreateUserForm, CreateRecordForm, CreateCatalogForm, CreateManufacturerForm, CreateProvenanceForm, \
    CustomFieldForm
from .filters import RecordFilter
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required

from .models import Record, Catalog, Provenance, Manufacturer, CUSTOMFIELD_TYPE, CustomField, Record


def about(request):
    return render(request, 'catalog/about.html')


def home(request):
    return render(request, 'catalog/home.html')


@login_required(login_url='/login')
def recordList(request, cr):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            records = models.Record.objects.filter(my_catalog__id=cr)
        else:
            records = models.Record.objects.filter(my_catalog__id=cr, my_catalog__created_by=request.user)
        provenances = models.Provenance.objects.all()
        
        context = {
            'records': records,
            'provenances': provenances,
        }
        # render gets the recordlist.html file from the folder in catalog/templates/catalog
        return render(request, 'catalog/recordlist.html', context)
    else:
        return HttpResponseRedirect('/login')


# @login_required(login_url='/login')
# def simpleSearch(request):
#     if request.method == 'POST':
#         searched = request.POST['searched']
#         records = Record.objects.filter(name__contains=searched)
#         return render(request, 'catalog/recordlist.html', {'searched':searched, 'records':records})
#     else:
#         return render(request, 'catalog/recordlist.html', {})


@login_required(login_url='/login')
def advancedSearch(request):
    catalogs = models.Catalog.objects.all()
    manufacturers = models.Manufacturer.objects.all()

    if request.user.is_superuser:
        records = models.Record.objects.all()
    else:
        records = models.Record.objects.filter(my_catalog__created_by=request.user)
    provenances = models.Provenance.objects.all()

    myFilter = RecordFilter(request.GET, queryset=records)
    records = myFilter.qs

    context = {
        'records': records,
        'provenances': provenances,
        'myFilter': myFilter,
        'catalogs': catalogs,
        'manufacturers': manufacturers,
    }
    # render gets the recordlist.html file from the folder in catalog/templates/catalog
    return render(request, 'catalog/recordlist.html', context)


@login_required(login_url='/login')
def catalogList(request):
    if request.user.is_authenticated:
        # catalogs = None
        if request.user.is_superuser:
            catalogs = models.Catalog.objects.all()
        else:
            catalogs = models.Catalog.objects.filter(created_by__exact=request.user)

        context = {'catalogs': catalogs, }
        return render(request, 'catalog/cataloglist.html', context)
    else:
        return HttpResponseRedirect('/login')


@login_required(login_url='/login')
def manufacturerList(request):
    if request.user.is_authenticated:
        # catalogs = None
        if request.user.is_superuser:
            manufacturers = models.Manufacturer.objects.all()
        else:
            manufacturers = models.Manufacturer.objects.filter(created_by__exact=request.user)

        context = {'manufacturers': manufacturers, }
        return render(request, 'catalog/manufacturerlist.html', context)
    else:
        return HttpResponseRedirect('/login')


def loginPage(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/home')
            else:
                messages.info(request, 'Username or password is incorrect!')
                return HttpResponseRedirect('/login')

    return render(request, 'catalog/login.html')


@login_required(login_url='/login')
def logoutUser(request):
    logout(request)
    return HttpResponseRedirect('/login')


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = authenticate(request, username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'])
                if user is not None:
                    login(request, user)
                    return HttpResponseRedirect('/home')

                return HttpResponseRedirect('/login')
            else:
                messages.info(request,
                              'Account creation was not successful. Make sure all fields are entered, that your password \n is strong, and that your two password entries match.')
                return HttpResponseRedirect('/register')  # Trying to redirect register page

        context = {'form': form}
    return render(request, 'catalog/register.html', context)


@login_required(login_url='/login')
def createRecord(request):
    record_form = CreateRecordForm()
    if not request.user.is_superuser:
        record_form.fields["my_catalog"].queryset = Catalog.objects.filter(created_by=request.user)
        record_form.fields["manufacturer"].queryset = Manufacturer.objects.filter(created_by=request.user)

    extra_forms = 1
    CustomFieldFormSet = modelformset_factory(CustomField, form=CustomFieldForm, extra=0, max_num=20, )
    custom_formset = CustomFieldFormSet(queryset=CustomField.objects.none())

    if request.method == 'POST':
        record_form = CreateRecordForm(request.POST, request.FILES)
            
        if request.POST.get('add_custom_field'):
            formset_dict_copy = request.POST.copy()
            formset_dict_copy['form-TOTAL_FORMS'] = int(formset_dict_copy['form-TOTAL_FORMS']) + extra_forms
            custom_formset = CustomFieldFormSet(formset_dict_copy)
        else:
            custom_formset = CustomFieldFormSet(request.POST)

            if record_form.is_valid() and custom_formset.is_valid():
                record = record_form.save(commit=False)
                record.created_by = request.user
                record.save()
                instances = custom_formset.save(commit=False)
                for cf in instances:
                    cf.record = record
                    cf.save()
                return redirect('/search')

    context = {
        'record_form': record_form,
        'custom_formset': custom_formset,
    }
    return render(request, 'catalog/create_record.html', context)


@login_required(login_url='/login')
def updateRecord(request, ur):
    record = Record.objects.get(id=ur)
    record_form = CreateRecordForm(instance=record)
    if not request.user.is_superuser:
        record_form.fields["my_catalog"].queryset = Catalog.objects.filter(created_by=request.user)
        record_form.fields["manufacturer"].queryset = Manufacturer.objects.filter(created_by=request.user)

    extra_forms = 1
    CustomFieldFormSet = modelformset_factory(CustomField, form=CustomFieldForm, extra=0, max_num=20, can_delete=True)
    custom_formset = CustomFieldFormSet(queryset=CustomField.objects.filter(record__exact=record))

    if request.method == 'POST':
        record_form = CreateRecordForm(request.POST, request.FILES, instance=record)
            
        if request.POST.get('add_custom_field'):
            formset_dict_copy = request.POST.copy()
            formset_dict_copy['form-TOTAL_FORMS'] = int(formset_dict_copy['form-TOTAL_FORMS']) + extra_forms
            custom_formset = CustomFieldFormSet(formset_dict_copy)
        else:
            custom_formset = CustomFieldFormSet(request.POST,queryset=CustomField.objects.filter(record__exact=record))

            if record_form.is_valid() and custom_formset.is_valid():
                record = record_form.save(commit=False)
                record.created_by = request.user
                record.save()
                instances = custom_formset.save(commit=False)
                for cf in instances:
                    cf.record = record
                    cf.save()
                for cf in custom_formset.deleted_objects:
                    cf.delete()
                return redirect('/search')

    context = {
        'record': record,
        'record_form': record_form,
        'custom_formset': custom_formset,
    }
    return render(request, 'catalog/update_record.html', context)


@login_required(login_url='/login')
def recordDetail(request, pk):
    records = models.Record.objects.filter(id__exact=pk)
    custom_fields = models.CustomField.objects.all()
    provenances = models.Provenance.objects.all()

    context = {
        'records': records,
        'custom_fields': custom_fields,
        'provenances': provenances,

    }
    return render(request, 'catalog/record_detail.html', context)


@login_required(login_url='/login')
def deleteRecord(request, ur):
    record = Record.objects.get(id=ur)
    if request.method == "POST":
        record.delete()
        return redirect('/search')

    context = {'record': record, }
    return render(request, 'catalog/delete_record.html', context)


@login_required(login_url='/login')
def createCatalog(request):
    form = CreateCatalogForm()

    if request.method == 'POST':
        form = CreateCatalogForm(request.POST)
        if form.is_valid():
            catalog = form.save(commit=False)
            catalog.created_by = request.user
            catalog.save()
            return redirect('/catalog')

    context = {'form': form, }
    return render(request, 'catalog/create_catalog.html', context)


@login_required(login_url='/login')
def deleteCatalog(request, ur):
    catalog = Catalog.objects.get(id=ur)
    if request.method == "POST":
        catalog.delete()
        return redirect('/catalog')

    context = {'catalog': catalog, }
    return render(request, 'catalog/delete_catalog.html', context)


@login_required(login_url='/login')
def updateCatalog(request, ur):
    catalog = Catalog.objects.get(id=ur)
    form = CreateCatalogForm(instance=catalog)

    if request.method == 'POST':
        form = CreateCatalogForm(request.POST, instance=catalog)
        if form.is_valid():
            form.save()
            return redirect('/catalog')

    context = {
        'form': form,
        'catalog': catalog,
    }
    return render(request, 'catalog/update_catalog.html', context)


@login_required(login_url='/login')
def createProvenance(request):
    form = CreateProvenanceForm()
    form.fields["record"].queryset = Record.objects.filter(created_by=request.user)
    if request.method == 'POST':
        form = CreateProvenanceForm(request.POST)
        if form.is_valid():
            provenance = form.save(commit=False)
            provenance.created_by = request.user
            provenance.save()

        return redirect('/search')

    context = {'form': form, }
    return render(request, 'catalog/create_provenance.html', context)


@login_required(login_url='/login')
def deleteProvenance(request, ur):
    provenance = Provenance.objects.get(id=ur)
    if request.method == "POST":
        provenance.delete()
        return redirect('/search')

    context = {'provenance': provenance, }
    return render(request, 'catalog/delete_provenance.html', context)


@login_required(login_url='/login')
def updateProvenance(request, ur):
    provenance = Provenance.objects.get(id=ur)
    form = CreateProvenanceForm(instance=provenance)
    form.fields["record"].queryset = Record.objects.filter(created_by=request.user)
    if request.method == 'POST':
        form = CreateProvenanceForm(request.POST, instance=provenance)
        if form.is_valid():
            form.save()
            return redirect('/search')

    context = {
        'form': form,
        'provenance': provenance,
    }
    return render(request, 'catalog/update_provenance.html', context)


@login_required(login_url='/login')
def createManufacturer(request):
    form = CreateManufacturerForm()

    if request.method == 'POST':
        form = CreateManufacturerForm(request.POST)
        if form.is_valid():
            manufacturer = form.save(commit=False)
            manufacturer.created_by = request.user
            manufacturer.save()
            return redirect('/manufacturer')

    context = {'form': form, }
    return render(request, 'catalog/create_manufacturer.html', context)


@login_required(login_url='/login')
def deleteManufacturer(request, ur):
    manufacturer = Manufacturer.objects.get(id=ur)
    if request.method == "POST":
        manufacturer.delete()
        return redirect('/manufacturer')

    context = {'manufacturer': manufacturer, }
    return render(request, 'catalog/delete_manufacturer.html', context)


@login_required(login_url='/login')
def updateManufacturer(request, ur):
    manufacturer = Manufacturer.objects.get(id=ur)
    form = CreateManufacturerForm(instance=manufacturer)

    if request.method == 'POST':
        form = CreateManufacturerForm(request.POST, instance=manufacturer)
        if form.is_valid():
            form.save()
            return redirect('/manufacturer')

    context = {
        'form': form,
        'manufacturer': manufacturer,
    }
    return render(request, 'catalog/update_manufacturer.html', context)