from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.contrib.auth.forms import UserCreationForm
from .forms import (UserRegisterForm, UserUpdateForm, ProfileUpdateForm,RegistrationFrom)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connection, IntegrityError
from .models import (tblObjectHead, tblUserRights)
import json
from django.contrib.auth.models import User
from django.db.models import Q


@login_required
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = RegistrationFrom
    return render(request, 'users/register.html', {'form': form})


def forgot_password(request):
    return render(request, 'users/forgot-password.html')


@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('Profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)


@login_required
def user_roles(request):
    request.session['objectID'] = 18
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM auth_user AU
                    WHERE AU.id IN (SELECT UserID FROM tblUserRights) AND id !=2''')
    users = cursor.fetchall()
    context = {
        'users':users,
        'title': "User Roles"
    }
    return render(request, 'users/user_roles.html', context)


@login_required
def add_user_roles(request):
    cursor = connection.cursor()
    main_menu = tblObjectHead.objects.filter(ParentID = 0).all()
    cursor.execute('''SELECT * FROM auth_user AU
                    WHERE AU.id NOT IN (SELECT UserID FROM tblUserRights) AND AU.id !=1 ''')
    users = cursor.fetchall()
    main_object_id = request.POST.get("main_object_id")
    if main_object_id:
        sub_menu = tblObjectHead.objects.filter(ParentID = main_object_id).all()
        sub_menu = serializers.serialize('json',sub_menu)
        return JsonResponse({"sub_menu":sub_menu})
    sub_menu_id = request.POST.get("sub_menu_id")
    if sub_menu_id:
        cursor.execute('''select OD.ObjectID, OD.ActionID, AC.ActionName
                        from tblObjectDetail OD
                        inner join tblAction AC on AC.ActionID = OD.ActionID
                        where OD.ObjectID = %s;''',[sub_menu_id])
        actions = cursor.fetchall()
        return JsonResponse({'actions':actions})
    if request.method == "POST":
        new_roles = json.loads(request.POST.get("new_roles"))
        for role in new_roles:
            role = tblUserRights(UserID = role["userID"], ObjectID = role["objectID"], ActionID = role["actionID"], IsAllow = role["isAllow"])
            role.save()
        return JsonResponse({"SUCCESS":"SUCCESS"})
    context = {
        'main_menu':main_menu,
        'users':users,
        'title':'User Roles New'
        }
    return render(request, 'users/add_user_roles.html',context)

@login_required
def edit_user_roles(request, id):
    cursor = connection.cursor()
    user = User.objects.filter(id = id).first()
    main_menu = tblObjectHead.objects.filter(ParentID = 0).all()
    main_object_id = request.POST.get("main_object_id")
    if main_object_id:
        sub_menu = tblObjectHead.objects.filter(ParentID = main_object_id).all()
        sub_menu = serializers.serialize('json',sub_menu)
        print(type(sub_menu))
        return JsonResponse({"sub_menu":sub_menu})
    sub_menu_id = request.POST.get("sub_menu_id")
    if sub_menu_id:
        cursor.execute('''select distinct tblAction.ActionID,ActionName,
                        ifnull((Select isAllow From tblUserRights WHERE
                        ObjectID = tblObjectHead.ObjectID AND
                        ActionID = tblAction.ActionID
                        And tblUserRights.UserID = %s),0) As isAllow
                        from tblObjectHead
                        inner join tblObjectDetail on tblObjectDetail.ObjectID = tblObjectHead.ObjectID
                        inner join tblAction  on tblAction.ActionID = tblObjectDetail.ActionID
                        where tblObjectHead.ObjectID = %s''', [user.id,sub_menu_id])
        actions = cursor.fetchall()
        return JsonResponse({'actions':actions})
    if request.method == "POST":
        edit_roles = json.loads(request.POST.get("edit_roles"))
        for value in edit_roles:
            object_id = Q(ObjectID = value["objectID"])
            action_id = Q(ActionID = value["actionID"])
            user_id = Q(UserID = value["userID"])
            try:
                rights = tblUserRights.objects.get(object_id, action_id, user_id)
                rights.IsAllow = value["isAllow"]
                rights.save()
            except Exception as e:
                role = tblUserRights(UserID = value["userID"], ObjectID = value["objectID"], ActionID = value["actionID"], IsAllow = value["isAllow"])
                role.save()
        return JsonResponse({"succss":"success"})
    context = {
        "user":user,
        "main_menu":main_menu,
    }
    return render(request, 'users/edit_user_roles.html', context)

@login_required
def delete_user_roles(request, id):
    tblUserRights.objects.filter(UserID = id).all().delete()
    messages.add_message(request, messages.SUCCESS, "Roles Deleted")
    return redirect('user-roles')
