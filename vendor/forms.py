from django import forms
from .models import Vendor, BusinessHour

class BusinessHourForm(forms.ModelForm):
    
    class Meta:
        model = BusinessHour
        fields = ["day", "is_open", "open_time", "close_time"]
        widgets = {
            "day":forms.HiddenInput(),
            "open_time":forms.TimeInput(attrs={
                "class":"ring-2 ring-solid ring-gray-400 rounded px-2 py-1 focus:outline-none focus:border-none focus-within:ring-2 focus-within:ring-burntOrange-700",
                "type":"time"
            }),
            "close_time":forms.TimeInput(attrs={
                "class":"ring-2 ring-solid ring-gray-400 rounded px-2 py-1 focus:outline-none focus:border-none focus-within:ring-2 focus-within:ring-burntOrange-700",
                "type":"time"
            })
        }

    def has_changed(self):
        # A form with a day field is always considered to have changed.
        # This forces Django to process forms for days that were not checked.
        if 'day' in self.initial:
            return True
        return super().has_changed()


BaseOpenFormset = forms.inlineformset_factory(
    Vendor,
    BusinessHour,
    form = BusinessHourForm,
    fields = ["day", "is_open", "open_time", "close_time"],
    extra = 0,
    can_delete = False,
)

class BusinessHourFormSet(BaseOpenFormset):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # check if there are already 7 forms
        if self.queryset.count() < 7:
            # get existing days
            existing_days = self.queryset.values_list("day", flat=True)
            

            days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
            
            # create a form instance for each missing day
            for day in days:
                if day not in existing_days:
                    # Add a new form instance
                    form = self._construct_form(len(self.forms))
                    form.initial['day'] = day
                    self.forms.append(form)

        # label each form with day of the week
        for form in self.forms:
            # `form.initial.get("day")` handles existing form
            # `form.data.get(...)` handles new form submissions
            day_index = form.initial.get("day") or form.data.get(form.prefix + "-day")

            if day_index is not None:
                # form.fields["is_open"].label = BusinessHour.Days[day_index][1]
                form.fields["is_open"].label = BusinessHour.Days(day_index).label
