import logging
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.utils import NestedObjects
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.utils.http import urlencode
from django.db import DEFAULT_DB_ALIAS
from rest_framework.authtoken.models import Token

from dojo.filters import GroupFilter
from dojo.forms import DojoGroupForm, DeleteGroupForm, Add_Product_Group_GroupForm, Add_Product_Type_Group_GroupForm
from dojo.models import Dojo_Group, Product_Group, Product_Type_Group
from dojo.utils import get_page_items, add_breadcrumb
from dojo.group.queries import get_authorized_products_for_group, get_authorized_product_types_for_group

logger = logging.getLogger(__name__)


@user_passes_test(lambda u: u.is_staff)
def group(request):
    groups = Dojo_Group.objects.order_by('name')
    groups = GroupFilter(request.GET, queryset=groups)
    paged_groups = get_page_items(request, groups.qs, 25)
    add_breadcrumb(title="All Groups", top_level=True, request=request)
    return render(request,
                  'dojo/groups.html',
                  {'groups': paged_groups,
                   'filtered': groups,
                   'name': 'All Groups',
                   })


@user_passes_test(lambda u: u.is_staff)
def view_group(request, gid):
    group = get_object_or_404(Dojo_Group, id=gid)
    products = get_authorized_products_for_group(group)
    product_types = get_authorized_product_types_for_group(group)
    users = group.users.all()

    add_breadcrumb(title="View Group", top_level=False, request=request)
    return render(request, 'dojo/view_group.html', {
        'group': group,
        'products': products,
        'product_types': product_types,
        'users': users
    })


@user_passes_test(lambda u: u.is_superuser)
def edit_group(request, gid):
    group = get_object_or_404(Dojo_Group, id=gid)
    form = DojoGroupForm(instance=group)

    if request.method == 'POST':
        form = DojoGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Group saved successfully.',
                                 extra_tags='alert-success')
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Group was not saved successfully.',
                                 extra_tags='alert_danger')

    add_breadcrumb(title="Edit Group", top_level=False, request=request)
    return render(request, "dojo/add_group.html", {
        'form': form
    })


@user_passes_test(lambda u: u.is_superuser)
def delete_group(request, gid):
    group = get_object_or_404(Dojo_Group, id=gid)
    form = DeleteGroupForm(instance=group)

    if request.method == 'POST':
        if 'id' in request.POST and str(group.id) == request.POST['id']:
            form = DeleteGroupForm(request.POST, instance=group)
            if form.is_valid():
                group.delete()
                messages.add_message(request,
                                     messages.SUCCESS,
                                     'Group and relationships successfully removed.',
                                     extra_tags='alert-success')
                return HttpResponseRedirect(reverse('groups'))

    collector = NestedObjects(using=DEFAULT_DB_ALIAS)
    collector.collect([group])
    rels = collector.nested()
    add_breadcrumb(title="Delete Group", top_level=False, request=request)
    return render(request, 'dojo/delete_group.html',{
        'to_delete': group,
        'form': form,
        'rels': rels
    })


@user_passes_test(lambda u: u.is_superuser)
def add_group(request):
    form = DojoGroupForm
    group = None

    if request.method == 'POST':
        form = DojoGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Group was added successfully, you may edit if necessary.',
                                 extra_tags='alert-success')
            return HttpResponseRedirect(reverse('edit_group', args=(group.id,)))
        else:
            messages.add_message(request, messages.ERROR,
                                 'Group was not added successfully.',
                                 extra_tags='alert-danger')

    add_breadcrumb(title="Add Group", top_level=False, request=request)
    return render(request, "dojo/add_group.html", {
        'form': form
    })


@user_passes_test(lambda u: u.is_superuser)
def add_product_group(request, gid):
    group = get_object_or_404(Dojo_Group, id=gid)
    group_form = Add_Product_Group_GroupForm(initial={'group': group.id})

    if request.method == 'POST':
        group_form = Add_Product_Group_GroupForm(request.POST, initial={'group': group.id})
        if group_form.is_valid():
            if 'products' in group_form.cleaned_data and len(group_form.cleaned_data['products']) > 0:
                for product in group_form.cleaned_data['products']:
                    existing_groups = Product_Group.objects.filter(product=product, group=group)
                    if existing_groups.count() == 0:
                        product_group = Product_Group()
                        product_group.product = product
                        product_group.group = group
                        product_group.role = group_form.cleaned_data['role']
                        product_group.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Product group added successfully.',
                                 extra_tags='alert-success')
            return HttpResponseRedirect(reverse('view_group', args=(gid, )))

    add_breadcrumb(title="Add Product Group", top_level=False, request=request)
    return render(request, 'dojo/new_product_group_group.html', {
        'group': group,
        'form': group_form
    })


@user_passes_test(lambda u: u.is_superuser)
def add_product_type_group(request, gid):
    group = get_object_or_404(Dojo_Group, id=gid)
    group_form = Add_Product_Type_Group_GroupForm(initial={'group': group.id})

    if request.method == 'POST':
        group_form = Add_Product_Type_Group_GroupForm(request.POST, initial={'group': group.id})
        if group_form.is_valid():
            if 'product_types' in group_form.cleaned_data and len(group_form.cleaned_data['product_types']) > 0:
                for product_type in group_form.cleaned_data['product_types']:
                    existing_groups = Product_Type_Group.objects.filter(product_type=product_type)
                    if existing_groups.count() == 0:
                        product_type_group = Product_Type_Group()
                        product_type_group.product_type = product_type
                        product_type_group.group = group
                        product_type_group.role = group_form.cleaned_data['role']
                        product_type_group.save()
                messages.add_message(request,
                                     messages.SUCCESS,
                                     'Product type groups added successfully.',
                                     extra_tags='alert-success')
                return HttpResponseRedirect(reverse('view_group', args=(gid, )))

    add_breadcrumb(title="Add Product Type Group", top_level=False, request=request)
    return render(request, 'dojo/new_product_type_group_group.html', {
        'group': group,
        'form': group_form,
    })
