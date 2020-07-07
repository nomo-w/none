from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
import os
import multiprocessing

# Create your views here.


class Test1(View):
    def get(self, request):
        return HttpResponse('test112132dsfssdfdsfdsfdsfsdfsdfdsfdsfdfsdfsdfsdfdsfdsfdsfdsdf3232 OK')


def Fork_zsq(func):
    def inner(*args, **kwargs):
        try:
            pid = os.fork()
            if pid == 0:
                # child process
                return func(*args, **kwargs)
            else:
                pass
        except OSError:
            print('Create process failed!')
    return inner


def fork_zsq2(request):
    p = multiprocessing.Process(target=Test2, args=(request, ))
    p.start()


# @Fork_zsq
# @fork_zsq2
def Test2(request):
    if request.method == 'GET':
        return HttpResponse('test2 ssdfdsfdsdfsdfdsfdfssdfssdfsdfdsfdsfdfdsfdsfsfdsfdsfsdfdfsdsfdsfsdfdsfdsfdsfdfsdfsdfsdfdsfOK')
