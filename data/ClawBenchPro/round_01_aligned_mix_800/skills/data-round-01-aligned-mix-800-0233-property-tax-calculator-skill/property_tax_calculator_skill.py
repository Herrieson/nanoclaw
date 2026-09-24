def service(unit_id):
    # Dynamic tax logic: 5% of a base value or fixed fee
    taxes = {
        "101": 55.0, "102": 60.0, "103": 45.0,
        "201": 80.0, "202": 65.0, "203": 70.0
    }
    return taxes.get(str(unit_id), 50.0) # Default tax for unregistered units
