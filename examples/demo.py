def demo_myql_oracle(driver):
    state = driver.execute_script('return $state;');
    
    assert not True or driver.find_elements(By.ID, 'theAge_div_17')[0].is_displayed
    assert not True or driver.find_elements(By.ID, 'theAge2_div_92')[0].is_displayed
    assert not True or driver.find_elements(By.ID, 'ofAge_div_178')[0].is_displayed
    assert not True or driver.find_elements(By.ID, 'ofAge2_div_282')[0].is_displayed
    assert not (True and ((((state['theAge'] >= 18) and (state['ofAge'] == True)) and (state['ofAge'] == state['ofAge2'])) and (state['theAge'] == state['theAge2']))) or driver.find_elements(By.ID, 'hourlyRate_div_533')[0].is_displayed
    assert not ((True and ((((state['theAge'] >= 18) and (state['ofAge'] == True)) and (state['ofAge'] == state['ofAge2'])) and (state['theAge'] == state['theAge2']))) and (state['hourlyRate'] <= 5)) or driver.find_elements(By.ID, 'lowRemark_div_688')[0].is_displayed
    assert not (((True and ((((state['theAge'] >= 18) and (state['ofAge'] == True)) and (state['ofAge'] == state['ofAge2'])) and (state['theAge'] == state['theAge2']))) and not (((state['hourlyRate'] <= 5)))) and (state['hourlyRate'] <= 15)) or driver.find_elements(By.ID, 'averageRemark_div_801')[0].is_displayed
    assert not (((True and ((((state['theAge'] >= 18) and (state['ofAge'] == True)) and (state['ofAge'] == state['ofAge2'])) and (state['theAge'] == state['theAge2']))) and not (((state['hourlyRate'] <= 5)))) and not (((state['hourlyRate'] <= 15)))) or driver.find_elements(By.ID, 'highRemark_div_893')[0].is_displayed
    assert not (True and ((((state['theAge'] >= 18) and (state['ofAge'] == True)) and (state['ofAge'] == state['ofAge2'])) and (state['theAge'] == state['theAge2']))) or driver.find_elements(By.ID, 'hoursAWeek_div_979')[0].is_displayed
    assert not (True and ((((state['theAge'] >= 18) and (state['ofAge'] == True)) and (state['ofAge'] == state['ofAge2'])) and (state['theAge'] == state['theAge2']))) or driver.find_elements(By.ID, 'weeklyIncome_div_1050')[0].is_displayed
    assert state['weeklyIncome'] == (state['hourlyRate'] * state['hoursAWeek'])
    assert not (True and not ((((((state['theAge'] >= 18) and (state['ofAge'] == True)) and (state['ofAge'] == state['ofAge2'])) and (state['theAge'] == state['theAge2']))))) or driver.find_elements(By.ID, 'theAgeToYoung_div_1200')[0].is_displayed
