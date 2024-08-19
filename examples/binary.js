var $state = {};
function $init() {
  
  $state.x_1_5 = false;
  
  $state.x_3_4 = false;
  
  $state.answer_1_2 = 0;
  
  $state.answer_3_4 = 0;
  
  $state.answer_6_7 = 0;
  
  $state.answer_7_8 = 0;
  
  $state.answer_8_9 = 0;
  
  $state.x_1_3 = false;
  
  $state.x_5_6 = false;
  
  $state.answer_2_3 = 0;
  
  $state.x_5_7 = false;
  
  $state.answer_9_10 = 0;
  
  $state.x_7_8 = false;
  
  $state.answer_4_5 = 0;
  
  $state.x_8_9 = false;
  
  $state.answer_5_6 = 0;
  
  $state.x_1_10 = false;
  
  $state.answer_19_20 = 19;
  
  $state.x_17_18 = false;
  
  $state.x_18_19 = false;
  
  $state.x_10_11 = false;
  
  $state.x_12_13 = false;
  
  $state.x_13_14 = false;
  
  $state.x_15_16 = false;
  
  $state.x_10_12 = false;
  
  $state.x_15_17 = false;
  
  $state.x_10_15 = false;
  
  $state.x_1_2 = false;
  
  $state.answer_10_11 = 0;
  
  $state.answer_11_12 = 0;
  
  $state.answer_12_13 = 0;
  
  $state.answer_13_14 = 0;
  
  $state.answer_14_15 = 0;
  
  $state.answer_15_16 = 0;
  
  $state.answer_16_17 = 0;
  
  $state.answer_17_18 = 0;
  
  $state.answer_18_19 = 0;
  
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
     
     div = document.getElementById('x_1_10_div_16');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('x_1_5_div_86');
     div.style.display = (true && $state.x_1_10) ? 'block' : 'none'; 
     
     
     div = document.getElementById('x_1_3_div_157');
     div.style.display = ((true && $state.x_1_10) && $state.x_1_5) ? 'block' : 'none'; 
     
     
     div = document.getElementById('x_1_2_div_232');
     div.style.display = (((true && $state.x_1_10) && $state.x_1_5) && $state.x_1_3) ? 'block' : 'none'; 
     
     
     div = document.getElementById('answer_1_2_div_311');
     div.style.display = ((((true && $state.x_1_10) && $state.x_1_5) && $state.x_1_3) && $state.x_1_2) ? 'block' : 'none'; 
     
     newVal = (1);
     if (newVal !== $state.answer_1_2) {
       let elt = document.getElementById('answer_1_2_widget_311');
       $state.answer_1_2 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('answer_2_3_div_388');
     div.style.display = ((((true && $state.x_1_10) && $state.x_1_5) && $state.x_1_3) && !(($state.x_1_2))) ? 'block' : 'none'; 
     
     newVal = (2);
     if (newVal !== $state.answer_2_3) {
       let elt = document.getElementById('answer_2_3_widget_388');
       $state.answer_2_3 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('x_3_4_div_470');
     div.style.display = (((true && $state.x_1_10) && $state.x_1_5) && !(($state.x_1_3))) ? 'block' : 'none'; 
     
     
     div = document.getElementById('answer_3_4_div_549');
     div.style.display = ((((true && $state.x_1_10) && $state.x_1_5) && !(($state.x_1_3))) && $state.x_3_4) ? 'block' : 'none'; 
     
     newVal = (3);
     if (newVal !== $state.answer_3_4) {
       let elt = document.getElementById('answer_3_4_widget_549');
       $state.answer_3_4 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('answer_4_5_div_627');
     div.style.display = ((((true && $state.x_1_10) && $state.x_1_5) && !(($state.x_1_3))) && !(($state.x_3_4))) ? 'block' : 'none'; 
     
     newVal = (4);
     if (newVal !== $state.answer_4_5) {
       let elt = document.getElementById('answer_4_5_widget_627');
       $state.answer_4_5 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('x_5_7_div_711');
     div.style.display = ((true && $state.x_1_10) && !(($state.x_1_5))) ? 'block' : 'none'; 
     
     
     div = document.getElementById('x_5_6_div_786');
     div.style.display = (((true && $state.x_1_10) && !(($state.x_1_5))) && $state.x_5_7) ? 'block' : 'none'; 
     
     
     div = document.getElementById('answer_5_6_div_865');
     div.style.display = ((((true && $state.x_1_10) && !(($state.x_1_5))) && $state.x_5_7) && $state.x_5_6) ? 'block' : 'none'; 
     
     newVal = (5);
     if (newVal !== $state.answer_5_6) {
       let elt = document.getElementById('answer_5_6_widget_865');
       $state.answer_5_6 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('answer_6_7_div_943');
     div.style.display = ((((true && $state.x_1_10) && !(($state.x_1_5))) && $state.x_5_7) && !(($state.x_5_6))) ? 'block' : 'none'; 
     
     newVal = (6);
     if (newVal !== $state.answer_6_7) {
       let elt = document.getElementById('answer_6_7_widget_943');
       $state.answer_6_7 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('x_7_8_div_1025');
     div.style.display = (((true && $state.x_1_10) && !(($state.x_1_5))) && !(($state.x_5_7))) ? 'block' : 'none'; 
     
     
     div = document.getElementById('answer_7_8_div_1104');
     div.style.display = ((((true && $state.x_1_10) && !(($state.x_1_5))) && !(($state.x_5_7))) && $state.x_7_8) ? 'block' : 'none'; 
     
     newVal = (7);
     if (newVal !== $state.answer_7_8) {
       let elt = document.getElementById('answer_7_8_widget_1104');
       $state.answer_7_8 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('x_8_9_div_1182');
     div.style.display = ((((true && $state.x_1_10) && !(($state.x_1_5))) && !(($state.x_5_7))) && !(($state.x_7_8))) ? 'block' : 'none'; 
     
     
     div = document.getElementById('answer_8_9_div_1265');
     div.style.display = (((((true && $state.x_1_10) && !(($state.x_1_5))) && !(($state.x_5_7))) && !(($state.x_7_8))) && $state.x_8_9) ? 'block' : 'none'; 
     
     newVal = (8);
     if (newVal !== $state.answer_8_9) {
       let elt = document.getElementById('answer_8_9_widget_1265');
       $state.answer_8_9 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('answer_9_10_div_1349');
     div.style.display = (((((true && $state.x_1_10) && !(($state.x_1_5))) && !(($state.x_5_7))) && !(($state.x_7_8))) && !(($state.x_8_9))) ? 'block' : 'none'; 
     
     newVal = (9);
     if (newVal !== $state.answer_9_10) {
       let elt = document.getElementById('answer_9_10_widget_1349');
       $state.answer_9_10 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('x_10_15_div_1446');
     div.style.display = (true && !(($state.x_1_10))) ? 'block' : 'none'; 
     
     
     div = document.getElementById('x_10_12_div_1523');
     div.style.display = ((true && !(($state.x_1_10))) && $state.x_10_15) ? 'block' : 'none'; 
     
     
     div = document.getElementById('x_10_11_div_1604');
     div.style.display = (((true && !(($state.x_1_10))) && $state.x_10_15) && $state.x_10_12) ? 'block' : 'none'; 
     
     
     div = document.getElementById('answer_10_11_div_1689');
     div.style.display = ((((true && !(($state.x_1_10))) && $state.x_10_15) && $state.x_10_12) && $state.x_10_11) ? 'block' : 'none'; 
     
     newVal = (10);
     if (newVal !== $state.answer_10_11) {
       let elt = document.getElementById('answer_10_11_widget_1689');
       $state.answer_10_11 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('answer_11_12_div_1770');
     div.style.display = ((((true && !(($state.x_1_10))) && $state.x_10_15) && $state.x_10_12) && !(($state.x_10_11))) ? 'block' : 'none'; 
     
     newVal = (11);
     if (newVal !== $state.answer_11_12) {
       let elt = document.getElementById('answer_11_12_widget_1770');
       $state.answer_11_12 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('x_12_13_div_1855');
     div.style.display = (((true && !(($state.x_1_10))) && $state.x_10_15) && !(($state.x_10_12))) ? 'block' : 'none'; 
     
     
     div = document.getElementById('answer_12_13_div_1940');
     div.style.display = ((((true && !(($state.x_1_10))) && $state.x_10_15) && !(($state.x_10_12))) && $state.x_12_13) ? 'block' : 'none'; 
     
     newVal = (12);
     if (newVal !== $state.answer_12_13) {
       let elt = document.getElementById('answer_12_13_widget_1940');
       $state.answer_12_13 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('x_13_14_div_2021');
     div.style.display = ((((true && !(($state.x_1_10))) && $state.x_10_15) && !(($state.x_10_12))) && !(($state.x_12_13))) ? 'block' : 'none'; 
     
     
     div = document.getElementById('answer_13_14_div_2110');
     div.style.display = (((((true && !(($state.x_1_10))) && $state.x_10_15) && !(($state.x_10_12))) && !(($state.x_12_13))) && $state.x_13_14) ? 'block' : 'none'; 
     
     newVal = (13);
     if (newVal !== $state.answer_13_14) {
       let elt = document.getElementById('answer_13_14_widget_2110');
       $state.answer_13_14 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('answer_14_15_div_2197');
     div.style.display = (((((true && !(($state.x_1_10))) && $state.x_10_15) && !(($state.x_10_12))) && !(($state.x_12_13))) && !(($state.x_13_14))) ? 'block' : 'none'; 
     
     newVal = (14);
     if (newVal !== $state.answer_14_15) {
       let elt = document.getElementById('answer_14_15_widget_2197');
       $state.answer_14_15 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('x_15_17_div_2296');
     div.style.display = ((true && !(($state.x_1_10))) && !(($state.x_10_15))) ? 'block' : 'none'; 
     
     
     div = document.getElementById('x_15_16_div_2377');
     div.style.display = (((true && !(($state.x_1_10))) && !(($state.x_10_15))) && $state.x_15_17) ? 'block' : 'none'; 
     
     
     div = document.getElementById('answer_15_16_div_2462');
     div.style.display = ((((true && !(($state.x_1_10))) && !(($state.x_10_15))) && $state.x_15_17) && $state.x_15_16) ? 'block' : 'none'; 
     
     newVal = (15);
     if (newVal !== $state.answer_15_16) {
       let elt = document.getElementById('answer_15_16_widget_2462');
       $state.answer_15_16 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('answer_16_17_div_2543');
     div.style.display = ((((true && !(($state.x_1_10))) && !(($state.x_10_15))) && $state.x_15_17) && !(($state.x_15_16))) ? 'block' : 'none'; 
     
     newVal = (16);
     if (newVal !== $state.answer_16_17) {
       let elt = document.getElementById('answer_16_17_widget_2543');
       $state.answer_16_17 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('x_17_18_div_2628');
     div.style.display = (((true && !(($state.x_1_10))) && !(($state.x_10_15))) && !(($state.x_15_17))) ? 'block' : 'none'; 
     
     
     div = document.getElementById('answer_17_18_div_2713');
     div.style.display = ((((true && !(($state.x_1_10))) && !(($state.x_10_15))) && !(($state.x_15_17))) && $state.x_17_18) ? 'block' : 'none'; 
     
     newVal = (17);
     if (newVal !== $state.answer_17_18) {
       let elt = document.getElementById('answer_17_18_widget_2713');
       $state.answer_17_18 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('x_18_19_div_2794');
     div.style.display = ((((true && !(($state.x_1_10))) && !(($state.x_10_15))) && !(($state.x_15_17))) && !(($state.x_17_18))) ? 'block' : 'none'; 
     
     
     div = document.getElementById('answer_18_19_div_2883');
     div.style.display = (((((true && !(($state.x_1_10))) && !(($state.x_10_15))) && !(($state.x_15_17))) && !(($state.x_17_18))) && $state.x_18_19) ? 'block' : 'none'; 
     
     newVal = (18);
     if (newVal !== $state.answer_18_19) {
       let elt = document.getElementById('answer_18_19_widget_2883');
       $state.answer_18_19 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('answer_19_20_div_2970');
     div.style.display = (((((true && !(($state.x_1_10))) && !(($state.x_10_15))) && !(($state.x_15_17))) && !(($state.x_17_18))) && !(($state.x_18_19))) ? 'block' : 'none'; 
     
     newVal = (19);
     if (newVal !== $state.answer_19_20) {
       let elt = document.getElementById('answer_19_20_widget_2970');
       $state.answer_19_20 = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
   } while (change);
}
