from django.shortcuts import render, get_object_or_404, redirect
from .models import Stamp
from .forms import StampForm

# 스티커 목록 조회
def stamp_list(request):
    stamps = Stamp.objects.all().order_by('-date')
    return render(request, 'stamps/stamp_list.html', {'stamps': stamps})

# 스티커 생성
def stamp_create(request):
    if request.method == 'POST':
        form = StampForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('stamp_list')
    else:
        form = StampForm()
    return render(request, 'stamps/stamp_form.html', {'form': form})

# 스티커 수정
def stamp_update(request, pk):
    stamp = get_object_or_404(Stamp, pk=pk)
    if request.method == 'POST':
        form = StampForm(request.POST, instance=stamp)
        if form.is_valid():
            form.save()
            return redirect('stamp_list')
    else:
        form = StampForm(instance=stamp)
    return render(request, 'stamps/stamp_form.html', {'form': form})

# 스티커 삭제
def stamp_delete(request, pk):
    stamp = get_object_or_404(Stamp, pk=pk)
    if request.method == 'POST':
        stamp.delete()
        return redirect('stamp_list')
    return render(request, 'stamps/stamp_confirm_delete.html', {'stamp': stamp})
