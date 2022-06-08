from django import forms

from users.models import Profile


class PersonalAccountEditForm(forms.ModelForm):
    """Форма для изменения данных в личном кабинете"""
    class Meta:
        model = Profile
        fields = ['username', 'first_name', 'last_name', 'email',
                  'comp_name', 'city', 'ogrn', 'phone_number', 'role',
                  'date_joined', 'bio']

    def __init__(self, *args, **kwargs):
        super(PersonalAccountEditForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['ogrn'].widget.attrs['readonly'] = True
        self.fields['role'].widget.attrs['readonly'] = True
        self.fields['date_joined'].widget.attrs['readonly'] = True
