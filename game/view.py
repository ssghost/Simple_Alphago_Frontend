from django.shortcuts import render
from . import gochess
 
def board_render(request):
    context          = {}
    context['screen'] = gochess.Game().screen
    context['endcheck'] = gochess.Game().endcheck()
    context['restart'] = gochess.Game().restart()
    context['result'] = gochess.Game().result
    context['showturn'] = gochess.Game().showturn()
    return render(request, 'temp.html', context)