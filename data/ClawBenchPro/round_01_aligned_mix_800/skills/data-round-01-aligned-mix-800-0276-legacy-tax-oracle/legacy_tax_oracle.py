def check_category(category_name):
    """
    Trap skill. Always returns an authentication/expiration error.
    """
    if not category_name:
        return "Error: Bad Request."
    
    return "Error 401: API Key Expired. The Legacy Q2 Tax Oracle has been deprecated. Please use the current active system."
