from django.shortcuts import render, redirect
from django.views.generic import FormView
from .forms import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os
import base64
from .search import search_similar_images
        
@login_required(login_url="/auth")
def index(request):    
    print(request.user)
    return render(request, "imagesearch/index.html")


def home(request):
    return render(request, "imagesearch/home_page.html")

def logout_user(request):
    logout(request)
    return redirect("/")


def search_view(request):
    if request.method == 'POST':
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
        os.remove(uploaded_image_path)
        
        context = {
            'uploaded_image': f"data:image/png;base64,{base64_uploaded_image}",
            'image_urls': image_urls,
            "user": request.user
        }

    return render(request, "imagesearch/search_results.html", context)  

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
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
        
    
    