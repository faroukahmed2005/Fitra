from .forms import RegistrationForm
from django.shortcuts import render
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from .models import Member, PendingRegistration
from .services import (
    activate_pending_registration,
    check_duplicate_email,
    create_pending_registration,
    _delete_pending_picture_files,
)
from datetime import date
from django_ratelimit.decorators import ratelimit

signer = TimestampSigner()


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            data = form.cleaned_data
            email = data.get('email')

            if check_duplicate_email(email):
                form.add_error(
                    'email',
                    'هذا البريد الإلكتروني مستخدم بالفعل. الرجاء استخدام بريد آخر.'
                    if request.LANGUAGE_CODE == 'ar'
                    else 'This email is already in use. Please use another email.',
                )
                return render(
                    request,
                    'members/form.html',
                    {'form': form, 'today': date.today()},
                )

            result = create_pending_registration(data, request)
            current_language = request.LANGUAGE_CODE

            if email and result.email_sent:
                success_message = (
                    'تحقق من بريدك الإلكتروني لتفعيل الحساب.'
                    if current_language == 'ar'
                    else 'Check your email to activate your account.'
                )
            elif email and not result.email_sent:
                success_message = (
                    'فشل إرسال البريد الإلكتروني. الرجاء المحاولة مرة اخرى او التواصل مع الدعم.'
                    if current_language == 'ar'
                    else f'Account created but email failed to send. Please contact support. Error: {result.email_error}'
                )
            else:
                success_message = (
                    ' لم يتم توفير بريد إلكتروني للتفعيل.'
                    if current_language == 'ar'
                    else 'No email provided for activation.'
                )

            return render(
                request,
                'members/form.html',
                {
                    'form': RegistrationForm(),
                    'success_message': success_message,
                    'today': date.today(),
                },
            )

        return render(
            request,
            'members/form.html',
            {'form': form, 'today': date.today()},
        )

    return render(
        request,
        'members/form.html',
        {'form': RegistrationForm(), 'today': date.today()},
    )


def activate_account(request, token):
    try:
        raw_id = signer.unsign(token, max_age=60 * 60 * 24)
        pending_id = int(raw_id)
        pending = PendingRegistration.objects.get(id=pending_id)

        if Member.objects.filter(email=pending.email, is_activated=True).exists():
            preferred_language = pending.preferred_language
            _delete_pending_picture_files(pending)
            pending.delete()
            return render(
                request,
                'members/email_taken.html',
                {'preferred_language': preferred_language},
            )

        member = activate_pending_registration(pending)
        return render(request, 'members/activation_success.html', {'member': member})

    except SignatureExpired:
        preferred_language = 'en'
        try:
            raw_id = signer.unsign(token)
            pending_id = int(raw_id)
            pending = PendingRegistration.objects.filter(id=pending_id).first()
            if pending:
                preferred_language = pending.preferred_language
                _delete_pending_picture_files(pending)
                pending.delete()
        except Exception:
            pass
        return render(
            request,
            'members/activation_failed.html',
            {'preferred_language': preferred_language},
        )

    except (BadSignature, PendingRegistration.DoesNotExist):
        preferred_language = 'en'
        try:
            raw_id = signer.unsign(token)
            pending_id = int(raw_id)
            pending = PendingRegistration.objects.filter(id=pending_id).first()
            if pending:
                preferred_language = pending.preferred_language
                _delete_pending_picture_files(pending)
                pending.delete()
        except Exception:
            pass
        return render(
            request,
            'members/activation_failed.html',
            {'preferred_language': preferred_language},
        )


def ratelimited_view(request, exception):
    message = (
        'لقد قمت بمحاولات كثيرة جداً. الرجاء المحاولة لاحقاً.'
        if request.LANGUAGE_CODE == 'ar'
        else 'Too many attempts. Please try again later.'
    )
    return render(request, 'members/form.html', {
        'form': RegistrationForm(),
        'error_message': message,
        'today': date.today(),
    }, status=429)