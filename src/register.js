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
   
     elt = document.getElementById('days_widget_27');
     
     elt.value = $state.days;
     
     div = document.getElementById('days_div_27');
     div.style.display = true ? 'block' : 'none'; 
   
     elt = document.getElementById('acm_widget_77');
     
     elt.checked = $state.acm;
     
     div = document.getElementById('acm_div_77');
     div.style.display = true ? 'block' : 'none'; 
   
     elt = document.getElementById('student_widget_119');
     
     elt.checked = $state.student;
     
     div = document.getElementById('student_div_119');
     div.style.display = true ? 'block' : 'none'; 
   
     elt = document.getElementById('price_widget_162');
     
     elt.value = $state.price;
     
     div = document.getElementById('price_div_162');
     div.style.display = true ? 'block' : 'none'; 
   
     elt = document.getElementById('discount_widget_252');
     
     elt.value = $state.discount;
     
     div = document.getElementById('discount_div_252');
     div.style.display = ((true && ($state.acm || $state.student)) && $state.acm) ? 'block' : 'none'; 
   
     elt = document.getElementById('discount_widget_319');
     
     elt.value = $state.discount;
     
     div = document.getElementById('discount_div_319');
     div.style.display = ((true && ($state.acm || $state.student)) && $state.student) ? 'block' : 'none'; 
   
     elt = document.getElementById('discount_widget_376');
     
     elt.value = $state.discount;
     
     div = document.getElementById('discount_div_376');
     div.style.display = (true && !((($state.acm || $state.student)))) ? 'block' : 'none'; 
   
     elt = document.getElementById('pay_widget_414');
     
     elt.value = $state.pay;
     
     div = document.getElementById('pay_div_414');
     div.style.display = true ? 'block' : 'none'; 
   
     return;
   }
   do {
     change = '';
     
     div = document.getElementById('days_div_27');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('acm_div_77');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('student_div_119');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('price_div_162');
     div.style.display = true ? 'block' : 'none'; 
     
     if (true) {
        if (change === 'price') {
           console.log('ERROR: mutual exclusion bug on price');
           break;
        }
        newVal = 100;
        if (newVal !== $state.price) {
          let elt = document.getElementById('price_widget_162');
          $state.price = newVal;
          
          elt.value = newVal;
          
         change = 'price';
       }
     }
     
     
     div = document.getElementById('discount_div_252');
     div.style.display = ((true && ($state.acm || $state.student)) && $state.acm) ? 'block' : 'none'; 
     
     if (((true && ($state.acm || $state.student)) && $state.acm)) {
        if (change === 'discount') {
           console.log('ERROR: mutual exclusion bug on discount');
           break;
        }
        newVal = 10;
        if (newVal !== $state.discount) {
          let elt = document.getElementById('discount_widget_252');
          $state.discount = newVal;
          
          elt.value = newVal;
          
         change = 'discount';
       }
     }
     
     
     div = document.getElementById('discount_div_319');
     div.style.display = ((true && ($state.acm || $state.student)) && $state.student) ? 'block' : 'none'; 
     
     if (((true && ($state.acm || $state.student)) && $state.student)) {
        if (change === 'discount') {
           console.log('ERROR: mutual exclusion bug on discount');
           break;
        }
        newVal = 20;
        if (newVal !== $state.discount) {
          let elt = document.getElementById('discount_widget_319');
          $state.discount = newVal;
          
          elt.value = newVal;
          
         change = 'discount';
       }
     }
     
     
     div = document.getElementById('discount_div_376');
     div.style.display = (true && !((($state.acm || $state.student)))) ? 'block' : 'none'; 
     
     if ((true && !((($state.acm || $state.student))))) {
        if (change === 'discount') {
           console.log('ERROR: mutual exclusion bug on discount');
           break;
        }
        newVal = 0;
        if (newVal !== $state.discount) {
          let elt = document.getElementById('discount_widget_376');
          $state.discount = newVal;
          
          elt.value = newVal;
          
         change = 'discount';
       }
     }
     
     
     div = document.getElementById('pay_div_414');
     div.style.display = true ? 'block' : 'none'; 
     
     if (true) {
        if (change === 'pay') {
           console.log('ERROR: mutual exclusion bug on pay');
           break;
        }
        newVal = ($state.days * (($state.price - $state.discount)));
        if (newVal !== $state.pay) {
          let elt = document.getElementById('pay_widget_414');
          $state.pay = newVal;
          
          elt.value = newVal;
          
         change = 'pay';
       }
     }
     
     
   } while (change !== '');
}
