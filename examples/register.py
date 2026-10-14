def ql_register_myql_oracle(page):
    state = page.evaluate('() => $state')
    
    assert not True or page.locator('#days_div_26').is_visible(), 'true evaluated to true, however days_div_26 was not displayed'
    assert not True or page.locator('#acm_div_76').is_visible(), 'true evaluated to true, however acm_div_76 was not displayed'
    assert not True or page.locator('#student_div_118').is_visible(), 'true evaluated to true, however student_div_118 was not displayed'
    assert not True or page.locator('#price_div_160').is_visible(), 'true evaluated to true, however price_div_160 was not displayed'
    assert state['price'] == 100 if True else True, ' price was expected to be 100 which equals ' + str(100) + ', but  price was  ' + str(state['price'])
    assert not (True and (state['acm'] and state['student'])) or page.locator('#discount_div_227').is_visible(), 'true && acm && student evaluated to true, however discount_div_227 was not displayed'
    assert state['discount'] == 5 if (True and (state['acm'] and state['student'])) else True, ' discount was expected to be 5 which equals ' + str(5) + ', but  discount was  ' + str(state['discount'])
    if page.locator('#discount_div_227').is_visible():
        
        assert not page.locator('#discount_div_287').is_visible(), ' discount_div_287 was displayed at the same time as discount_div_227'
        
        assert not page.locator('#discount_div_353').is_visible(), ' discount_div_353 was displayed at the same time as discount_div_227'
        
        assert not page.locator('#discount_div_405').is_visible(), ' discount_div_405 was displayed at the same time as discount_div_227'
        

    assert not ((True and (not (((state['acm'] and state['student']))))) and state['acm']) or page.locator('#discount_div_287').is_visible(), 'true && !(acm && student) && acm evaluated to true, however discount_div_287 was not displayed'
    assert state['discount'] == 10 if ((True and (not (((state['acm'] and state['student']))))) and state['acm']) else True, ' discount was expected to be 10 which equals ' + str(10) + ', but  discount was  ' + str(state['discount'])
    if page.locator('#discount_div_287').is_visible():
        
        assert not page.locator('#discount_div_227').is_visible(), ' discount_div_227 was displayed at the same time as discount_div_287'
        
        assert not page.locator('#discount_div_353').is_visible(), ' discount_div_353 was displayed at the same time as discount_div_287'
        
        assert not page.locator('#discount_div_405').is_visible(), ' discount_div_405 was displayed at the same time as discount_div_287'
        

    assert not (((True and (not (((state['acm'] and state['student']))))) and (not ((state['acm'])))) and state['student']) or page.locator('#discount_div_353').is_visible(), 'true && !(acm && student) && !(acm) && student evaluated to true, however discount_div_353 was not displayed'
    assert state['discount'] == 20 if (((True and (not (((state['acm'] and state['student']))))) and (not ((state['acm'])))) and state['student']) else True, ' discount was expected to be 20 which equals ' + str(20) + ', but  discount was  ' + str(state['discount'])
    if page.locator('#discount_div_353').is_visible():
        
        assert not page.locator('#discount_div_227').is_visible(), ' discount_div_227 was displayed at the same time as discount_div_353'
        
        assert not page.locator('#discount_div_287').is_visible(), ' discount_div_287 was displayed at the same time as discount_div_353'
        
        assert not page.locator('#discount_div_405').is_visible(), ' discount_div_405 was displayed at the same time as discount_div_353'
        

    assert not (((True and (not (((state['acm'] and state['student']))))) and (not ((state['acm'])))) and (not ((state['student'])))) or page.locator('#discount_div_405').is_visible(), 'true && !(acm && student) && !(acm) && !(student) evaluated to true, however discount_div_405 was not displayed'
    assert state['discount'] == 0 if (((True and (not (((state['acm'] and state['student']))))) and (not ((state['acm'])))) and (not ((state['student'])))) else True, ' discount was expected to be 0 which equals ' + str(0) + ', but  discount was  ' + str(state['discount'])
    if page.locator('#discount_div_405').is_visible():
        
        assert not page.locator('#discount_div_227').is_visible(), ' discount_div_227 was displayed at the same time as discount_div_405'
        
        assert not page.locator('#discount_div_287').is_visible(), ' discount_div_287 was displayed at the same time as discount_div_405'
        
        assert not page.locator('#discount_div_353').is_visible(), ' discount_div_353 was displayed at the same time as discount_div_405'
        

    assert not True or page.locator('#pay_div_443').is_visible(), 'true evaluated to true, however pay_div_443 was not displayed'
    assert state['pay'] == (state['days'] * ((state['price'] - state['discount']))) if True else True, ' pay was expected to be days * (price - discount) which equals ' + str((state['days'] * ((state['price'] - state['discount'])))) + ', but  pay was  ' + str(state['pay'])
