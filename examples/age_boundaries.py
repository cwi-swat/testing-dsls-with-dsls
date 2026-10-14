def ql_age_boundaries_myql_oracle(page):
    state = page.evaluate('() => $state')
    
    assert not True or page.locator('#personName_div_26').is_visible(), 'true evaluated to true, however personName_div_26 was not displayed'
    assert not True or page.locator('#age_div_54').is_visible(), 'true evaluated to true, however age_div_54 was not displayed'
    assert not True or page.locator('#invalidAge_div_75').is_visible(), 'true evaluated to true, however invalidAge_div_75 was not displayed'
    assert state['invalidAge'] == (state['age'] < 0) if True else True, ' invalidAge was expected to be age < 0 which equals ' + str((state['age'] < 0)) + ', but  invalidAge was  ' + str(state['invalidAge'])
    assert not (True and (state['age'] < 0)) or page.locator('#ageWarning_div_150').is_visible(), 'true && age < 0 evaluated to true, however ageWarning_div_150 was not displayed'
    assert state['ageWarning'] == 'Age cannot be negative' if (True and (state['age'] < 0)) else True, ' ageWarning was expected to be "Age cannot be negative" which equals ' + str('Age cannot be negative') + ', but  ageWarning was  ' + str(state['ageWarning'])
    assert not ((True and (not (((state['age'] < 0))))) and (state['age'] < 18)) or page.locator('#ageGroup_div_239').is_visible(), 'true && !(age < 0) && age < 18 evaluated to true, however ageGroup_div_239 was not displayed'
    assert state['ageGroup'] == 'Under 18' if ((True and (not (((state['age'] < 0))))) and (state['age'] < 18)) else True, ' ageGroup was expected to be "Under 18" which equals ' + str('Under 18') + ', but  ageGroup was  ' + str(state['ageGroup'])
    if page.locator('#ageGroup_div_239').is_visible():
        
        assert not page.locator('#ageGroup_div_351').is_visible(), ' ageGroup_div_351 was displayed at the same time as ageGroup_div_239'
        
        assert not page.locator('#ageGroup_div_439').is_visible(), ' ageGroup_div_439 was displayed at the same time as ageGroup_div_239'
        

    assert not ((True and (not (((state['age'] < 0))))) and (state['age'] < 18)) or page.locator('#guardianName_div_285').is_visible(), 'true && !(age < 0) && age < 18 evaluated to true, however guardianName_div_285 was not displayed'
    assert not (((True and (not (((state['age'] < 0))))) and (not (((state['age'] < 18))))) and (state['age'] < 65)) or page.locator('#ageGroup_div_351').is_visible(), 'true && !(age < 0) && !(age < 18) && age < 65 evaluated to true, however ageGroup_div_351 was not displayed'
    assert state['ageGroup'] == 'Adult' if (((True and (not (((state['age'] < 0))))) and (not (((state['age'] < 18))))) and (state['age'] < 65)) else True, ' ageGroup was expected to be "Adult" which equals ' + str('Adult') + ', but  ageGroup was  ' + str(state['ageGroup'])
    if page.locator('#ageGroup_div_351').is_visible():
        
        assert not page.locator('#ageGroup_div_239').is_visible(), ' ageGroup_div_239 was displayed at the same time as ageGroup_div_351'
        
        assert not page.locator('#ageGroup_div_439').is_visible(), ' ageGroup_div_439 was displayed at the same time as ageGroup_div_351'
        

    assert not (((True and (not (((state['age'] < 0))))) and (not (((state['age'] < 18))))) and (state['age'] < 65)) or page.locator('#employed_div_394').is_visible(), 'true && !(age < 0) && !(age < 18) && age < 65 evaluated to true, however employed_div_394 was not displayed'
    assert not (((True and (not (((state['age'] < 0))))) and (not (((state['age'] < 18))))) and (not (((state['age'] < 65))))) or page.locator('#ageGroup_div_439').is_visible(), 'true && !(age < 0) && !(age < 18) && !(age < 65) evaluated to true, however ageGroup_div_439 was not displayed'
    assert state['ageGroup'] == 'Senior' if (((True and (not (((state['age'] < 0))))) and (not (((state['age'] < 18))))) and (not (((state['age'] < 65))))) else True, ' ageGroup was expected to be "Senior" which equals ' + str('Senior') + ', but  ageGroup was  ' + str(state['ageGroup'])
    if page.locator('#ageGroup_div_439').is_visible():
        
        assert not page.locator('#ageGroup_div_239').is_visible(), ' ageGroup_div_239 was displayed at the same time as ageGroup_div_439'
        
        assert not page.locator('#ageGroup_div_351').is_visible(), ' ageGroup_div_351 was displayed at the same time as ageGroup_div_439'
        

    assert not (((True and (not (((state['age'] < 0))))) and (not (((state['age'] < 18))))) and (not (((state['age'] < 65))))) or page.locator('#retired_div_483').is_visible(), 'true && !(age < 0) && !(age < 18) && !(age < 65) evaluated to true, however retired_div_483 was not displayed'
    assert not True or page.locator('#exactlyEighteen_div_518').is_visible(), 'true evaluated to true, however exactlyEighteen_div_518 was not displayed'
    assert state['exactlyEighteen'] == (state['age'] == 18) if True else True, ' exactlyEighteen was expected to be age == 18 which equals ' + str((state['age'] == 18)) + ', but  exactlyEighteen was  ' + str(state['exactlyEighteen'])
    assert not True or page.locator('#exactlySixtyFive_div_570').is_visible(), 'true evaluated to true, however exactlySixtyFive_div_570 was not displayed'
    assert state['exactlySixtyFive'] == (state['age'] == 65) if True else True, ' exactlySixtyFive was expected to be age == 65 which equals ' + str((state['age'] == 65)) + ', but  exactlySixtyFive was  ' + str(state['exactlySixtyFive'])
    assert not True or page.locator('#adultAge_div_623').is_visible(), 'true evaluated to true, however adultAge_div_623 was not displayed'
    assert state['adultAge'] == (state['age'] >= 18) if True else True, ' adultAge was expected to be age >= 18 which equals ' + str((state['age'] >= 18)) + ', but  adultAge was  ' + str(state['adultAge'])
