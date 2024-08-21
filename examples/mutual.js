var $state = {
  
  num: 0,
  
  x: true,
  
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
     
     div = document.getElementById('num_div_31');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('x_div_84');
     div.style.display = (true && ($state.num >= 0)) ? 'block' : 'none'; 
     
     
     div = document.getElementById('x_div_134');
     div.style.display = (true && ($state.num <= 0)) ? 'block' : 'none'; 
     
     newVal = true;
     if (newVal !== $state.x) {
       let elt = document.getElementById('x_widget_134');
       $state.x = newVal;
       
       elt.checked = newVal;
       
       change = true;
     }
     
     
   } while (change);
}
