//Changing Z-index
function zee_index(documentLF){
  const dropdownButton = document.getElementById("user-dropdown");
  let ok = false;
  document.body.addEventListener('click', function(){
      // console.log("clicked")
      let lst = (dropdownButton.classList);
      // console.log(lst);
      if (lst[lst.length - 1] == 'block'){
          documentLF.classList.add('change-z-index');
          ok=true;
      }
      else if (ok){
          documentLF.classList.remove('change-z-index');
          ok=false;
      }
  });
}
zee_index(document.getElementById("defaultTab"));
zee_index(document.getElementById("overall_tab_content"));

//sending req to backend
const addbtn=document.getElementById('add-items');
const sub_btn = document.getElementById('submit-btn-found');
// let hostelbtn = document.querySelector('#hostel-btn-submit-2')
const a=()=>{
  document.getElementById('report-msg-2').innerHTML="";
  fetch('/send', {
    method: 'POST',
    headers:{
      'Content-Type': 'application/json',
      'credentials': 'include'
    }, 
    body: JSON.stringify({'timestamp':Date.now()})
  })
  .then(response => response.json())
  .then(result=>{
    console.log(result)
  })
  .catch(error=>{console.log(error)})
}

addbtn.addEventListener('click',a); // working fine

document.querySelector('#submit-btn-found').addEventListener('click', (e) => {
  e.preventDefault();
  // let imageFile = undefined;
  let imageFile = document.getElementById('found-item-img').files[0]; // Get the image file from the input field
  let formData = new FormData();
  formData.append('image', imageFile);
  formData.append('product_name',document.getElementById('product_name').value);
  formData.append('product_description', document.getElementById('item-description').value);
  formData.append('contact_number', document.getElementById('mobile_num').value);
  // disable the button here...

  console.log(formData)
  fetch('/items', {
    method: 'POST',
    body: formData
  })
    .then(response => {
      return response.json();
    })
    .then(result => {
      document.getElementById('report-msg-2').innerHTML = result['message'];
        if(result['status']){
          document.getElementById('report-msg-2').classList.remove('text-red-600');
          document.getElementById('report-msg-2').classList.add('text-green-600');
      
        }
        else {
          document.getElementById('report-msg-2').classList.remove('text-green-600');
          document.getElementById('report-msg-2').classList.add('text-red-600');
        }
       console.log(typeof result['status'])
        icon.style.display= "none";
        icon.style.opacity = "0";
        sub_btn.style.opacity = "1";
        sub_btn.style.cursor="pointer";
        console.log(result)
    })
    .catch(error => {
      console.log(error)
      icon.style.display= "none";
      icon.style.opacity = "0";
      sub_btn.style.opacity = "1";
      sub_btn.style.cursor="pointer";
    });
});
// function founded(btn_found){
//   btn_found.addEventListener('click',()=>{
//     btn_found.style.display="none";
//     btn_found.outerHTML=`<<button type="button" id="btn_found"class="text-red-700 hover:text-red border border-red-700  focus:ring-4 focus:outline-none focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center mr-2 mb-2 dark:border-red-500 dark:text-red-500  dark:focus:ring-red-900">Someone has found it :)</button> `;

//   })
// }
// function claimed(btn_found){
//   btn_found.addEventListener('click',()=>{
//     btn_found.style.display="none";
//     btn_found.outerHTML=`<<button type="button" id="btn_found"class="text-red-700 hover:text-red border border-red-700  focus:ring-4 focus:outline-none focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center mr-2 mb-2 dark:border-red-500 dark:text-red-500  dark:focus:ring-red-900">Claimed</button> `;

//   })
// }
// founded(document.getElementById('found-btn1'));
// founded(document.getElementById('found-btn2'));
// founded(document.getElementById('found-btn3'));
// founded(document.getElementById('found-btn4'));

// claimed(document.getElementById('claimed1'));
// claimed(document.getElementById('claimed2'));

let icon = document.getElementById("myIcon-2");

sub_btn.addEventListener("click", function() {
    if (sub_btn.style.opacity === "" || sub_btn.style.opacity === "1") {
        sub_btn.style.opacity = "0";
        icon.style.opacity = "1";
        icon.style.display= "block";
        sub_btn.style.cursor ="none"; 
    }
});

let claimbtn = document.getElementsByName("claim-btn");
for (let i = 0; i < claimbtn.length; i++) {
  claimbtn[i].addEventListener("click", function() {
    console.log("Claiming");
    let id = String(claimbtn[i].id);
    id = id.split("-")[1];
    console.log(id)
    let data = {'id': Number(id)};
    fetch('/claim', {
        method: 'POST',
      headers:{
        'Content-Type': 'application/json',
      },
        body: JSON.stringify(data)
      })
        .then(response => {
          return response.json();
        })
          .then(result => {
            console.log(result);
          })
            .catch(error =>{
              console.log(error);
            })
    
    // cliambtn[i].style.display="none";
    // cliambtn[i].outerHTML=`<button type="button" id="claim-btn" class="text-red-700 hover:text-red border border-red-700 focus:ring-4 focus:outline-none focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center mr-2 mb-2 dark:border-red-500 dark:text-red-500  dark:focus:ring-red-900" disabled>Claimed by</button> `;
  });
}