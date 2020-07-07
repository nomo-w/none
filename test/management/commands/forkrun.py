# from django.core.management.base import BaseCommand, CommandError
# class Command(BaseCommand):
#     def add_arguments(self, parser):
#         parser.add_argument(
#             '-n',
#             '--name',
#             action='store',
#             dest='name',
#             default='close',
#             help='name of author.',
#         )
#     def handle(self, *args, **options):
#         try:
#             if options['name']:
#                 print('hello world, %s' % options['name'])        
#             self.stdout.write(self.style.SUCCESS('命令%s执行成功, 参数为%s' % (__file__, options['name'])))
#         except Exception as ex:
#             self.stdout.write(self.style.ERROR('命令执行出错'))


from django.core.management.base import BaseCommand, CommandError
from django.db import models
import os

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-f', '--fork', default='none', dest='fork', action='store', help='fork')

    def handle(self, *args, **options):
        # print('hello, django!')
        try:
            # if options['name']:
                # print(options['name'])
            # self.stdout.write(self.style.SUCCESS('命令%s执行成功, 参数为%s' % (__file__, options['name']
            self.stdout.write(self.style.SUCCESS(options['fork']))
        except Exception as ex:
            self.stdout.write(self.style.ERROR('命令执行出错'))
            
            