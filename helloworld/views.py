from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from .models import Member, Book, Loan


def home(request):
    return render(request, 'helloworld/home.html', {
        'book_count': Book.objects.count(),
        'member_count': Member.objects.count(),
        'active_loans': Loan.objects.filter(return_date__isnull=True).count(),
    })


# ── Book CRUD ──

def book_list(request):
    books = Book.objects.all().order_by('title')
    return render(request, 'helloworld/book_list.html', {'books': books})


def book_create(request):
    if request.method == 'POST':
        Book.objects.create(
            title=request.POST['title'],
            author=request.POST['author'],
            genre=request.POST['genre'],
            total_copies=int(request.POST['total_copies']),
        )
        messages.success(request, 'Book added successfully.')
        return redirect('book_list')
    return render(request, 'helloworld/book_form.html', {'form_title': 'Add Book'})


def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.title = request.POST['title']
        book.author = request.POST['author']
        book.genre = request.POST['genre']
        book.total_copies = int(request.POST['total_copies'])
        book.save()
        messages.success(request, 'Book updated successfully.')
        return redirect('book_list')
    return render(request, 'helloworld/book_form.html', {'form_title': 'Edit Book', 'book': book})


def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    messages.success(request, 'Book deleted successfully.')
    return redirect('book_list')


# ── Member CRUD ──

def member_list(request):
    members = Member.objects.all().order_by('name')
    min_age = request.GET.get('min_age')
    max_age = request.GET.get('max_age')
    if min_age:
        members = members.filter(age__gte=int(min_age))
    if max_age:
        members = members.filter(age__lte=int(max_age))
    return render(request, 'helloworld/member_list.html', {
        'members': members,
        'min_age': min_age or '',
        'max_age': max_age or '',
    })


def member_create(request):
    if request.method == 'POST':
        Member.objects.create(
            name=request.POST['name'],
            age=int(request.POST['age']),
            email=request.POST['email'],
            membership_date=request.POST['membership_date'],
        )
        messages.success(request, 'Member added successfully.')
        return redirect('member_list')
    return render(request, 'helloworld/member_form.html', {'form_title': 'Add Member'})


def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        member.name = request.POST['name']
        member.age = int(request.POST['age'])
        member.email = request.POST['email']
        member.membership_date = request.POST['membership_date']
        member.save()
        messages.success(request, 'Member updated successfully.')
        return redirect('member_list')
    return render(request, 'helloworld/member_form.html', {'form_title': 'Edit Member', 'member': member})


def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    member.delete()
    messages.success(request, 'Member deleted successfully.')
    return redirect('member_list')


# ── Loan Management ──

def loan_list(request):
    loans = Loan.objects.select_related('member', 'book').all().order_by('-checkout_date')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')

    if start_date:
        loans = loans.filter(checkout_date__gte=start_date)
    if end_date:
        loans = loans.filter(checkout_date__lte=end_date)
    if status == 'active':
        loans = loans.filter(return_date__isnull=True, due_date__gte=date.today())
    elif status == 'overdue':
        loans = loans.filter(return_date__isnull=True, due_date__lt=date.today())
    elif status == 'returned':
        loans = loans.filter(return_date__isnull=False)

    return render(request, 'helloworld/loan_list.html', {
        'loans': loans,
        'start_date': start_date or '',
        'end_date': end_date or '',
        'status': status or '',
    })


def loan_create(request):
    if request.method == 'POST':
        member = get_object_or_404(Member, pk=request.POST['member_id'])
        book = get_object_or_404(Book, pk=request.POST['book_id'])

        if book.total_copies <= 0:
            messages.error(request, 'No copies available for this book.')
            return redirect('loan_create')

        # Transaction: atomically create loan and decrement copies
        with transaction.atomic():
            Loan.objects.create(
                member=member,
                book=book,
                checkout_date=request.POST['checkout_date'],
                due_date=request.POST['due_date'],
            )
            book.total_copies -= 1
            book.save()

        messages.success(request, f'"{book.title}" checked out to {member.name}.')
        return redirect('loan_list')

    today = date.today()
    return render(request, 'helloworld/loan_form.html', {
        'members': Member.objects.all().order_by('name'),
        'books': Book.objects.filter(total_copies__gt=0).order_by('title'),
        'today': today.isoformat(),
        'due_date': (today + timedelta(days=14)).isoformat(),
    })


def loan_return(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    if loan.return_date:
        messages.error(request, 'This book has already been returned.')
        return redirect('loan_list')

    # Transaction: atomically mark returned and increment copies
    with transaction.atomic():
        loan.return_date = date.today()
        loan.save()
        loan.book.total_copies += 1
        loan.book.save()

    messages.success(request, f'"{loan.book.title}" returned by {loan.member.name}.')
    return redirect('loan_list')


# ── Report ──

def loan_report(request):
    loans = Loan.objects.select_related('member', 'book').all().order_by('-checkout_date')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')

    if start_date:
        loans = loans.filter(due_date__gte=start_date)
    if end_date:
        loans = loans.filter(due_date__lte=end_date)
    if status == 'active':
        loans = loans.filter(return_date__isnull=True, due_date__gte=date.today())
    elif status == 'overdue':
        loans = loans.filter(return_date__isnull=True, due_date__lt=date.today())
    elif status == 'returned':
        loans = loans.filter(return_date__isnull=False)

    today = date.today()
    active_count = sum(1 for l in loans if not l.return_date and l.due_date >= today)
    overdue_count = sum(1 for l in loans if not l.return_date and l.due_date < today)
    returned_count = sum(1 for l in loans if l.return_date)

    return render(request, 'helloworld/loan_report.html', {
        'loans': loans,
        'total': loans.count(),
        'active_count': active_count,
        'overdue_count': overdue_count,
        'returned_count': returned_count,
        'start_date': start_date or '',
        'end_date': end_date or '',
        'status': status or '',
    })
