from django.contrib.auth.forms import (
    PasswordResetForm,
)

class PwdResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)