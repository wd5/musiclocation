import datetime
from urllib2 import urlopen

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.forms.models import inlineformset_factory
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.utils import simplejson
from django.core import serializers

from songs.models import SongLocation
from songs.forms import SongLocationForm



def get_client_ip(request):
    """
    Get client IP, used to localize client
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_lat_lon_client(ip):
    """
    Get latitude and longitude based on freegeoip service
    """
    try:
        url = 'http://freegeoip.net/json/%s' % (ip)
        data = simplejson.load(urlopen(url))
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        if lat == 0.0 or lon == 0.0:
            lat, lon = 48.833, 2.333
        return lat, lon
    except:
        return 48.833, 2.333

def home(request):
    ip = get_client_ip(request)
    lat, lon = get_lat_lon_client(ip)
    form = None
    if request.user.is_authenticated():
        items = SongLocation.objects.filter(user = request.user)[0:20]
        json_serializer = serializers.get_serializer("json")()
        items_serialized = json_serializer.serialize(items, ensure_ascii=False)
        form = SongLocationForm()
    else:
        items = SongLocation.objects.none()
        items_serialized = []
    return render_to_response('index.html', {'lat':lat, 'lon':lon, 'items':items, 
                                             'items_serialized':items_serialized, 'form':form}, 
                              context_instance=RequestContext(request))

def all(request):
    items = SongLocation.objects.all()
    return render_to_response('all.html', {'items':items}, 
                 context_instance=RequestContext(request))

def logout_view(request):
    logout(request)
    return redirect('home')
    