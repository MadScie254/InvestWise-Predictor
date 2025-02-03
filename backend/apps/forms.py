from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django_countries.widgets import CountrySelectWidget
from .models import (
    Prediction,
    DataPoint,
    InvestmentPreference,
    RiskProfile,
    Notification,
    EconomicIndicator,
    SectorPerformance,
)


# ===========================
# 1. User-Related Forms
# ===========================

class CustomUserCreationForm(UserCreationForm):
    """
    Custom form for user registration.
    """
    phone_number = forms.CharField(max_length=15, required=False, help_text="Optional.")
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        help_text="Optional."
    )
    risk_tolerance = forms.ChoiceField(
        choices=User.RiskTolerance.choices,
        initial=User.RiskTolerance.MODERATE,
        help_text="Your tolerance for investment risks."
    )

    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'email',
            'password1',
            'password2',
            'first_name',
            'last_name',
            'phone_number',
            'date_of_birth',
            'risk_tolerance',
        ]

    def clean_email(self):
        """
        Ensure that the email is unique.
        """
        email = self.cleaned_data.get('email')
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom form for user login.
    """
    username = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={'autofocus': True})
    )

    def clean(self):
        """
        Allow users to log in using either username or email.
        """
        username_or_email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username_or_email and password:
            # Check if the input is an email
            if '@' in username_or_email:
                try:
                    user = get_user_model().objects.get(email=username_or_email)
                    self.user_cache = user
                except get_user_model().DoesNotExist:
                    pass
            else:
                # Default to username-based authentication
                super().clean()

        if not self.user_cache:
            raise ValidationError("Please enter a correct username/email and password.")

        return self.cleaned_data


class UserProfileForm(forms.ModelForm):
    """
    Form for managing user profile information.
    """
    class Meta:
        model = get_user_model()
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'date_of_birth',
            'risk_tolerance',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }


# ===========================
# 2. Core Model Forms
# ===========================

class PredictionForm(forms.ModelForm):
    """
    Form for creating and updating predictions.
    """
    sector = forms.CharField(
        max_length=255,
        help_text="The industry or sector being analyzed (e.g., Technology, Agriculture)."
    )
    country = forms.ChoiceField(
        choices=[],
        widget=CountrySelectWidget(),
        help_text="The country or region for the prediction."
    )

    class Meta:
        model = Prediction
        fields = ['sector', 'country']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate the country field with available countries
        self.fields['country'].choices = [(c.code, c.name) for c in CountrySelectWidget.countries]

    def clean_sector(self):
        """
        Validate the sector field.
        """
        sector = self.cleaned_data.get('sector')
        if not sector.strip():
            raise ValidationError("Sector cannot be empty.")
        return sector


class DataPointForm(forms.ModelForm):
    """
    Form for creating and updating data points.
    """
    indicator = forms.CharField(
        max_length=255,
        help_text="The type of economic indicator (e.g., GDP, Inflation)."
    )
    value = forms.FloatField(
        min_value=0,
        help_text="The numerical value of the data point."
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="The date associated with the data point."
    )
    country = forms.ChoiceField(
        choices=[],
        widget=CountrySelectWidget(),
        help_text="The country or region for the data point."
    )
    source = forms.CharField(
        max_length=255,
        help_text="The source of the data (e.g., World Bank, KNBS)."
    )

    class Meta:
        model = DataPoint
        fields = ['indicator', 'value', 'date', 'country', 'source']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate the country field with available countries
        self.fields['country'].choices = [(c.code, c.name) for c in CountrySelectWidget.countries]

    def clean_value(self):
        """
        Ensure the value is positive.
        """
        value = self.cleaned_data.get('value')
        if value <= 0:
            raise ValidationError("Value must be positive.")
        return value


class InvestmentPreferenceForm(forms.ModelForm):
    """
    Form for managing investment preferences.
    """
    preferred_sector = forms.CharField(
        max_length=255,
        required=False,
        help_text="Your preferred sector for investments (optional)."
    )
    preferred_country = forms.ChoiceField(
        choices=[],
        widget=CountrySelectWidget(),
        required=False,
        help_text="Your preferred country for investments (optional)."
    )
    risk_tolerance = forms.ChoiceField(
        choices=User.RiskTolerance.choices,
        required=False,
        help_text="Your tolerance for investment risks (optional)."
    )

    class Meta:
        model = InvestmentPreference
        fields = ['preferred_sector', 'preferred_country', 'risk_tolerance']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate the country field with available countries
        self.fields['preferred_country'].choices = [(c.code, c.name) for c in CountrySelectWidget.countries]


class RiskProfileForm(forms.ModelForm):
    """
    Form for managing risk profiles.
    """
    profile_type = forms.ChoiceField(
        choices=RiskProfile.ProfileType.choices,
        help_text="Your risk profile type (Conservative, Balanced, Aggressive)."
    )
    score = forms.IntegerField(
        min_value=0,
        max_value=100,
        help_text="Your risk score between 0 and 100."
    )
    description = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="A brief description of your risk profile (optional)."
    )

    class Meta:
        model = RiskProfile
        fields = ['profile_type', 'score', 'description']

    def clean_score(self):
        """
        Ensure the score is within the valid range.
        """
        score = self.cleaned_data.get('score')
        if score < 0 or score > 100:
            raise ValidationError("Score must be between 0 and 100.")
        return score


# ===========================
# 3. Supporting Model Forms
# ===========================

class EconomicIndicatorForm(forms.ModelForm):
    """
    Form for creating and updating economic indicators.
    """
    name = forms.CharField(
        max_length=255,
        help_text="The name of the economic indicator (e.g., GDP, Inflation)."
    )
    description = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="A brief description of the indicator (optional)."
    )
    unit = forms.CharField(
        max_length=50,
        help_text="The unit of measurement (e.g., %, USD)."
    )
    source = forms.CharField(
        max_length=255,
        help_text="The source of the indicator (e.g., World Bank, KNBS)."
    )

    class Meta:
        model = EconomicIndicator
        fields = ['name', 'description', 'unit', 'source']


class SectorPerformanceForm(forms.ModelForm):
    """
    Form for creating and updating sector performance data.
    """
    sector = forms.CharField(
        max_length=255,
        help_text="The name of the sector (e.g., Technology, Agriculture)."
    )
    growth_rate = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=0,
        help_text="The growth rate (%) of the sector."
    )
    market_size = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        help_text="The market size (USD) of the sector."
    )
    year = forms.PositiveIntegerField(
        help_text="The year of the performance data."
    )

    class Meta:
        model = SectorPerformance
        fields = ['sector', 'growth_rate', 'market_size', 'year']

    def clean_year(self):
        """
        Ensure the year is not in the future.
        """
        year = self.cleaned_data.get('year')
        current_year = datetime.now().year
        if year > current_year:
            raise ValidationError("Year cannot be in the future.")
        return year


# ===========================
# 4. Utility Functions
# ===========================

def validate_positive(value):
    """
    Validates that a value is positive.
    """
    if value <= 0:
        raise ValidationError("Value must be positive.")


def validate_year(value):
    """
    Validates that a year is not in the future.
    """
    current_year = datetime.now().year
    if value > current_year:
        raise ValidationError("Year cannot be in the future.")
