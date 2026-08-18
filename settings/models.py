from django.db import models
from solo.models import SingletonModel

class Info(SingletonModel):
    logo = models.ImageField(verbose_name = 'Logo', upload_to = 'settings/')
    slogan = models.CharField(verbose_name ='Slogan', max_length = 200 )

class Brief(SingletonModel): 
    brief_title = models.CharField(verbose_name ='Brief Title', max_length = 100 )
    brief_content = models.TextField(verbose_name ='Brief')
    brief_image = models.ImageField(verbose_name = 'Brief Image', upload_to ='settings/') 

class AboutUs(SingletonModel):
    about_us_content =  models.TextField(verbose_name ='About Us')
    about_us_image = models.ImageField(verbose_name ='About US Image', upload_to='settings/')

class SocialLinks(SingletonModel):
    youtube = models.URLField(verbose_name ='Youtube Link', max_length = 100, blank=True)  
    whatsapp = models.URLField(verbose_name ='Whatsapp Link', max_length = 100, blank=True)   
    facebook = models.URLField(verbose_name ='Facebook Link', max_length = 100, blank=True)
    instagram = models.URLField(verbose_name ='Instagram Link', max_length = 100, blank=True)
    instagram_page = models.URLField(verbose_name ='Instagram Page Link', max_length = 100, blank=True)
    tiktok = models.URLField(verbose_name ='Tiktok Link', max_length = 100, blank=True)
    telegram = models.URLField(verbose_name ='Telegram Link', max_length = 100, blank=True)

class SuccessfullStories(models.Model):
    name = models.CharField(verbose_name = 'Name', max_length = 200)
    before_image = models.ImageField(verbose_name = 'Before Image', upload_to ='settings/') 
    after_image = models.ImageField(verbose_name = 'After Image', upload_to ='settings/') 
    def __str__(self):
        return self.name

class Feature(models.Model):
    text = models.TextField(verbose_name='Feature')

    def __str__(self):
        return self.text


class Packages(models.Model):
    name = models.CharField(verbose_name='Package', max_length=200)
    before_price = models.DecimalField(max_digits=10, decimal_places=2)
    after_price = models.DecimalField(max_digits=10, decimal_places=2)
    time = models.CharField(verbose_name='Duration', max_length=100)
    image = models.ImageField(verbose_name='Package Image', upload_to='settings/')
    features = models.ManyToManyField(Feature, through='PackageFeature', related_name='packages')

    def __str__(self):
        return self.name


class PackageFeature(models.Model):
    package = models.ForeignKey(Packages, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    is_included = models.BooleanField(default=True, verbose_name='Included in this package?')
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        unique_together = ('package', 'feature')
        ordering = ['order']

    def __str__(self):
        return f"{self.package.name} — {self.feature.text} ({'✓' if self.is_included else '✗'})"

