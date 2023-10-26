from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe

from .gpt import ChatConversation
from .models import Profile, ChatInfo, UserInfo
import json

def signup(request):
    
    #TODO: Create HTML template and backend for User model, with openai validation
    #TODO: Create template and backend for changing data in model
    #TODO: Veryfi user email
    #TODO: Sigup with google, github
    
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        openai_api_key = request.POST['Open ai api key']
        
        if password2 == password:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Ten email jest zajęty')
                return redirect('signup')
            
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Nazwa użytkownia jest zajęta')
                return redirect('signup')
            
            else:

                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                user_model = Profile.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id, openai_api_key=openai_api_key)
                new_profile.save()
                return redirect('/settings')
        else:
            messages.info(request, 'Hasła nie są takie same')
            return redirect('signup')
        
    else:
        return render(request, 'signup.html')

def signin(request):
    #TODO: Sign in with github, google
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is None:
            messages.info(request, 'Niepoprawna nazwa użytkownika lub hasło')
            return redirect('signin')
        else:
            auth.login(request, user)
            return redirect('/')
    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')



@login_required(login_url='signin')
def home(request):
    messages_ = []
    reply_content = ''
    api_key = open("C:\\Users\\mikol\\OneDrive\\Dokumenty\\key.txt", "r").read().strip("\n")
    user = request.user.username


    
    #TODO : Reset user chat(add chat ID and current chat ID to ChatInfo model)
    #TODO : Integrate home function with ORM models
    #TODO : Create multimple chat categories
    #TODO : Organize code in diffrent files as soon it will be huge mess
    
    # declaring ChatConversation class for gpt
    conversation = ChatConversation(user, 20, api_key)
    chats = ChatInfo.objects.filter(user=user)
    chat_category = ''
    chat_ids = []

    #checkig if chat was previously generated and if not generating promt saying hello
    if not ChatInfo.objects.filter(user=user).exists():
        chatTimeline = conversation.get_gptResponse("Say short hello to user")
        obj = ChatInfo(user=user, chat=str(chatTimeline))
        obj.save()
        chat_category = obj.category
    else:
        obj = ChatInfo.objects.filter(user=user).order_by('-created_at').first()
        chat_category = obj.category
        for chat in chats:
            chat_ids.append(chat.id_chat)
    
    
    # must use list(eval(str)) to convert single string to list of dictionaries
    conversation.messages = list(eval(obj.chat))
    if request.method == "POST":
        prompt = request.POST["prompt"]
        chatTimeline  = conversation.get_gptFunction(prompt)
        obj.chat = str(chatTimeline)
        obj.save()
    
    messages_ = list(eval(obj.chat))
    messages_ = [mark_safe(conversation.get_messegesHTML())]
    context = {'messages_': messages_,
               'reply_content': reply_content,
               'chat_cats': chat_ids,
               'chat_category': chat_category
               }

    return render(request, 'home.html', context=context)

@login_required(login_url='signin')
def create_chat(request):
    if request.method == 'POST':
        new_chat = request.POST.get()

    return redirect('home')

def chat(request, pk):
    Chat = ChatInfo.objects.get(id_chat=pk)

@login_required(login_url='signin')
def settings(request):
    user_profile = UserInfo.objects.get(user=request.user)

    if request.method == "POST":

        investments = request.POST.get('investments', '')
        sectors = request.POST.get('sectors', '')
        risk_level = request.POST.get('risk_level', '')
        expected_annual_return = request.POST.get('expected_annual_return', '')
        investment_period = request.POST.get('investment_period', '')
        esg = request.POST.get('esg', '')

        user_profile.investments = investments
        user_profile.sectors = sectors
        user_profile.risk_level = risk_level
        user_profile.expected_annual_return = expected_annual_return
        user_profile.investment_period = investment_period
        user_profile.esg = esg

        user_profile.save()

        return redirect('settings')

    return render(request, 'settings.html', {'user_profile': user_profile})




