from django.shortcuts import render, redirect
import pandas as pd
import pickle
import os
import joblib
from django.conf import settings
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.forms import UserCreationForm
from .models import Room, Community, RoomMessage, User
from .forms import RoomForm, UserForm, MyUserForm
from . import model


def userLogin(request):

    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'No User Found')

        # either returns an error or return a user object that matches these credentials
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # adds a session in the database and the user will be officially logged in
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def userLogout(request):
    logout(request)
    return redirect('login')


def userRegister(request):
    form = MyUserForm()

    if request.method == 'POST':
        form = MyUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # to access the user
            # cleaning the data
            user.username = user.username.lower()  # lowercase letters
            user.save()
            # user that just registered will be logged in through this
            login(request, user)
            return redirect('home')
        else:
            messages.error(
                request, 'An error has occurred during registration.Please enter correct information.')

    return render(request, 'base/login_register.html', {'form': form})

@login_required(login_url='/login')
def home(request):
    # rooms = Room.objects.all() #gives all rooms in the database
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(subject__name__icontains=q) | Q(
        name__icontains=q) | Q(description__icontains=q))

    communities = Community.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = RoomMessage.objects.filter(Q(room__subject__name__icontains=q))

    coin_names = {
        "Cardano (ADA)": "base/model/ADA_predictions.pkl",
        "Bitcoin Cash (BCH)" : "base/model/BCH_predictions.pkl",
        "Binance Coin (BNB)" : "base/model/BNB_predictions.pkl",
        "Bitcoin (BTC)" : "base/model/BTC_predictions.pkl",
        "Dai Coin (DAI)" : "base/model/DAI_predictions.pkl",
        "DogeCoin (DOGE)" : "base/model/DOGE_predictions.pkl",
        "Ethereum (ETH)" : "base/model/ETH_predictions.pkl",
        "ChainLink (LINK)" : "base/model/LINK_predictions.pkl",
        "LiteCoin (LTC)" : "base/model/LITECOIN_predictions.pkl",
        "PolkaDot (DOT)" : "base/model/POLKADOT_predictions.pkl",
        "Polygon (MATIC)" : "base/model/POLYGON_predictions.pkl",
        "Shiba INU (SHIB)" : "base/model/SHIBA_predictions.pkl",
        "Solana (SOL)" : "base/model/SOLANA_predictions.pkl",
        "Stellar (XLM)" : "base/model/STELLAR_predictions.pkl",
        "TRON (TRX)" : "base/model/TRON_predictions.pkl",
        "TrueUSD (TUSD)" : "base/model/TrueUSD_predictions.pkl",
        "USD Coin (USDC)" : "base/model/USDC_predictions.pkl",
        "Tether (USDT)" : "base/model/USDT_predictions.pkl",
        "Wrapped Bitcoin (WBTC)" : "base/model/WBTC_predictions.pkl",
        "Ripple USD (XRP)" : "base/model/XRP_predictions.pkl",
    }


    context = {'rooms': rooms, 'communities': communities,
                   'room_count': room_count, "coin_names":coin_names, "room_messages":room_messages}

    if request.method == 'POST':
        print(request.POST.get('selected_coin_name'))
        model = joblib.load(request.POST.get('selected_coin_name'))
        model_name = request.POST.get('selected_coin_name')
        print(model)
        name_input = request.POST.get('input_coin_name').lower()
        context['name_input'] = name_input

        open_input = float(request.POST.get('input_data', 0))
        context['open_input'] = open_input
        print(open_input)
        close_input = float(request.POST.get('input_data1'))
        context['close_input'] = close_input
        print(close_input)
        

        BTC_input = pd.DataFrame(
            {"Open": [open_input], "Close": [close_input]})
        BTC_prediction = "Default Val"
        BTC_prediction = model.predict(BTC_input)
        print("Predicted value: ", BTC_prediction)
        context['BTC_prediction'] = BTC_prediction
        return render(request, 'base/home.html', context)
    

    if request.method == 'GET':
        
        return render(request, 'base/home.html', context)


def room(request, pk):  # pk used to query the database. We are passing pk here so that each room can be accessed by their ids when requested
    # room = None #At the start, there will be no room, so initialized to none.
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room = i
    room = Room.objects.get(id=pk)
    # we can query child objects of any specific room here
    room_messages = room.roommessage_set.all()
    participants = room.participants.all()
    if request.method == 'POST':
        message = RoomMessage.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants}

    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.roommessage_set.all()
    communities = Community.objects.all()
    context = {'user':user, "rooms":rooms,'room_messages':room_messages, 'communities':communities,}
    return render(request, 'base/user_profile.html', context)


@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm()
    communities = Community.objects.all()

    if request.method == 'POST':
        community_name = request.POST.get('subject')
        community, created = Community.objects.get_or_create(name = community_name)

        Room.objects.create(
            buddy=request.user,
            subject=community,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')

    context = {'form': form, 'communities':communities}
    return render(request, 'base/form.html', context)


@login_required(login_url='/login')
def roomUpdate(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    communities = Community.objects.all()


    if request.user != room.buddy:
        return HttpResponse("You have been restricted for this feature")

    if request.method == 'POST':
        community_name = request.POST.get('subject')
        community, created = Community.objects.get_or_create(name = community_name)
        room.name = request.POST.get('name')
        room.subject = community
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'communities':communities, 'room':room}
    return render(request, 'base/form.html', context)


@login_required(login_url='/login')
def roomDelete(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.buddy:
        return HttpResponse("You have been restricted for this feature")

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='/login')
def deleteMessage(request, pk):
    message = RoomMessage.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You have been restricted for this feature")

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form':form})

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    communities = Community.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'communities':communities})

def activityPage(request):
    room_messages = RoomMessage.objects.all()
    return render(request, 'base/activity.html', {'room_messages':room_messages})