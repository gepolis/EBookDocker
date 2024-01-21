from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Account, Building


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Почта")
    class Meta:
        model = Account
        fields = (
        "username", "email", "second_name", "first_name", "middle_name", "password1", "password2", "building","role")
        labels = {
            "username": "Имя пользователя",
            "second_name": "Фамилия",
            "first_name": "Имя",
            "middle_name": "Отчество",
            "password1": "Пароль",
            "password2": "Подтверждение пароля",
            "building": "Учебный корпус",
        }
        widgets = {
            'username': forms.TextInput(attrs={'onkeydown': "check_form_valid()"}),
            'role': forms.HiddenInput(),
        }

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if user.role not in ["student", "teacher"]:
            user.role=None
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

class AccountSignInForm(AuthenticationForm):
    username = forms.CharField(label='Логин')
    password = forms.CharField(widget=forms.PasswordInput(), label='Пароль')

    class Meta:
        model = Account
        fields = ['username', 'password']

class AccountMosRuForm(forms.Form):
    login = forms.CharField(label="Почта или номер телефона")
    password = forms.CharField(widget=forms.PasswordInput(), label='Пароль')
class NewBuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ("name", "type")
        labels = {
            "name": "Название",
            "type": "Тип"
        }

    def save(self, commit=True):
        user = super(NewBuildingForm, self).save(commit=False)
        if commit:
            user.save()
        return user
