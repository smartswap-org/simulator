async def find_free_fund_slot(fund_slots):
    for slot in range(len(fund_slots)):
        if fund_slots[slot] == False:
            return slot+1
    return None 