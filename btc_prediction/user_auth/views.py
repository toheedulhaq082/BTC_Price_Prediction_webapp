
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import CreateUserForm, LoginForm
from django.contrib.auth.models import auth
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
import datetime
import pandas as pd 
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tensorflow
import datetime


model = tensorflow.keras.models.load_model("./savedModels/model.keras", compile=True, safe_mode=True)
df = pd.read_csv('./savedModels/BTC-USD.csv', index_col = False)

# # home view
def home(request):
    return render(request, "user_auth/index.html")

# #register view
def register(request):

    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    context = {"form": form}

    return render(request, "user_auth/register.html", context=context)



# login view
def login(request):

    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect("prediction")
            
    context = {'loginform':form}
    
    return render(request, 'user_auth/login.html', context=context)
            
    
# logout view
def logout(request):
    auth.logout(request)
    return render(request, "user_auth/index.html")

# prediction view
def prediction(request):
    new_df = df.reset_index()['Close']

    scaler = MinMaxScaler(feature_range=(0,1))
    new_df =scaler.fit_transform(np.array(new_df).reshape(-1,1))
     
    ##splitting dataset into train and test split
    training_size=int(len(new_df)*0.70)
    test_size=len(new_df)-training_size
    train_data, test_data=new_df[0:training_size,:],new_df[training_size: len(new_df),:1]

    x_input=test_data[449:].reshape(1,-1)
    
    temp_input=list(x_input)
    temp_input=temp_input[0].tolist()

    lst_output=[]
    n_steps=100
    i=0
    while(i<30):
        if(len(temp_input)>100):
            #print(temp_input)
            x_input = np.array(temp_input[1:])
            print("{} day input {}".format(i,x_input))
            x_input=x_input.reshape(1,-1)
            x_input = x_input.reshape((1, n_steps, 1))
            #print(x_input)
            yhat = model.predict(x_input, verbose=0)
            print("{} day output {}".format(i,yhat))
            temp_input.extend(yhat[0].tolist())
            temp_input=temp_input[1:]
            #print(temp_input)
            lst_output.extend(yhat.tolist())
            i=i+1
        else:
            x_input = x_input.reshape((1, n_steps,1))
            yhat = model.predict(x_input, verbose=0)
            print(yhat[0])
            temp_input.extend(yhat[0].tolist())
            print(len(temp_input))
            lst_output.extend(yhat.tolist())
            i=i+1
    lst = scaler.inverse_transform(lst_output).tolist

    # int_lst = [int(item[0]) for item in lst]

    # date_price_dict = {}
    # today = datetime.date.today()
    
    # for price in int_lst:
    #    date_price_dict[today] = price
    #    today += datetime.timedelta(days=1)

    return render(request, "user_auth/predict.html", {"prediction":lst})
