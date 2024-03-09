from django.shortcuts import render, redirect
from django.views.generic import FormView
from .forms import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os
import base64
from .search import search_similar_images, add_features
from time import time

@login_required(login_url="/auth")
def index(request):    
    return render(request, "imagesearch/index.html")


def home(request):
    return render(request, "imagesearch/home_page.html")

def logout_user(request):
    print(f"User {request.user} logged out successfully")
    logout(request)
    return redirect("/")
            

def search_view(request):
    start_time = time()
    print(f"incoming request for action {request.POST['action']}, user: {request.user}")
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'search':
            uploaded_image = request.FILES.get('image')

            uploaded_image_path = os.path.join(settings.MEDIA_ROOT, uploaded_image.name)
            with open(uploaded_image_path, 'wb') as destination:
                for chunk in uploaded_image.chunks():
                    destination.write(chunk)

            with open(uploaded_image_path, "rb") as image_file:
                base64_uploaded_image = base64.b64encode(image_file.read()).decode("utf-8")
                
            # image_urls = [
            #     (f"/media/images/user_{request.user}/image_1.jpeg", 'image_1'),
            #     ] 
            
            image_urls = search_similar_images(request.user, uploaded_image_path)
            try:
                os.remove(uploaded_image_path)
            except:
                print("failed to remove image here ... ", uploaded_image_path)
                pass
            
            context = {
                'uploaded_image': f"data:image/png;base64,{base64_uploaded_image}",
                'image_urls': image_urls,
                "user": request.user
            }
            print(f"return with rendering search result. user {request.user}, time taken {start_time - time()}")
            return render(request, "imagesearch/search_results.html", context) 
        
        elif action == 'add_to_database':
            try:
                uploaded_image = request.FILES.get('image')
                user_name = request.user
                uploaded_image_path = os.path.join(settings.MEDIA_ROOT, f"images/user_{user_name}", uploaded_image.name)
                with open(uploaded_image_path, 'wb') as destination:
                    for chunk in uploaded_image.chunks():
                        destination.write(chunk)
                        
                add_features(user_name, uploaded_image_path, uploaded_image.name)
                context = {'success_message': 'Insert Successful', 'status': 'success'}
            except:
                print("failed to add image to dataset for user ", request.user)
                context = {'success_message': 'Insert Failed', 'status': 'failure'}

            print(f"inserted to db. user {request.user}, time taken {start_time - time()}")
            return render(request, "imagesearch/index.html", context) 
        
        
    print(f"it should not be logged. user {request.user}, time taken {start_time - time()}")
    return render(request, "imagesearch/search_results.html")  

class LoginView(FormView):
    template_name = "user/login.html"
    form_class = LoginForm
    success_url = "/imagesearch"
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        
        user = authenticate(self.request, username=username, password=password)
        
        if user is not None:
            login(self.request, user)
            print(f"User logged in successfully {username}")
            return super().form_valid(form)
        else:
            print(f"Invalid user submission request. username {username}, password {password}")
            return self.form_invalid(form)
        
    
    