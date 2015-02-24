from django.shortcuts import render, render_to_response, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Avg
import hashlib
import time
from datetime import datetime
import json
#from facepy import GraphAPI
from game.forms import UserForm, UserProfileForm, StoreGameForm
from game.models import *


def mainPage(request):
    """This will direct the user to the main page that provide additional
    actions (login, register, etc)"""
    return render(request, 'base.html')


def registerUser(request):
    #Funktio on lähes kokonaan kopioitu www.tangowithdjango.com/ tutoriaalista

    registered = False
    if request.method == 'POST':

        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)

            #KOMMENTOI POIS SEURAAVAT KAKSI RIVIÄ, JOS ET HALUA ERIKSEEN AKTIVOIDA ACCOUNTTIA!
            user.is_active = False
            sendConfirmEmail(user)

            user.save()
            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            #if 'picture' in request.FILES:
            #   profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print(user_form.errors, profile_form.errors)

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    if not registered:
        return render(request,
            'register.html',
            {
                'user_form': user_form,
                'profile_form': profile_form,
            }
        )
    else:
        return render(request,
            'message.html',
            {
                'title': "Thank you for registering!",
                'message': "Please check you email in order to activate the account.",
            }
        )


def loginUser(request):
    #Funktio on lähes kokonaan kopioitu www.tangowithdjango.com/ tutoriaalista

    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/game/')
            else:
                # An inactive account was used - no logging in!
                return render(request, 'message.html',
                    {
                        'title': "Account not activated",
                        'message': "Please check your email and activate your account before logging in."
                    })
        else:
            # Bad login details were provided. So we can't log the user in.
            print ("Invalid login details: {0}, {1}".format(username, password))
            return render(request, 'message.html',
                {
                    'title': "Invalid login details supplied",
                    'message': "Please check your login information and try again."
                })

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
            # blank dictionary object...
            context['request'] = request
            context['user'] = request.user
            # If the user is authenticated, we'll sent the user to homepage
            if request.user.is_authenticated():
                return HttpResponseRedirect('/game/')
            return render_to_response('login.html', {}, context)


# Sends email confirmation to newly registered user
# email backend configuration found in gameshop/settings.py
def sendConfirmEmail(user):

    tag = user.username + "_" + str(user.id)
    receiver = user.email
    host = "WSD Gameshop"
    url = "http://localhost:8000/game/confirmRegistration/" + tag
    subject = "Please activate your registration"
    message = "Hi " + user.username + "!\nPlease activate your account here:\n" + url
    send_mail(subject, message, host, [receiver], fail_silently=False)


# User is accessing this url via the confirmation email
# checks if the user account related to url parameters exists
#and activates the user account
def confirmRegistration(request, tag):

    try:
        temp = tag.split("_")
        RegUser = User.objects.get(username=temp[0], id=int(temp[1]))
    except:
        return HttpResponse("No user found!")

    RegUser.is_active = True
    RegUser.save()
    return render(request, "message.html",
        {
            "title": "Account is now activated!",
            "message": "Please login to continue.",
            "linkUrl": "/game/login/",
            "linkText": "Login"
        }
    )


def ourGame(request):
    return render(request, 'our_game.html')


# ALL VIEWS WHICH REQUIRE LOGGING IN SHOULD BE PLACES BELOW THIS LINE ##


#Renders the shop view, where users can buy and play games
@login_required
def gameShop(request):

    context = RequestContext(request)
    context['genres'] = GameGenre.objects.all()
    ownedGamesQuery = UserGame.objects.filter(owner=request.user)
    context['ownedGamesObjects'] = ownedGamesQuery

    # Get list of owned game ids in order to remove them from the available games
    ownedGameIds = []
    for game in ownedGamesQuery:
        ownedGameIds.append(int(game.game.id))

    if request.is_ajax():

        # post variables
        priceRange = request.POST['priceRange']
        ordering = request.POST['ordering']
        searchField = request.POST['searchField']
        # Notice the getlist() method that has to be used for javascript arrays
        genreSelections = request.POST.getlist('genreSelections[]')

        # Define the price range parameter
        if priceRange == "Any":
            gteV = 0
            lteV = 99999
        else:
            minMax = priceRange.split("-")
            gteV = int(minMax[0])
            lteV = int(minMax[1])+1

        # Define the ordering parameter
        orderingString = "title"
        if ordering == "Title":
            orderingString = "title"
        elif ordering == "Price (Descending)":
            orderingString = "-price"
        elif ordering == "Price (Ascending)":
            orderingString = "price"
        elif ordering == "Newest":
            orderingString = "-relDate"
        elif ordering == "Oldest":
            orderingString = "relDate"
        elif ordering == "Rating":
            orderingString = "-avgRate"

        # If searched by title get games that contain the value of search field
        if not searchField.isspace():
            games = StoreGame.objects.filter(title__contains=searchField)
        else:
            games = StoreGame.objects.all()

        # Filter out genres that are not selected
        games = games.filter(genre__genre__in=genreSelections)

        # Filter out games that don't fall into the price range
        if priceRange != "Any":
            games = games.filter(price__lt=lteV, price__gte=gteV)
        games = games.order_by(orderingString)

        # Remove already owned games
        games = games.exclude(id__in=ownedGameIds)

        context['storeGamesObjects'] = games
        return render_to_response('available_games.html', context)

    games = StoreGame.objects.all().order_by('title')
    games = games.exclude(id__in=ownedGameIds)
    context['storeGamesObjects'] = games
    return render_to_response('shop.html', context)


