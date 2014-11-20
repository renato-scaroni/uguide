var main = function() {
  var checked=false;
  function checkedAll(){
   var c = document.getElementsByName("viju");
   var checkboxesChecked = [];
  // loop over them all
  for (var i=0; i<c.length; i++) {
  // And stick the checked ones onto an array...
  if (c[i].checked) {
    checkboxesChecked.push(c[i]);
      }
 }

  
  for (var j=0; j<checkboxesChecked.length; j++) {
      // iterate the pushed values
       alert(checkboxesChecked[j].value);

 }

}


$(document).ready(main);