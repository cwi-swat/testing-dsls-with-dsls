def ql_tax_myql_oracle(page):
    state = page.evaluate('() => $state')
    
    assert not True or page.locator('#hasBoughtHouse_div_31').is_visible(), 'true evaluated to true, however hasBoughtHouse_div_31 was not displayed'
    assert not True or page.locator('#hasMaintLoan_div_95').is_visible(), 'true evaluated to true, however hasMaintLoan_div_95 was not displayed'
    assert not True or page.locator('#hasSoldHouse_div_152').is_visible(), 'true evaluated to true, however hasSoldHouse_div_152 was not displayed'
    assert not (True and state['hasSoldHouse']) or page.locator('#sellingPrice_div_244').is_visible(), 'true && hasSoldHouse evaluated to true, however sellingPrice_div_244 was not displayed'
    assert not (True and state['hasSoldHouse']) or page.locator('#privateDebt_div_306').is_visible(), 'true && hasSoldHouse evaluated to true, however privateDebt_div_306 was not displayed'
    assert not (True and state['hasSoldHouse']) or page.locator('#valueResidue_div_373').is_visible(), 'true && hasSoldHouse evaluated to true, however valueResidue_div_373 was not displayed'
    assert state['valueResidue'] == (state['sellingPrice'] - state['privateDebt']) if (True and state['hasSoldHouse']) else True, ' valueResidue was expected to be sellingPrice - privateDebt which equals ' + str((state['sellingPrice'] - state['privateDebt'])) + ', but  valueResidue was  ' + str(state['valueResidue'])
