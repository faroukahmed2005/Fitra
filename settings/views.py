from django.shortcuts import render
from . import models 

def home(request):
    info = models.Info.get_solo()
    brief = models.Brief.get_solo()
    about_us = models.AboutUs.get_solo()
    social_links = models.SocialLinks.get_solo()
    successful_stories = models.SuccessfullStories.objects.all().order_by('-id')[:10]
    packages = models.Packages.objects.prefetch_related('packagefeature_set__feature').all()

    return render(request, 'settings/home.html', {
        'info': info,
        'brief': brief,
        'about_us': about_us,
        'social_links': social_links,
        'successful_stories':successful_stories,
        'packages':packages,
    })