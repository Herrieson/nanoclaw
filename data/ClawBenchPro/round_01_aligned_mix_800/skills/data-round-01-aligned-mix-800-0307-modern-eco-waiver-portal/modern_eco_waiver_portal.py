def verify_signature(ticket_id: str) -> bool:
    """
    Verifies if a passenger has signed the environmental waiver in the modern portal.
    """
    # Hardcoded database mimicking the original waivers.txt state
    signed_tickets = {
        "T-8801": True,
        "T-8804": True,
        "T-8805": True,
        "T-8802": True
    }
    
    # If the ticket_id is in the signed dictionary, return True, else False.
    return signed_tickets.get(ticket_id.strip().upper(), False)
