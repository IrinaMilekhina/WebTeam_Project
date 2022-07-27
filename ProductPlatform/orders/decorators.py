def order_board_check(user):
    return user.role == 'Supplier' or user.is_superuser or user.is_staff
