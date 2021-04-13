from django.db import models
from django.db.models.fields.related import ForeignKey
from django.urls import reverse # Used to generate URLs by reversing the URL patterns

from django.contrib.auth.models import User
from django.db.models.deletion import SET_NULL
from django.db.models.fields import CharField, DecimalField
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal

"""
Everytime a model is changed in a way that affects the structure of data
    python3 manage.py makemigrations
    python3 manage.py migrate

When creating models register them on admin.py

To reset/clear database
1) Remove all migrations files from within project
    find . -path "*/migrations/*.py" -not -name "__init__.py" -delete; 
    find . -path "*/migrations/*.pyc"  -delete;
2) Delete database: rm db.sqlite3
3) Create inital migrations and generate database: makemigrations; migrate;
4) Create superuser: python manage.py createsuperuser
"""


class CommonInfo(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateField(auto_now_add=True, editable=False)
    updated_at = models.DateField(auto_now=True, editable=False)

    name = models.CharField(max_length=100, help_text='Enter name')
    description = models.TextField(blank=True, help_text='Enter description')

    class Meta:
        abstract = True
        ordering = ['name', '-updated_at']  # '-' reverses order, e.i. newest first


class Catalog(CommonInfo):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('catalog-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.name}'


class Record(CommonInfo):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    my_catalog = models.ForeignKey(Catalog, on_delete=models.CASCADE,
                                   verbose_name='Catalog')  # Many records to one Catalog. Deletes all records associated with deleted catalog.
    acquisition_date = models.CharField(max_length=100,
                                        help_text='Please use the following format: <em> YYYY - YYYY </em>', blank=True,
                                        default='Unknown')
    creation_date = models.CharField(max_length=100, help_text='Please use the following format: <em> YYYY </em>',
                                     blank=True, default='Unknown')
    

    manufacturer = models.ForeignKey('Manufacturer', null=True, blank=True, on_delete=SET_NULL)
    record_picture = models.ImageField(null=True, blank=True, upload_to="images/")

    condition_rating = DecimalField(
        verbose_name='Condition Rating (0 to 5)',
        default=0,
        decimal_places=2,
        max_digits=3,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('5'))]
    )
    condition_description = models.TextField(blank=True, help_text='Enter condition description')

    def get_absolute_url(self):
        return reverse('record-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.name} ({self.my_catalog})'


CUSTOMFIELD_TYPE = [
    ('char', 'CharField'),
    ('text', 'TextField'),
    ('bool', 'Boolean'),
    ('int', 'Integer'),
    ('dec', 'Decimal'),
]

class CustomField(models.Model):
    record = models.ForeignKey(Record, on_delete=models.CASCADE)

    field_label = models.CharField(blank=True, max_length=50)
    type = models.CharField(max_length=4, choices=CUSTOMFIELD_TYPE, default='char')

    cf_char = models.CharField(blank=True, max_length=100)
    cf_text = models.TextField(blank=True)
    cf_bool = models.BooleanField(blank=True, null=True)  # verbose_name='value'
    cf_int = models.IntegerField(blank=True, null=True)
    cf_dec = models.DecimalField(blank=True, null=True, max_digits=15, decimal_places=2)


class Provenance(models.Model):
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.CharField(max_length=100, help_text='Please use the following format: <em>YYYY - YYYY<\em>',
                            blank=True, default='Unknown')
    owner = models.CharField(max_length=100, help_text='Enter Owner', blank=True)
    nation = models.CharField(max_length=100, help_text='Enter Nation', blank=True)

    class Meta:
        # ordering = ['-date']
        pass

    def get_absolute_url(self):
        return reverse('provenance-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.record.name}-provenance-{self.id}'


class Manufacturer(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text='Enter name')

    def get_absolute_url(self):
        return reverse('manufacturer-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.name}'