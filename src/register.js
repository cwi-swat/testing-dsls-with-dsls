var $state = {
  
  discount: 0,
  
  pay: 0,
  
  price: 100,
  
  acm: false,
  
  days: 0,
  
  student: false,
  
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
   
     elt = document.getElementById('acm_widget_76');
     
     elt.checked = $state.acm;
     
     div = document.getElementById('acm_div_76');
     div.style.display = true ? 'block' : 'none'; 
   
     elt = document.getElementById('student_widget_118');
     
     elt.checked = $state.student;
     
     div = document.getElementById('student_div_118');
     div.style.display = true ? 'block' : 'none'; 
   
     elt = document.getElementById('price_widget_160');
     
     elt.value = $state.price;
     
     div = document.getElementById('price_div_160');
     div.style.display = true ? 'block' : 'none'; 
   
     elt = document.getElementById('discount_widget_227');
     
     elt.value = $state.discount;
     
     div = document.getElementById('discount_div_227');
     div.style.display = (true && ($state.acm && $state.student)) ? 'block' : 'none'; 
   
     elt = document.getElementById('discount_widget_287');
     
     elt.value = $state.discount;
     
     div = document.getElementById('discount_div_287');
     div.style.display = ((true && !((($state.acm && $state.student)))) && $state.acm) ? 'block' : 'none'; 
   
     elt = document.getElementById('discount_widget_353');
     
     elt.value = $state.discount;
     
     div = document.getElementById('discount_div_353');
     div.style.display = (((true && !((($state.acm && $state.student)))) && !(($state.acm))) && $state.student) ? 'block' : 'none'; 
   
     elt = document.getElementById('discount_widget_405');
     
     elt.value = $state.discount;
     
     div = document.getElementById('discount_div_405');
     div.style.display = (((true && !((($state.acm && $state.student)))) && !(($state.acm))) && !(($state.student))) ? 'block' : 'none'; 
   
     elt = document.getElementById('pay_widget_444');
     
     elt.value = $state.pay;
     
     div = document.getElementById('pay_div_444');
     div.style.display = true ? 'block' : 'none'; 
   
     return;
   }
   do {
     change = '';
     
     div = document.getElementById('days_div_26');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('acm_div_76');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('student_div_118');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('price_div_160');
     div.style.display = true ? 'block' : 'none'; 
     
     if (true) {
        if (change === 'price') {
           console.log('ERROR: mutual exclusion bug on price');
           break;
        }
        newVal = 100;
        if (newVal !== $state.price) {
          let elt = document.getElementById('price_widget_160');
          $state.price = newVal;
          
          elt.value = newVal;
          
         change = 'price';
       }
     }
     
     
     div = document.getElementById('discount_div_227');
     div.style.display = (true && ($state.acm && $state.student)) ? 'block' : 'none'; 
     
     if ((true && ($state.acm && $state.student))) {
        if (change === 'discount') {
           console.log('ERROR: mutual exclusion bug on discount');
           break;
        }
        newVal = 5;
        if (newVal !== $state.discount) {
          let elt = document.getElementById('discount_widget_227');
          $state.discount = newVal;
          
          elt.value = newVal;
          
         change = 'discount';
       }
     }
     
     
     div = document.getElementById('discount_div_287');
     div.style.display = ((true && !((($state.acm && $state.student)))) && $state.acm) ? 'block' : 'none'; 
     
     if (((true && !((($state.acm && $state.student)))) && $state.acm)) {
        if (change === 'discount') {
           console.log('ERROR: mutual exclusion bug on discount');
           break;
        }
        newVal = 10;
        if (newVal !== $state.discount) {
          let elt = document.getElementById('discount_widget_287');
          $state.discount = newVal;
          
          elt.value = newVal;
          
         change = 'discount';
       }
     }
     
     
     div = document.getElementById('discount_div_353');
     div.style.display = (((true && !((($state.acm && $state.student)))) && !(($state.acm))) && $state.student) ? 'block' : 'none'; 
     
     if ((((true && !((($state.acm && $state.student)))) && !(($state.acm))) && $state.student)) {
        if (change === 'discount') {
           console.log('ERROR: mutual exclusion bug on discount');
           break;
        }
        newVal = 20;
        if (newVal !== $state.discount) {
          let elt = document.getElementById('discount_widget_353');
          $state.discount = newVal;
          
          elt.value = newVal;
          
         change = 'discount';
       }
     }
     
     
     div = document.getElementById('discount_div_405');
     div.style.display = (((true && !((($state.acm && $state.student)))) && !(($state.acm))) && !(($state.student))) ? 'block' : 'none'; 
     
     if ((((true && !((($state.acm && $state.student)))) && !(($state.acm))) && !(($state.student)))) {
        if (change === 'discount') {
           console.log('ERROR: mutual exclusion bug on discount');
           break;
        }
        newVal = 0;
        if (newVal !== $state.discount) {
          let elt = document.getElementById('discount_widget_405');
          $state.discount = newVal;
          
          elt.value = newVal;
          
         change = 'discount';
       }
     }
     
     
     div = document.getElementById('pay_div_444');
     div.style.display = true ? 'block' : 'none'; 
     
     if (true) {
        if (change === 'pay') {
           console.log('ERROR: mutual exclusion bug on pay');
           break;
        }
        newVal = ($state.days * (($state.price - $state.discount)));
        if (newVal !== $state.pay) {
          let elt = document.getElementById('pay_widget_444');
          $state.pay = newVal;
          
          elt.value = newVal;
          
         change = 'pay';
       }
     }
     
     
   } while (change !== '');
}