@login_required
def logoutUser(request):
    logout(request)
    return HttpResponseRedirect('/game/')


#Modify existing StoreGame object
@login_required
def modifyGame(request, game_id):

    context = RequestContext(request)
    done = False
    obj = get_object_or_404(StoreGame, id=game_id, author=context['user'])
    storegame_form = StoreGameForm(request.POST or None, request.FILES or None, instance=obj)

    if request.method == 'POST':
        if storegame_form.is_valid():
            # Save the user's form data to the database.
            storegame_form.save()
            done = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print(storegame_form.errors)

            # Not a HTTP POST, so we render our form using the StoreGameForm instance.
            # Thiis form will be blank, ready for user input.

    # Render the template depending on the context.
    if not done:
        return render_to_response(
            'modify_game.html',
            {'form': storegame_form, 'id': game_id},
            context)
    else:
        return render(request, "message.html",
            {
                "title": "Game Modification Succesful!",
                "message": "Your modification have been saved."
            }
        )


#Save new StoreGame object to the database
@login_required
def registerNewGame(request):

    context = RequestContext(request)
    context['profile'] = get_object_or_404(UserProfile, user=context['user'])

    if context['profile'].isDeveloper == 1:
        done = False
        if request.method == 'POST':

            storegame_form = StoreGameForm(data=request.POST)

            if storegame_form.is_valid():
                # Save the user's form data to the database.
                context = RequestContext(request)
                username = context['user']

                # The author name is inferred from the login details. This is then
                # inserted into the model. Note the commit=False as described in
                # https://docs.djangoproject.com/en/1.7/topics/forms/modelforms/
                new_game = storegame_form.save(commit=False)
                new_game.author = username
                new_game.lastPlayed = ""
                new_game.ratingPoints = 0
                new_game.rates = 0
                new_game.save()
                done = True

                addedGame = StoreGame.objects.get(author=context['user'], title=new_game.title)
                gameToUserGames = UserGame(game_id=addedGame.id, owner_id=addedGame.author.id)
                gameToUserGames.save()

            # Invalid form or forms - mistakes or something else?
            # Print problems to the terminal.
            # They'll also be shown to the user.
            else:
                print(storegame_form.errors)

                # Not a HTTP POST, so we render our form using the StoreGameForm instance.
                # Thiis form will be blank, ready for user input.
        else:
            storegame_form = StoreGameForm()

        # Render the template depending on the context.
        if not done:
            return render_to_response(
                'register_game.html',
                {'form': storegame_form, 'done': False},
                context)
        else:
            return render(request, "message.html",
                {
                    "title": "Game Registration Succesful!",
                    "message": "Your game is now available in the shop. You can manage your games in the profile section."
                }
            )
    else:
        return HttpResponse("You are not authorized to register new games!<br><a href=\"http://localhost:8000/game/\">Return to Homepage</a>")


#User profile page, normal users can view their games and personal info
#Developer users can add and modify their games
@login_required
def userProfile(request):

    if request.method == 'POST' and request.POST['type'] == 'REMOVE':
        StoreGame.objects.filter(id=int(request.POST['game_id'])).delete()
        return HttpResponse("Game removed!")

    else:
        context = RequestContext(request)
        context['profile'] = get_object_or_404(UserProfile, user=context['user'])
        context['ownedGames'] = UserGame.objects.filter(owner=context['user'])

        if context['profile'].isDeveloper == 1:
            gameData = StoreGame.objects.filter(author=context['user'])
            context['createdGames'] = gameData
            gameSales = {}
            for m in gameData:
                usergame = UserGame.objects.filter(game__title=m.title, game__author__username=context['user']).order_by('-id')

                data = []
                data.append(usergame.count())
                if usergame.count() > 0:
                    latest = UserGame.objects.filter(game__title=m.title, game__author__username=context['user']).latest()
                    data.append(latest.purDate)
                else:
                    data.append("None")

                gameSales[m.title] = data

            context['salesData'] = gameSales

        # profile = get_object_or_404(UserProfile, user=context.user)
        # context['profile'] = profile
        return render_to_response('profile.html', context)


