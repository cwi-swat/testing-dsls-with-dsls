from selenium.webdriver.common.by import By
def register_myql_oracle(driver):
    state = driver.execute_script('return $state;');
    
    assert not True or driver.find_elements(By.ID, 'days_div_26')[0].is_displayed(), 'true evaluated to true, however days_div_26 was not displayed'
    assert not True or driver.find_elements(By.ID, 'isAcm_div_61')[0].is_displayed(), 'true evaluated to true, however isAcm_div_61 was not displayed'
    assert not True or driver.find_elements(By.ID, 'isStudent_div_101')[0].is_displayed(), 'true evaluated to true, however isStudent_div_101 was not displayed'
    assert not True or driver.find_elements(By.ID, 'price_div_145')[0].is_displayed(), 'true evaluated to true, however price_div_145 was not displayed'
    assert state['price'] == 100, ' price was not the same as 100'
    assert not ((True and (state['isAcm'] or state['isStudent'])) and state['isAcm']) or driver.find_elements(By.ID, 'discount_div_243')[0].is_displayed(), 'true && isAcm || isStudent && isAcm evaluated to true, however discount_div_243 was not displayed'
    assert state['discount'] == 10, ' discount was not the same as 10'
    if driver.find_elements(By.ID, 'discount_div_243')[0].is_displayed():
        
        assert not driver.find_elements(By.ID, 'discount_div_328')[0].is_displayed(), ' discount_div_328 was displayed at the same time as discount_div_243'
        
        assert not driver.find_elements(By.ID, 'discount_div_396')[0].is_displayed(), ' discount_div_396 was displayed at the same time as discount_div_243'
        

    assert not ((True and (state['isAcm'] or state['isStudent'])) and state['isStudent']) or driver.find_elements(By.ID, 'discount_div_328')[0].is_displayed(), 'true && isAcm || isStudent && isStudent evaluated to true, however discount_div_328 was not displayed'
    assert state['discount'] == 20, ' discount was not the same as 20'
    if driver.find_elements(By.ID, 'discount_div_328')[0].is_displayed():
        
        assert not driver.find_elements(By.ID, 'discount_div_243')[0].is_displayed(), ' discount_div_243 was displayed at the same time as discount_div_328'
        
        assert not driver.find_elements(By.ID, 'discount_div_396')[0].is_displayed(), ' discount_div_396 was displayed at the same time as discount_div_328'
        

    assert not (True and not (((state['isAcm'] or state['isStudent'])))) or driver.find_elements(By.ID, 'discount_div_396')[0].is_displayed(), 'true && !(isAcm || isStudent) evaluated to true, however discount_div_396 was not displayed'
    assert state['discount'] == 0, ' discount was not the same as 0'
    if driver.find_elements(By.ID, 'discount_div_396')[0].is_displayed():
        
        assert not driver.find_elements(By.ID, 'discount_div_243')[0].is_displayed(), ' discount_div_243 was displayed at the same time as discount_div_396'
        
        assert not driver.find_elements(By.ID, 'discount_div_328')[0].is_displayed(), ' discount_div_328 was displayed at the same time as discount_div_396'
        

    assert not True or driver.find_elements(By.ID, 'total_div_434')[0].is_displayed(), 'true evaluated to true, however total_div_434 was not displayed'
    assert state['total'] == (state['days'] * ((state['price'] - state['discount']))), ' total was not the same as days * (price - discount)'
