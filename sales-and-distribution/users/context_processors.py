from django.http import request
from .models import tblObjectHead
from django.contrib.auth.models import User
import mysql.connector
from django.db import connection

def side_bar_objects(request):
    ObjectHead = tblObjectHead.objects.filter(ParentID = 0,).all()
    cursor = connection.cursor()
    cursor.execute('''Select * from tblObjectHead Where ObjectID in
                    (
                    Select ObjectID From tblUserRights Where UserID = %s AND ActionID = 1 AND isAllow = 1 AND tblObjectHead.isActive = 1)
                    ''',[request.user.id])
    ObjectHeadChild = cursor.fetchall()
    return {'ObjectHead':ObjectHead,'ObjectHeadChild':ObjectHeadChild}


def add_allow(request):
    try:
        if request.session["objectID"]:
            c = request.session["objectID"]
            print("yahan per c ", c)
            cursor = connection.cursor()
            cursor.execute("""select isAllow from tblUserRights where UserID=%s and ActionID=2 and ObjectId=%s LIMIT 1""",[request.user.id, c])
            allow = cursor.fetchall()
            return {'allow_add':allow}
        else:
            pass
    except Exception as e:
        print(e)
    return {'allow_add':[[0]]}

def edit_allow(request):
    try:
        if request.session["objectID"]:
            c = request.session["objectID"]
            cursor = connection.cursor()
            cursor.execute("""select isAllow from tblUserRights where UserID=%s and ActionID=3 and ObjectId=%s LIMIT 1""",[request.user.id, c])
            allow = cursor.fetchall()
            print("edit is",allow)
            return {'allow_edit':allow}
        else:
            pass
    except Exception as e:
        print(e)

    return {'allow_edit':0}

def delete_allow(request):
    try:
        if request.session["objectID"]:
            c = request.session["objectID"]
            cursor = connection.cursor()
            cursor.execute("""select isAllow from tblUserRights where UserID=%s and ActionID=4 and ObjectId=%s LIMIT 1""",[request.user.id, c])
            allow = cursor.fetchall()
            return {'allow_delete':allow}
        else:
            pass
    except:
        print('error')

    return {'allow_delete':0}

def print_allow(request):
    try:
        if request.session["objectID"]:
            c = request.session["objectID"]
            cursor = connection.cursor()
            cursor.execute("""select isAllow from tblUserRights where UserID=%s and ActionID=5 and ObjectId=%s LIMIT 1""",[request.user.id, c])
            allow = cursor.fetchall()
            return {'allow_print':allow}
        else:
            pass
    except Exception as e:
        print(e)

    return {'allow_print':0}

    # print('here is ths session', request.session['ObjectId'])
