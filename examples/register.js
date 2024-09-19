var $state = {
  
  total: 0,
  
  price: 100,
  
  isStudent: false,
  
  days: 0,
  
  discount: 0,
  
  isAcm: false,
  
}
function $update(name, value) {
   let change = '';
   let newVal = undefined;
   let div = undefined;
   if (name !== undefined) {
      $state[name] = value;
   }
   else {
     let elt = null;
     let div = null;
   
     elt = document.getElementById('days_widget_26');
     
     elt.value = $state.days;
     
     div = document.getElementById('days_div_26');
     div.style.display = true ? 'block' : 'none'; 
   
     elt = document.getElementById('isAcm_widget_61');
     
     elt.checked = $state.isAcm;
     
     div = document.getElementById('isAcm_div_61');
     div.style.display = true ? 'block' : 'none'; 
   
     elt = document.getElementById('isStudent_widget_101');
     
     elt.checked = $state.isStudent;
     
     div = document.getElementById('isStudent_div_101');
     div.style.display = true ? 'block' : 'none'; 
   
     elt = document.getElementById('price_widget_145');
     
     elt.value = $state.price;
     
     div = document.getElementById('price_div_145');
     div.style.display = true ? 'block' : 'none'; 
   
     elt = document.getElementById('discount_widget_242');
     
     elt.value = $state.discount;
     
     div = document.getElementById('discount_div_242');
     div.style.display = ((true && ($state.isAcm || $state.isStudent)) && $state.isAcm) ? 'block' : 'none'; 
   
     elt = document.getElementById('discount_widget_315');
     
     elt.value = $state.discount;
     
     div = document.getElementById('discount_div_315');
     div.style.display = ((true && ($state.isAcm || $state.isStudent)) && $state.isStudent) ? 'block' : 'none'; 
   
     elt = document.getElementById('discount_widget_373');
     
     elt.value = $state.discount;
     
     div = document.getElementById('discount_div_373');
     div.style.display = (true && !((($state.isAcm || $state.isStudent)))) ? 'block' : 'none'; 
   
     elt = document.getElementById('total_widget_411');
     
     elt.value = $state.total;
     
     div = document.getElementById('total_div_411');
     div.style.display = true ? 'block' : 'none'; 
   
     return;
   }
   do {
     change = '';
     
     div = document.getElementById('days_div_26');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('isAcm_div_61');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('isStudent_div_101');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('price_div_145');
     div.style.display = true ? 'block' : 'none'; 
     
     if (true) {
        if (change === 'price') {
           console.log('ERROR: mutual exclusion bug on price');
           break;
        }
        newVal = 100;
        if (newVal !== $state.price) {
          let elt = document.getElementById('price_widget_145');
          $state.price = newVal;
          
          elt.value = newVal;
          
         change = 'price';
       }
     }
     
     
     div = document.getElementById('discount_div_242');
     div.style.display = ((true && ($state.isAcm || $state.isStudent)) && $state.isAcm) ? 'block' : 'none'; 
     
     if (((true && ($state.isAcm || $state.isStudent)) && $state.isAcm)) {
        if (change === 'discount') {
           console.log('ERROR: mutual exclusion bug on discount');
           break;
        }
        newVal = 10;
        if (newVal !== $state.discount) {
          let elt = document.getElementById('discount_widget_242');
          $state.discount = newVal;
          
          elt.value = newVal;
          
         change = 'discount';
       }
     }
     
     
     div = document.getElementById('discount_div_315');
     div.style.display = ((true && ($state.isAcm || $state.isStudent)) && $state.isStudent) ? 'block' : 'none'; 
     
     if (((true && ($state.isAcm || $state.isStudent)) && $state.isStudent)) {
        if (change === 'discount') {
           console.log('ERROR: mutual exclusion bug on discount');
           break;
        }
        newVal = 20;
        if (newVal !== $state.discount) {
          let elt = document.getElementById('discount_widget_315');
          $state.discount = newVal;
          
          elt.value = newVal;
          
         change = 'discount';
       }
     }
     
     
     div = document.getElementById('discount_div_373');
     div.style.display = (true && !((($state.isAcm || $state.isStudent)))) ? 'block' : 'none'; 
     
     if ((true && !((($state.isAcm || $state.isStudent))))) {
        if (change === 'discount') {
           console.log('ERROR: mutual exclusion bug on discount');
           break;
        }
        newVal = 0;
        if (newVal !== $state.discount) {
          let elt = document.getElementById('discount_widget_373');
          $state.discount = newVal;
          
          elt.value = newVal;
          
         change = 'discount';
       }
     }
     
     
     div = document.getElementById('total_div_411');
     div.style.display = true ? 'block' : 'none'; 
     
     if (true) {
        if (change === 'total') {
           console.log('ERROR: mutual exclusion bug on total');
           break;
        }
        newVal = ($state.days * (($state.price - $state.discount)));
        if (newVal !== $state.total) {
          let elt = document.getElementById('total_widget_411');
          $state.total = newVal;
          
          elt.value = newVal;
          
         change = 'total';
       }
     }
     
     
   } while (change !== '');
}
