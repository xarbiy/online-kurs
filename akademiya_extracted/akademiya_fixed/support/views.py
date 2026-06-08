from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import SupportTicket, TicketReply
from .forms import SupportTicketForm, TicketReplyForm


DEFAULT_FAQ = [
    {"q": "Kursga qanday yozilaman?", "a": "Kurslar bo'limiga o'ting, qiziqtirgan kursni tanlang va 'Kursga yozilish' tugmasini bosing."},
    {"q": "Parolimni unutdim, nima qilaman?", "a": "Login sahifasida 'Parolni unutdim' havolasini bosing va email manzilingizga ko'rsatma yuboriladi."},
    {"q": "Telegram orqali ro'yxatdan o'tish qanday ishlaydi?", "a": "Ro'yxatdan o'tish sahifasida 'Telegram bilan' tugmasini bosing, ma'lumotlaringizni to'ldiring, so'ng botga o'tib telefon raqamingizni yuboring. Bot sizga 6 xonali kod yuboradi."},
    {"q": "Kod muharririda qaysi tillar qo'llab-quvvatlanadi?", "a": "Python, JavaScript, Java, C++, C tillarida kod yozish va ishlatish mumkin. SQL, HTML, CSS uchun faqat saqlash imkoniyati mavjud."},
    {"q": "Sertifikat olish mumkinmi?", "a": "Ha, kursni to'liq tugatgach sertifikat olish imkoniyati mavjud. Buni profil bo'limidan ko'rishingiz mumkin."},
]


@login_required
def ticket_list(request):
    tickets = SupportTicket.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "support/ticket_list.html", {
        "tickets": tickets,
        "default_faq": DEFAULT_FAQ,
    })


@login_required
def create_ticket(request):
    if request.method == "POST":
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, f"Ticketingiz #{ticket.ticket_number} raqami bilan yuborildi!")
            return redirect("ticket_detail", pk=ticket.pk)
    else:
        form = SupportTicketForm()
    return render(request, "support/create_ticket.html", {"form": form})


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(SupportTicket, pk=pk, user=request.user)
    replies = ticket.replies.all()

    if request.method == "POST":
        if ticket.status == SupportTicket.STATUS_CLOSED:
            messages.error(request, "Yopilgan ticketga javob yozib bo'lmaydi.")
            return redirect("ticket_detail", pk=pk)
        form = TicketReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.ticket = ticket
            reply.user = request.user
            reply.is_staff_reply = request.user.is_staff
            reply.save()
            # Ticket statusini yangilash
            if ticket.status == SupportTicket.STATUS_RESOLVED:
                ticket.status = SupportTicket.STATUS_OPEN
                ticket.save()
            messages.success(request, "Javobingiz yuborildi.")
            return redirect("ticket_detail", pk=pk)
    else:
        form = TicketReplyForm()

    return render(request, "support/ticket_detail.html", {
        "ticket": ticket,
        "replies": replies,
        "form": form,
    })


@login_required
def close_ticket(request, pk):
    ticket = get_object_or_404(SupportTicket, pk=pk, user=request.user)
    if ticket.status != SupportTicket.STATUS_CLOSED:
        ticket.status = SupportTicket.STATUS_CLOSED
        ticket.resolved_at = timezone.now()
        ticket.save()
        messages.info(request, "Ticket yopildi.")
    return redirect("ticket_detail", pk=pk)
