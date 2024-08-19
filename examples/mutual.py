from selenium.webdriver.common.by import By
def mutual_myql_oracle(driver):
    state = driver.execute_script('return $state;');
    
    assert not True or driver.find_elements(By.ID, 'num_div_31')[0].is_displayed
    assert not (True and (state['num'] >= 0)) or driver.find_elements(By.ID, 'x_div_84')[0].is_displayed
    if driver.find_elements(By.ID, 'x_div_84')[0].is_displayed:
        
        assert not driver.find_elements(By.ID, 'x_div_134')[0].is_displayed
        

    assert not (True and (state['num'] <= 0)) or driver.find_elements(By.ID, 'x_div_134')[0].is_displayed
    assert state['x'] == True
    if driver.find_elements(By.ID, 'x_div_134')[0].is_displayed:
        
        assert not driver.find_elements(By.ID, 'x_div_84')[0].is_displayed
        

