from datetime import date

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from django.views.decorators.http import require_GET

from .forms import RegistrationForm
from .models import Member, PendingRegistration
from .services import (
    activate_pending_registration,
    check_duplicate_email,
    create_pending_registration,
    _delete_pending_picture_files,
)

signer = TimestampSigner()


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            data = form.cleaned_data
            reg_type: str = data.get('registration_type', 'New')
            current_language: str = request.LANGUAGE_CODE

            if reg_type == 'New':
                # ---- New path: check for duplicate email before proceeding ----
                email: str | None = data.get('email')
                if check_duplicate_email(email):
                    form.add_error(
                        'email',
                        'هذا البريد الإلكتروني مستخدم بالفعل. الرجاء استخدام بريد آخر.'
                        if current_language == 'ar'
                        else 'This email is already in use. Please use another email.',
                    )
                    return render(
                        request,
                        'members/form.html',
                        {'form': form, 'today': date.today()},
                    )

                result = create_pending_registration(data, request, renewal_target_member_id=None)

                if result.email_sent:
                    success_message: str = (
                        'تحقق من بريدك الإلكتروني لتفعيل الحساب.'
                        if current_language == 'ar'
                        else 'Check your email to activate your account.'
                    )
                elif not result.email_sent and result.email_error:
                    success_message = (
                        'فشل إرسال البريد الإلكتروني. الرجاء المحاولة مرة أخرى أو التواصل مع الدعم.'
                        if current_language == 'ar'
                        else f'Account created but email failed to send. Please contact support. Error: {result.email_error}'
                    )
                else:
                    success_message = (
                        'لم يتم توفير بريد إلكتروني للتفعيل.'
                        if current_language == 'ar'
                        else 'No email provided for activation.'
                    )

            else:
                # ---- Renewal path: identity established by member_id ----
                # Email is retrieved from the existing Member by the service layer.
                # We do NOT run check_duplicate_email here — doing so against
                # the member's own stored email would always return True (they're
                # already confirmed), causing a false "email already in use" error.
                member_id: int = data['member_id']
                result = create_pending_registration(
                    data, request, renewal_target_member_id=member_id
                )

                if result.email_sent:
                    success_message = (
                        'تم إرسال رابط التجديد إلى بريدك الإلكتروني المسجّل. تحقق منه لتفعيل التجديد.'
                        if current_language == 'ar'
                        else 'A renewal link has been sent to your registered email. Check it to activate your renewal.'
                    )
                else:
                    success_message = (
                        'فشل إرسال البريد الإلكتروني. الرجاء المحاولة مرة أخرى أو التواصل مع الدعم.'
                        if current_language == 'ar'
                        else f'Renewal created but email failed to send. Please contact support. Error: {result.email_error}'
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

        # Form is invalid — re-render with errors
        return render(
            request,
            'members/form.html',
            {'form': form, 'today': date.today()},
        )

    # GET request
    return render(
        request,
        'members/form.html',
        {'form': RegistrationForm(), 'today': date.today()},
    )


@require_GET
def activate_account(request: HttpRequest, token: str) -> HttpResponse:
    try:
        raw_id: str = signer.unsign(token, max_age=60 * 60 * 24)
        pending_id: int = int(raw_id)
        pending: PendingRegistration = PendingRegistration.objects.get(id=pending_id)

        # Race-condition guard: only applies to the New path.
        # For Renewal path, the email is already confirmed on the existing Member
        # and we're updating (not creating), so skip the "email taken" guard.
        if pending.renewal_target_member_id is None:
            if Member.objects.filter(email=pending.email, email_confirmed=True).exists():
                preferred_language: str = pending.preferred_language
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


def ratelimited_view(request: HttpRequest, exception: Ratelimited) -> HttpResponse:
    message: str = (
        'لقد قمت بمحاولات كثيرة جداً. الرجاء المحاولة لاحقاً.'
        if request.LANGUAGE_CODE == 'ar'
        else 'Too many attempts. Please try again later.'
    )
    return render(request, 'members/form.html', {
        'form': RegistrationForm(),
        'error_message': message,
        'today': date.today(),
    }, status=429)
