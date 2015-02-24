from django.conf.urls import *
from game.views import *


urlpatterns = patterns('',
    #URL to the main page
    url(r"^$", mainPage),
    url(r'^register/$', registerUser, name='register'),
    url(r'^register_game/$', registerNewGame, name='register_game'),
    url(r'^modify_game/(?P<game_id>[0-99]+)/$', modifyGame, name='modify_game'),
    url(r'^confirmRegistration/(?P<tag>[-\w]+)', confirmRegistration, name='confirm_reg'),
    url(r'^login/$', loginUser, name='login'),
    url(r'^logout/$', logoutUser, name='logout'),
    url(r'^profile/$', userProfile, name='profile'),
    url(r'^shop/$', gameShop, name='shop'),
    url(r'^shop/buy/(?P<game_id>[0-99]+)/$', buyGame, name='buy_game'),
    url(r'^paymentSuccessful/*', paymentSuccessful, name='payment_successful'),
    url(r'^paymentCancelled/*', paymentCancelled, name='payment_cancelled'),
    url(r'^paymentFailed/*', paymentFailed, name='payment_failed'),
    url(r'^play/(?P<game_id>[0-99]+)/$', playGame, name='play_game'),
    url(r'^json/$', jsonData, name='json_info'),
    url(r'^json/(?P<JSONtype>[-\w]+)/(?P<arg>[-\w]+)/$', jsonData, name='json_data'),
    url(r'^our_game/$', ourGame, name='our_game'),
    # url(r'^404/$',error_404),
)
