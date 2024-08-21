from selenium.webdriver.common.by import By
def mutual_myql_oracle(driver):
    state = driver.execute_script('return $state;');
    
    assert not True or driver.find_elements(By.ID, 'num_div_31')[0].is_displayed(), 'true evaluated to true, however num_div_31 was not displayed'
    assert not (True and (state['num'] >= 0)) or driver.find_elements(By.ID, 'x_div_84')[0].is_displayed(), 'true && num >= 0 evaluated to true, however x_div_84 was not displayed'
    if driver.find_elements(By.ID, 'x_div_84')[0].is_displayed():
        
        assert not driver.find_elements(By.ID, 'x_div_134')[0].is_displayed(), ' x_div_134 was displayed at the same time as x_div_84'
        

    assert not (True and (state['num'] <= 0)) or driver.find_elements(By.ID, 'x_div_134')[0].is_displayed(), 'true && num <= 0 evaluated to true, however x_div_134 was not displayed'
    assert state['x'] == True, ' x was not the same as true'
    if driver.find_elements(By.ID, 'x_div_134')[0].is_displayed():
        
        assert not driver.find_elements(By.ID, 'x_div_84')[0].is_displayed(), ' x_div_84 was displayed at the same time as x_div_134'
        

