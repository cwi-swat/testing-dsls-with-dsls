var $state = {
  
  yearsInJob: 0,
  
  approvalMessage: "",
  
  interestRate: 0,
  
  employed: false,
  
  totalInterest: 0,
  
  hasCoSigner: false,
  
  not_approvalMessage: "Not Approved",
  
  jobTitle: "",
  
  loanTerm: 0,
  
  age: 0,
  
  hasLicense: false,
  
  loanApproved: false,
  
  loanAmount: 0,
  
  healthcareExpenses: 0,
  
  monthlyExpenses: 0,
  
  income: 0,
  
  retired: false,
  
  annualPension: 0,
  
  totalRepayment: 0,
  
  netPension: 0,
  
  seniorDiscount: false,
  
  monthlyDebts: 0,
  
  yearsRetired: 0,
  
  monthlySalary: 0,
  
  lookingForJob: false,
  
  grade: 0,
  
  inSchool: false,
  
  monthlyPayment: 0,
  
  fullName: "",
  
  annualSavings: 0,
  
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
     
     div = document.getElementById('fullName_div_25');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('age_div_70');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('hasLicense_div_104');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('inSchool_div_183');
     div.style.display = (true && ($state.age < 18)) ? 'block' : 'none'; 
     
     
     div = document.getElementById('grade_div_258');
     div.style.display = ((true && ($state.age < 18)) && $state.inSchool) ? 'block' : 'none'; 
     
     
     div = document.getElementById('employed_div_360');
     div.style.display = ((true && !((($state.age < 18)))) && (($state.age >= 18) && ($state.age <= 65))) ? 'block' : 'none'; 
     
     
     div = document.getElementById('jobTitle_div_445');
     div.style.display = (((true && !((($state.age < 18)))) && (($state.age >= 18) && ($state.age <= 65))) && $state.employed) ? 'block' : 'none'; 
     
     
     div = document.getElementById('yearsInJob_div_496');
     div.style.display = (((true && !((($state.age < 18)))) && (($state.age >= 18) && ($state.age <= 65))) && $state.employed) ? 'block' : 'none'; 
     
     
     div = document.getElementById('monthlySalary_div_578');
     div.style.display = (((true && !((($state.age < 18)))) && (($state.age >= 18) && ($state.age <= 65))) && $state.employed) ? 'block' : 'none'; 
     
     
     div = document.getElementById('monthlyExpenses_div_640');
     div.style.display = (((true && !((($state.age < 18)))) && (($state.age >= 18) && ($state.age <= 65))) && $state.employed) ? 'block' : 'none'; 
     
     
     div = document.getElementById('annualSavings_div_713');
     div.style.display = (((true && !((($state.age < 18)))) && (($state.age >= 18) && ($state.age <= 65))) && $state.employed) ? 'block' : 'none'; 
     
     newVal = ((($state.monthlySalary - $state.monthlyExpenses)) * 12);
     if (newVal !== $state.annualSavings) {
       let elt = document.getElementById('annualSavings_widget_713');
       $state.annualSavings = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('lookingForJob_div_822');
     div.style.display = (((true && !((($state.age < 18)))) && (($state.age >= 18) && ($state.age <= 65))) && !(($state.employed))) ? 'block' : 'none'; 
     
     
     div = document.getElementById('retired_div_910');
     div.style.display = ((true && !((($state.age < 18)))) && !(((($state.age >= 18) && ($state.age <= 65))))) ? 'block' : 'none'; 
     
     
     div = document.getElementById('yearsRetired_div_975');
     div.style.display = (((true && !((($state.age < 18)))) && !(((($state.age >= 18) && ($state.age <= 65))))) && $state.retired) ? 'block' : 'none'; 
     
     
     div = document.getElementById('annualPension_div_1039');
     div.style.display = (((true && !((($state.age < 18)))) && !(((($state.age >= 18) && ($state.age <= 65))))) && $state.retired) ? 'block' : 'none'; 
     
     
     div = document.getElementById('healthcareExpenses_div_1101');
     div.style.display = (((true && !((($state.age < 18)))) && !(((($state.age >= 18) && ($state.age <= 65))))) && $state.retired) ? 'block' : 'none'; 
     
     
     div = document.getElementById('netPension_div_1180');
     div.style.display = (((true && !((($state.age < 18)))) && !(((($state.age >= 18) && ($state.age <= 65))))) && $state.retired) ? 'block' : 'none'; 
     
     newVal = ($state.annualPension - $state.healthcareExpenses);
     if (newVal !== $state.netPension) {
       let elt = document.getElementById('netPension_widget_1180');
       $state.netPension = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('seniorDiscount_div_1296');
     div.style.display = true ? 'block' : 'none'; 
     
     newVal = (($state.age >= 65) && $state.retired);
     if (newVal !== $state.seniorDiscount) {
       let elt = document.getElementById('seniorDiscount_widget_1296');
       $state.seniorDiscount = newVal;
       
       elt.checked = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('income_div_1398');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('monthlyDebts_div_1446');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('hasCoSigner_div_1501');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('loanAmount_div_1564');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('interestRate_div_1608');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('loanTerm_div_1666');
     div.style.display = true ? 'block' : 'none'; 
     
     
     div = document.getElementById('totalInterest_div_1709');
     div.style.display = true ? 'block' : 'none'; 
     
     newVal = (function () { const div = 100; return div !== 0 ? (((($state.loanAmount * $state.interestRate) * $state.loanTerm)) / div) : 0; })();
     if (newVal !== $state.totalInterest) {
       let elt = document.getElementById('totalInterest_widget_1709');
       $state.totalInterest = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('totalRepayment_div_1809');
     div.style.display = true ? 'block' : 'none'; 
     
     newVal = ($state.loanAmount + $state.totalInterest);
     if (newVal !== $state.totalRepayment) {
       let elt = document.getElementById('totalRepayment_widget_1809');
       $state.totalRepayment = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('monthlyPayment_div_1892');
     div.style.display = true ? 'block' : 'none'; 
     
     newVal = (function () { const div = (($state.loanTerm * 12)); return div !== 0 ? ($state.totalRepayment / div) : 0; })();
     if (newVal !== $state.monthlyPayment) {
       let elt = document.getElementById('monthlyPayment_widget_1892');
       $state.monthlyPayment = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('loanApproved_div_1984');
     div.style.display = true ? 'block' : 'none'; 
     
     newVal = (((($state.income > 50000) && ($state.monthlyDebts < 10000))) || $state.hasCoSigner);
     if (newVal !== $state.loanApproved) {
       let elt = document.getElementById('loanApproved_widget_1984');
       $state.loanApproved = newVal;
       
       elt.checked = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('approvalMessage_div_2114');
     div.style.display = (true && $state.loanApproved) ? 'block' : 'none'; 
     
     newVal = "Approved";
     if (newVal !== $state.approvalMessage) {
       let elt = document.getElementById('approvalMessage_widget_2114');
       $state.approvalMessage = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
     div = document.getElementById('not_approvalMessage_div_2214');
     div.style.display = (true && !(($state.loanApproved))) ? 'block' : 'none'; 
     
     newVal = "Not Approved";
     if (newVal !== $state.not_approvalMessage) {
       let elt = document.getElementById('not_approvalMessage_widget_2214');
       $state.not_approvalMessage = newVal;
       
       elt.value = newVal;
       
       change = true;
     }
     
     
   } while (change);
}
