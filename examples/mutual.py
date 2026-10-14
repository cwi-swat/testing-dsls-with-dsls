def ql_mutual_myql_oracle(page):
    state = page.evaluate('() => $state')
    
    assert not True or page.locator('#num_div_31').is_visible(), 'true evaluated to true, however num_div_31 was not displayed'
    assert not (True and (state['num'] >= 0)) or page.locator('#x_div_84').is_visible(), 'true && num >= 0 evaluated to true, however x_div_84 was not displayed'
    if page.locator('#x_div_84').is_visible():
        
        assert not page.locator('#x_div_134').is_visible(), ' x_div_134 was displayed at the same time as x_div_84'
        

    assert not (True and (state['num'] <= 0)) or page.locator('#x_div_134').is_visible(), 'true && num <= 0 evaluated to true, however x_div_134 was not displayed'
    assert state['x'] == True if (True and (state['num'] <= 0)) else True, ' x was expected to be true which equals ' + str(True) + ', but  x was  ' + str(state['x'])
    if page.locator('#x_div_134').is_visible():
        
        assert not page.locator('#x_div_84').is_visible(), ' x_div_84 was displayed at the same time as x_div_134'
        

