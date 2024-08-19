var $state = {
  
  highRemark: "",
  
  theAge2: 0,
  
  hoursAWeek: 0,
  
  ofAge: false,
  
  theAge: 0,
  
  theAgeToYoung: false,
  
  hourlyRate: 0,
  
  lowRemark: "",
  
  averageRemark: "",
  
  ofAge2: false,
  
  weeklyIncome: 0,
  
}
function $update(name, value) {
   let change = false;
   let newVal = undefined;
   let div = undefined;
   if (name !== undefined) {
      $state[name] = value;
   }
   do {
     change = false;
     
     div = document.getElementById('theAge_div_15');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('theAge2_div_90');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('ofAge_div_176');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('ofAge2_div_280');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('hourlyRate_div_531');
     div.style.display = (true && (((($state.theAge >= 18) && ($state.ofAge === true)) && ($state.ofAge === $state.ofAge2)) && ($state.theAge === $state.theAge2))) ? 'block' : 'none'; 
     
     
     div = document.getElementById('lowRemark_div_686');
     div.style.display = ((true && (((($state.theAge >= 18) && ($state.ofAge === true)) && ($state.ofAge === $state.ofAge2)) && ($state.theAge === $state.theAge2))) && ($state.hourlyRate <= 5)) ? 'block' : 'none'; 
     
     
     div = document.getElementById('averageRemark_div_799');
     div.style.display = (((true && (((($state.theAge >= 18) && ($state.ofAge === true)) && ($state.ofAge === $state.ofAge2)) && ($state.theAge === $state.theAge2))) && !((($state.hourlyRate <= 5)))) && ($state.hourlyRate <= 15)) ? 'block' : 'none'; 
     
     
     div = document.getElementById('highRemark_div_891');
     div.style.display = (((true && (((($state.theAge >= 18) && ($state.ofAge === true)) && ($state.ofAge === $state.ofAge2)) && ($state.theAge === $state.theAge2))) && !((($state.hourlyRate <= 5)))) && !((($state.hourlyRate <= 15)))) ? 'block' : 'none'; 
     
     
     div = document.getElementById('hoursAWeek_div_977');
     div.style.display = (true && (((($state.theAge >= 18) && ($state.ofAge === true)) && ($state.ofAge === $state.ofAge2)) && ($state.theAge === $state.theAge2))) ? 'block' : 'none'; 
     
     
     div = document.getElementById('weeklyIncome_div_1048');
     div.style.display = (true && (((($state.theAge >= 18) && ($state.ofAge === true)) && ($state.ofAge === $state.ofAge2)) && ($state.theAge === $state.theAge2))) ? 'block' : 'none'; 
     
     newVal = ($state.hourlyRate * $state.hoursAWeek);
     if (newVal !== $state.weeklyIncome) {
       let elt = document.getElementById('weeklyIncome_widget_1048');
       $state.weeklyIncome = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('theAgeToYoung_div_1198');
     div.style.display = (true && !(((((($state.theAge >= 18) && ($state.ofAge === true)) && ($state.ofAge === $state.ofAge2)) && ($state.theAge === $state.theAge2))))) ? 'block' : 'none'; 
     
     
   } while (change);
}
