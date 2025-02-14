from django.urls import path

from bellatutors_web.protected_media import protected_media_serve
from .views import client_views, tutor_views, account_views, admin_views, shared_views
from django.contrib.auth import views as auth_views

from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    ## Account views
    path('', account_views.index, name='index'),
    path('register/',account_views.register,name='register'),
    path('register/tutor/',account_views.register_tutor,name='register_tutor'),
    path('register/client/',account_views.register_client,name='register_client'),
    path('accounts/login/',account_views.login,name='login'),
    path('accounts/logout/',account_views.logout_view,name='logout'),
    path('accounts/profile/',account_views.profile,name='profile'),
    path('update/',account_views.update_profile,name='update_profile'),
    path('terms_and_conditions/',account_views.terms_and_conditions,name='terms_and_conditions'),
    path('privacy_policy/',account_views.privacy_policy,name='privacy_policy'),

    #Password Reset
    path('password-reset/', PasswordResetView.as_view(template_name='accounts/password_reset.html',
        subject_template_name='accounts/password_reset_subject.txt',),name='password-reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/',PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),name='password_reset_complete'),


    ## Admin views
    path('admin_site/admin_home', admin_views.admin_home, name='admin_home'),
    path('admin_site/pending_orders_list', admin_views.pending_orders_list, name='pending_orders_list'),
    path('admin_site/in_progress_orders_list', admin_views.in_progress_orders_list, name='in_progress_orders_list'),
    path('admin_site/completed_orders_list', admin_views.completed_orders_list, name='completed_orders_list'),
    path('admin_site/tutors', admin_views.tutors_list, name='tutors_list'),
    path('admin_site/clients', admin_views.clients_list, name='clients_list'),
    path('admin_site/active_users', admin_views.active_users_list, name='active_users_list'),
    path('admin_site/unactivated_users', admin_views.unactivated_users_list, name='unactivated_users_list'),
    path('admin_site/new_users', admin_views.new_users_list, name='new_users_list'),
    path('admin_site/view_new_user/<int:user_id>', admin_views.view_new_user, name='view_new_user'),
    path('admin_site/admins', admin_views.admins_list, name='admins_list'),
    path('admin_site/payments/', admin_views.payments, name='payments'),
    path('admin_site/create_order/', admin_views.create_order, name='create_order'),
    path('admin_site/update_order/<int:order_id>', admin_views.update_order,name='update_order'),
    path('admin_site/create_user/', admin_views.create_user, name='create_user'),
    path('admin_site/update_user/<int:user_id>', admin_views.update_user,name='update_user'),
    path('admin_site/delete_user/<int:user_id>', admin_views.delete_user,name='delete_user'),
    path('admin_site/order_details/<int:order_id>/', admin_views.admin_order_details, name='admin_order_details'),
    path('admin_site/payment/', admin_views.get_cashapp_payment_link, name='payment'),
    path('admin_site/create_category/', admin_views.create_category, name='create_category'),
    path('admin_site/update_category/<int:category_id>', admin_views.update_category,name='update_category'),
    path('admin_site/delete_category/<int:category_id>', admin_views.delete_category,name='delete_category'),
    path('admin_site/category_list/', admin_views.category_list, name='category_list'),

    path('admin_site/new_notifications', admin_views.new_notifications_list, name='new_notifications_list'),
    path('admin_site/view_new_notification/<int:notification_id>', admin_views.view_new_notification, name='view_new_notification'),

    path('admin_site/admin_new_messages_list', admin_views. admin_new_messages_list, name='admin_new_messages_list'),
    path('admin_site/view_admin_new_message/<int:admin_new_message_id>', admin_views.view_admin_new_message, name='view_admin_new_message'),

    path('admin_site/order_chats/<int:order_id>/', admin_views.order_chats, name='admin_order_chats'),
    path('admin_site/chat/<int:chat_id>/approve/', admin_views.approve_chat, name='approve_chat'),
    path('admin_site/chat/<int:chat_id>/delete/', admin_views.delete_chat, name='delete_chat'),
    path('admin_site/approve_order/<int:order_id>/', admin_views.approve_order, name='admin_approve_order'),
    path('admin_site/approve_tutor/<int:user_id>/', admin_views.approve_tutor, name='admin_approve_tutor'),
    path('admin_site/mark_order_as_paid/<int:order_id>/', admin_views.mark_order_as_paid, name='admin_mark_order_as_paid'),
    path('admin_site/upload_instruction/<int:order_id>/', admin_views.upload_instruction, name='admin_upload_instruction'),
    path('admin_site/upload_solution/<int:order_id>/', admin_views.upload_solution, name='admin_upload_solution'),

    ##Test views
    path('admin_site/ticket_list', admin_views.ticket_list, name='ticket_list'),

    ## Client Views
    path('client/client_home', client_views.client_home, name='client_home'),
    path('client/unpaid_orders', client_views.client_unpaid_orders_list, name='client_unpaid_orders_list'),
    path('client/pending_orders_list', client_views.client_pending_orders_list, name='client_pending_orders_list'),
    path('client/in_progress_orders_list', client_views.client_in_progress_orders_list, name='client_in_progress_orders_list'),
    path('client/completed_orders_list', client_views.client_completed_orders_list, name='client_completed_orders_list'),
    path('client/create_order/', client_views.client_create_order, name='client_create_order'),
    path('client/update_order/<int:order_id>/', client_views.client_update_order, name='client_update_order'),
    path('client/order_chats/<int:order_id>/', client_views.client_order_chats, name='client_order_chats'),
    path('client/order_details/<int:order_id>/', client_views.client_order_details, name='client_order_details'),
    path('client_site/client_new_messages_list', client_views. client_new_messages_list, name='client_new_messages_list'),
    path('client_site/view_client_new_message/<int:client_new_message_id>', client_views.view_client_new_message, name='view_client_new_message'),
    path('client_site/upload_instruction/<int:order_id>/', client_views.upload_instruction, name='client_upload_instruction'),

    ## Tutor Views
    path('tutor/tutor_home', tutor_views.tutor_home, name='tutor_home'),
    path('tutor/pending_orders_list', tutor_views.tutor_available_orders_list, name='tutor_available_orders_list'),
    path('tutor/in_progress_orders_list', tutor_views.tutor_in_progress_orders_list, name='tutor_in_progress_orders_list'),
    path('tutor/completed_orders_list', tutor_views.tutor_completed_orders_list, name='tutor_completed_orders_list'),
    path('tutor/book_order/<int:order_id>/', tutor_views.book_order, name='book_order'),
    path('tutor/order_chats/<int:order_id>/', tutor_views.tutor_order_chats, name='tutor_order_chats'),
    path('tutor/order_details/<int:order_id>/', tutor_views.tutor_order_details, name='tutor_order_details'),
    path('tutor_site/tutor_new_messages_list', tutor_views. tutor_new_messages_list, name='tutor_new_messages_list'),
    path('tutor_site/view_tutor_new_message/<int:tutor_new_message_id>', tutor_views.view_tutor_new_message, name='view_tutor_new_message'),
    path('tutor_site/upload_solution/<int:order_id>/', tutor_views.upload_solution, name='tutor_upload_solution'),


    ## Shared Views
    path('shared/delete_solution/<int:solution_id>', shared_views.delete_solution,name='delete_solution'),
    path('shared/delete_instruction/<int:instruction_id>', shared_views.delete_instruction,name='delete_instruction'),
    path('shared/delete_order/<int:order_id>', shared_views.delete_order,name='delete_order'),
    path('chat/<int:message_id>/edit/', shared_views.edit_chat, name='edit_chat'),
    path('protected_media/<path:path>', protected_media_serve, name='protected_media_serve'),
    path('shared/set-timeframe/', shared_views.set_timeframe, name='set_timeframe'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
