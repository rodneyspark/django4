from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import Project, UserUpdateForm, ProfileUpdateForm, SignUpForm, NewProjectForm
from django.contrib import messages
from .models import Profile, Project,Ratings
# from rest_framework import status


@login_required(login_url = '/accounts/login/')
def home(request):
    json_projects = Project.all_projects()
    return render(request,'home.html',{'json_projects':json_projects})

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/registration_form.html', {'form': form})

@login_required(login_url='/accounts/login/')
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,f'Your account has been updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'profile.html', context)


@login_required(login_url='/accounts/login/')
def update_profile(request):
    if request.method == 'POST':

        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)

        if user_form.is_valid():
            user_form.save()
            profile_form.save()

            return redirect('home')

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user)

        context = {
            'user_form': user_form,
            'profile_form': profile_form

        }

    return render(request, 'update_profile.html', context)



@login_required(login_url='/accounts/login/')
def new_project(request):
    current_user = request.user
   
    if request.method == 'POST':
        form = NewProjectForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.user = current_user
           
            image.save()
            
        return redirect('home')

    else:
        form = NewProjectForm()
    return render(request, 'new_project.html', {"form": form})


def search_results(request):
    if 'project' in request.GET and request.GET['project']:
        search_term =request.GET.get('project')
        searched_project = Project.search_by_title(search_term)
        message = f'{search_term}'

        return render(request, 'search.html',{"message":message,"projects":searched_project})

    else:
        message = "You haven't searched for any term"

        return render(request,'search.html',{'message':message})


@login_required(login_url = '/accounts/login/')
def rate(request,id):
    if request.method =='POST':
        rates = Ratings.objects.filter(id = id)
        for rate in rates:
            if rate.user == request.user:
                messages.info(request,'You cannot rate a project twice')
                return redirect('singleproject',id)
        design = request.POST.get('design')
        usability = request.POST.get('usability')
        content = request.POST.get('content')
        if design and usability and content:
            project = Project.objects.get(id = id)
            rate = Ratings(design = design,usability = usability,content = content,project_id = project,user = request.user)
            rate.save()
            return redirect('singleproject',id)
        else:
            messages.info(request,'Input all fields')
            return redirect('singleproject',id)
    else:
        messages.info(request,'Input all fields')
        return redirect('singleproject',id)

@login_required(login_url = '/accounts/login/')
def single_project(request,id):  
    project = Project.objects.get(id = id)
    rates = Ratings.objects.filter(project_id = id)
    designrate = []
    usabilityrate = []
    contentrate = []
    if rates:
        for rate in rates:
            designrate.append(rate.design)
            usabilityrate.append(rate.usability)
            contentrate.append(rate.content)
        total = len(designrate)*10
        design = round(sum(designrate)/total*100,1)
        usability = round(sum(usabilityrate)/total*100,1)
        content = round(sum(contentrate)/total*100,1)
        return render(request,'single_project.html',{'project':project,'design':design,'usability':usability,'content':usability})
    else:
        design = 0
        usability = 0
        content = 0       
        return render(request,'single_project.html',{'project':project,'design':design,'usability':usability,'content':usability})