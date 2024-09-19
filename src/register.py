from selenium.webdriver.common.by import By
def register_myql_oracle(driver):
    state = driver.execute_script('return $state;');
    
    assert not True or driver.find_elements(By.ID, 'days_div_26')[0].is_displayed(), 'true evaluated to true, however days_div_26 was not displayed'
    assert not True or driver.find_elements(By.ID, 'acm_div_76')[0].is_displayed(), 'true evaluated to true, however acm_div_76 was not displayed'
    assert not True or driver.find_elements(By.ID, 'student_div_118')[0].is_displayed(), 'true evaluated to true, however student_div_118 was not displayed'
    assert not True or driver.find_elements(By.ID, 'price_div_160')[0].is_displayed(), 'true evaluated to true, however price_div_160 was not displayed'
    assert state['price'] == 100, ' price was not the same as 100, expected ' + 100 + ', got ' + state['price']
    assert not (True and (state['acm'] and state['student'])) or driver.find_elements(By.ID, 'discount_div_227')[0].is_displayed(), 'true && acm && student evaluated to true, however discount_div_227 was not displayed'
    assert state['discount'] == 5, ' discount was not the same as 5, expected ' + 5 + ', got ' + state['discount']
    if driver.find_elements(By.ID, 'discount_div_227')[0].is_displayed():
        
        assert not driver.find_elements(By.ID, 'discount_div_287')[0].is_displayed(), ' discount_div_287 was displayed at the same time as discount_div_227'
        
        assert not driver.find_elements(By.ID, 'discount_div_353')[0].is_displayed(), ' discount_div_353 was displayed at the same time as discount_div_227'
        
        assert not driver.find_elements(By.ID, 'discount_div_405')[0].is_displayed(), ' discount_div_405 was displayed at the same time as discount_div_227'
        

    assert not ((True and not (((state['acm'] and state['student'])))) and state['acm']) or driver.find_elements(By.ID, 'discount_div_287')[0].is_displayed(), 'true && !(acm && student) && acm evaluated to true, however discount_div_287 was not displayed'
    assert state['discount'] == 10, ' discount was not the same as 10, expected ' + 10 + ', got ' + state['discount']
    if driver.find_elements(By.ID, 'discount_div_287')[0].is_displayed():
        
        assert not driver.find_elements(By.ID, 'discount_div_227')[0].is_displayed(), ' discount_div_227 was displayed at the same time as discount_div_287'
        
        assert not driver.find_elements(By.ID, 'discount_div_353')[0].is_displayed(), ' discount_div_353 was displayed at the same time as discount_div_287'
        
        assert not driver.find_elements(By.ID, 'discount_div_405')[0].is_displayed(), ' discount_div_405 was displayed at the same time as discount_div_287'
        

    assert not (((True and not (((state['acm'] and state['student'])))) and not ((state['acm']))) and state['student']) or driver.find_elements(By.ID, 'discount_div_353')[0].is_displayed(), 'true && !(acm && student) && !(acm) && student evaluated to true, however discount_div_353 was not displayed'
    assert state['discount'] == 20, ' discount was not the same as 20, expected ' + 20 + ', got ' + state['discount']
    if driver.find_elements(By.ID, 'discount_div_353')[0].is_displayed():
        
        assert not driver.find_elements(By.ID, 'discount_div_227')[0].is_displayed(), ' discount_div_227 was displayed at the same time as discount_div_353'
        
        assert not driver.find_elements(By.ID, 'discount_div_287')[0].is_displayed(), ' discount_div_287 was displayed at the same time as discount_div_353'
        
        assert not driver.find_elements(By.ID, 'discount_div_405')[0].is_displayed(), ' discount_div_405 was displayed at the same time as discount_div_353'
        

    assert not (((True and not (((state['acm'] and state['student'])))) and not ((state['acm']))) and not ((state['student']))) or driver.find_elements(By.ID, 'discount_div_405')[0].is_displayed(), 'true && !(acm && student) && !(acm) && !(student) evaluated to true, however discount_div_405 was not displayed'
    assert state['discount'] == 0, ' discount was not the same as 0, expected ' + 0 + ', got ' + state['discount']
    if driver.find_elements(By.ID, 'discount_div_405')[0].is_displayed():
        
        assert not driver.find_elements(By.ID, 'discount_div_227')[0].is_displayed(), ' discount_div_227 was displayed at the same time as discount_div_405'
        
        assert not driver.find_elements(By.ID, 'discount_div_287')[0].is_displayed(), ' discount_div_287 was displayed at the same time as discount_div_405'
        
        assert not driver.find_elements(By.ID, 'discount_div_353')[0].is_displayed(), ' discount_div_353 was displayed at the same time as discount_div_405'
        

    assert not True or driver.find_elements(By.ID, 'pay_div_444')[0].is_displayed(), 'true evaluated to true, however pay_div_444 was not displayed'
    assert state['pay'] == (state['days'] * ((state['price'] - state['discount']))), ' pay was not the same as days * (price - discount), expected ' + (state['days'] * ((state['price'] - state['discount']))) + ', got ' + state['pay']
