from selenium.webdriver.common.by import By
def tax_myql_oracle(driver):
    state = driver.execute_script('return $state;');
    
    assert not True or driver.find_elements(By.ID, 'hasBoughtHouse_div_31')[0].is_displayed
    assert not True or driver.find_elements(By.ID, 'hasMaintLoan_div_97')[0].is_displayed
    assert not True or driver.find_elements(By.ID, 'hasSoldHouse_div_154')[0].is_displayed
    assert not (True and state['hasSoldHouse']) or driver.find_elements(By.ID, 'sellingPrice_div_246')[0].is_displayed
    assert not (True and state['hasSoldHouse']) or driver.find_elements(By.ID, 'privateDebt_div_308')[0].is_displayed
    assert not (True and state['hasSoldHouse']) or driver.find_elements(By.ID, 'valueResidue_div_375')[0].is_displayed
    assert state['valueResidue'] == (state['sellingPrice'] - state['privateDebt'])