#Renders the gameplay view with iFrame
@login_required
def playGame(request, game_id):

    if request.method == 'POST':

        if request.POST['type'] == 'FBPOST':
            game = get_object_or_404(StoreGame, id=game_id)
            #gameTitle = game.title
            context = RequestContext(request)
            user = context['user']
            #social = user.social_auth.get(provider='facebook')
            #graph = GraphAPI(social.extra_data['access_token'])
            #linkUrl = "www.yle.fi"  # Change to heroku url when deployed
            #highScore = user.user_scores.filter(game__id=game_id).order_by("-score")[:1][0].score
            #statusMessage = "Can you beat my score " + str(highScore) + " on " + gameTitle + "?"
            #graph.post(path='me/feed', link = linkUrl, message = statusMessage)
            return HttpResponse("POSTED")

        elif request.POST['type'] == 'SCORE':

            score = int(request.POST['score'])
            game = int(request.POST['game'])
            user = int(request.POST['user'])
            newscore = GameScore(game_id=game, player_id=user, score=score)
            newscore.save()
            return HttpResponse("Score saved successfully!")

        elif request.POST['type'] == 'SAVE':

            data = request.POST['data']
            game = int(request.POST['game'])
            user = int(request.POST['user'])

            if GameSave.objects.filter(game_id=game, user_id=user).exists():
                GameSave.objects.filter(game_id=game, user_id=user).update(saveData=data)

            else:
                newsave = GameSave(game_id=game, user_id=user, saveData=data)
                newsave.save()

            return HttpResponse("Savefile saved successfully!")

        elif request.POST['type'] == 'LOAD':
            game = int(request.POST['game'])
            user = int(request.POST['user'])

            if GameSave.objects.filter(game_id=game, user_id=user).exists():
                result = get_object_or_404(GameSave, game_id=game, user_id=user)
                return HttpResponse(result.saveData)
            else:
                return HttpResponse("")

        elif request.POST['type'] == 'RATE':

            newRate = int(request.POST['newRate'])
            user = int(request.POST['user'])
            game = int(request.POST['game'])
            userGame = UserGame.objects.get(game__id=game, owner__id=user)
            userGame.rating = newRate
            userGame.save()

            # Calculate the average rating for this game
            ratings = UserGame.objects.filter(game__id=game_id).exclude(rating__isnull=True)
            if not ratings.exists():
                avgRate = None
            else:
                avgRate = ratings.aggregate(Avg('rating'))['rating__avg']
            storeGame = StoreGame.objects.get(id=game)
            storeGame.avgRate = avgRate
            storeGame.save()

            return HttpResponse("Game rated")

    else:
        context = RequestContext(request)
        user = context['user']
        game = get_object_or_404(StoreGame, id=game_id)

        # Check if the user already owns the game
        if UserGame.objects.filter(game_id=game.id, owner_id=user.id).count() == 0:
            return HttpResponse("You don't own this game!<br><a href=\"http://localhost:8000/game/\">Return to Homepage</a>")

        userGame = get_object_or_404(UserGame, game_id=game, owner_id=user)
        userGame.lastPlayed = datetime.now()
        userGame.save()
        context['game'] = game
        context['userGame'] = userGame

        # Fetch the average rating for this game
        avgRate = StoreGame.objects.get(id=game_id).avgRate
        context['avgRate'] = avgRate

        # Fetch the game highscores
        globalHighscores = StoreGame.objects.get(id=game_id).high_scores.order_by("-score")[:5]
        context['globalHighscores'] = globalHighscores

        # Fetch the personal highscores
        personalHighscores = user.user_scores.filter(game__id=game_id).order_by("-score")[:5]
        context['personalHighscores'] = personalHighscores

        context['profile'] = get_object_or_404(UserProfile, user=context['user'])

        return render_to_response('play.html', context)


#Views below connect the GameShop to payment service
#Custom pid is used to confirm the authenticy of the payment
@login_required
def buyGame(request, game_id):

    context = RequestContext(request)
    user = context['user']
    game = get_object_or_404(StoreGame, id=game_id)
    pid = user.username + "_" + str(game.id) + "_" + str(time.time())
    amount = game.price
    sid = "ajl2014wsdproject"  # uniikki nimi
    secret_key = "95dd5f4a942e5678da687f1a6c86d8f3"  # uniikki avain

    success_url = "http://localhost:8000/game/paymentSuccessful/"
    error_url = "http://localhost/game/paymentFailed/"
    cancel_url = "http://localhost:8000/game/paymentCancelled"

    checksumstr = "pid=%s&sid=%s&amount=%s&token=%s" % (pid, sid, amount, secret_key)

    m = hashlib.md5(checksumstr.encode('utf-8')).hexdigest()

    context['pid'] = pid
    context['sid'] = sid
    context['amount'] = amount
    context['checksum'] = m
    context['success_url'] = success_url
    context['cancel_url'] = cancel_url
    context['error_url'] = error_url
    context['game'] = game
    context['checksumstr'] = checksumstr
    return render_to_response('buy.html', context)


