#-*- coding: utf-8 -*-
from django import forms

class ProfileForm(forms.Form):
   
   picture = forms.FileFields()