@login_required
def paymentSuccessful(request):

    context = RequestContext(request)
    pid = request.GET.get('pid', '').split("_")
    game_id = int(pid[1])
    buyer = pid[0]
    game = get_object_or_404(StoreGame, id=game_id)

    user = context['user']

    # Check if the user is trying to use someone else's payment_successful url
    if str(user) != str(buyer):
        text = "Hey that's stealing!<br><a href=\"http://localhost:8000/game/\">Return to Homepage</a>"

    # Check if the user already owns the game
    elif UserGame.objects.filter(game_id=game.id, owner_id=user.id).count() == 0:

        paidgame = UserGame(game_id=game.id, owner_id=user.id)
        paidgame.save()

        title = "Payment successful!"
        text = "Go play your new game!"
        url = "/game/shop/"
        linkText = "Return to game view"

    else:
        title = "You already own that game!"
        url = "/game/"
        linkText = "Return to homepage"

    return render(request, "message.html",
        {
            "title": title,
            "message": text,
            "linkUrl": url,
            "linkText": linkText
        }
    )


@login_required
def paymentCancelled(request):
    title = "Payment cancelled!"
    url = "/game/shop/"
    linkText = "Return to game view"
    return render(request, "message.html",
        {
            "title": title,
            "linkUrl": url,
            "linkText": linkText
        }
    )


@login_required
def paymentFailed(request):

    title = "Payment failed!"
    text = "Not enough money? Go work!"
    url = "/game/shop/"
    linkText = "Return to game view"

    return render(request, "message.html",
        {
            "title": title,
            "message": text,
            "linkUrl": url,
            "linkText": linkText
        }
    )


#REST API to receive shop info and gamescores in JSON
@login_required
def jsonData(request, JSONtype="", arg=""):
    context = RequestContext(request)
    user = context['user']

    if JSONtype == "" and arg == "":
        info = ("<p>genre = shows all games specfied genre. If genre is \"all\", lists all games in store.<br>score"
        "= Shows all players and their scores for specified game"
        "<br>developer= shows games created by specified author. Also shows sales statistics<br></p><p>"
        "Example of use:<br><br>json/genre/\"genre_name_here\"/<br>json/score/\"game_id_here\"/"
        "<br>json/developer/\"author_name_here\"/</p>")
        return HttpResponse(info)

    json_data = {}

    if JSONtype == "genre":
        if arg == 'all':

            data = StoreGame.objects.all()
            for n in data:
                name = n.title
                json_data[name] = {
                    'title': n.title,
                    'description': n.desc,
                    'author': n.author.username,
                    'relDate': str(n.relDate),
                    'price': str(n.price),
                    'genre': n.genre.genre
                }
        elif arg == '':
            return HttpResponse("Please specify genre.")
        else:
            data = StoreGame.objects.filter(genre__genre=arg)
            if data:
                json_data['genre'] = arg
                games = []
                for n in data:
                    games.append(n.title)
                json_data['games'] = games

            else:
                return HttpResponse("No data found with given arguments.")

        return HttpResponse(json.dumps(json_data), content_type="application/json")

    elif JSONtype == "score":
        data = GameScore.objects.filter(game_id=arg)
        if data:
            json_data['game'] = arg
            scores = []
            for n in data:
                temp = n.player.username + " : " + str(n.score)
                scores.append(temp)
            json_data['scores'] = scores
            return HttpResponse(json.dumps(json_data), content_type="application/json")
        else:
            return HttpResponse("No data found with given arguments.")

    elif JSONtype == "developer":
        if user.username == arg:
            data = StoreGame.objects.filter(author__username=arg)

            if data:
                json_data['author'] = arg
                createdGames = []
                for n in data:
                    createdGames.append(n.title)
                json_data['Created Games'] = createdGames

                gameSales = []
                for m in createdGames:
                    count = UserGame.objects.filter(game__title=m, game__author__username=arg).count()
                    #gameSales.append( m + " sold: " + str(count) + " pcs" )
                    gameSales.append(count)
                json_data['Created Games'] = createdGames
                json_data['Nro of games sold by title'] = gameSales
                return HttpResponse(json.dumps(json_data), content_type="application/json")
            else:
                return HttpResponse("No data found with given arguments.")
        else:
            return HttpResponse("You are only allowed to see your own developer statistics.")

    else:
        return HttpResponse("Wrong search arguments.")
