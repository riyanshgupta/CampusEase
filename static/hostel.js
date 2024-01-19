let hostelbtn = document.querySelector('#hostel-btn-submit')
let addbtn = document.querySelector('#add-complain-btn')
const a=()=>{
  document.getElementById('report-msg').innerHTML="";
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
const getVal=(s)=>{
    let radioInputs = document.getElementsByName(s);
    for (let i = 0; i < radioInputs.length; i++) {
        if (radioInputs[i].checked)  return radioInputs[i].value;
    }
}
addbtn.addEventListener('click',a);
document.querySelector('#hostel-btn-submit').addEventListener('click', (e) => {
  console.log("here");
  e.preventDefault();
  let imageFile = undefined;
  if (document.getElementById('hostel-complain-img') != null) imageFile = document.getElementById('hostel-complain-img').files[0]; // Get the image file from the input field
  let formData = new FormData();
  if (imageFile!==undefined) formData.append('image', imageFile);
  formData.append('hostel', getVal('default-radio'));
  formData.append('description', document.getElementById('description').value);
  formData.append('room', document.getElementById('room_no').value);
  formData.append('type', getVal('type')); // make the default-radio as type
  formData.append('mobile', document.getElementById('mobile_no').value);
  // disable the button here...
  
  
  fetch('/hostel-complaints', {
    method: 'POST',
    body: formData
  })
    .then(response => {
      
      return response.json();
    })
    .then(result => {
     document.getElementById('report-msg').innerHTML = result['message'];
      if(result['status']){
        document.getElementById('report-msg').classList.remove('text-red-600');
        document.getElementById('report-msg').classList.add('text-green-600');
        document.getElementById('total_cnt').innerHTML=result['count'];
        let htmlContent = `
        <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600">
          <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">
            ${result['complain_date']}
          </th>
          <td class="px-6 py-4">
            ${result['complain_type']}
          </td>
          <td class="px-6 py-4">
            ${result['complain_description']}
          </td>
        </tr>
        `;
        if (document.getElementById('add_row').innerText == "") document.getElementById('add_row').innerHTML = htmlContent;
        document.getElementById('add_row').insertAdjacentHTML('beforeend', htmlContent);   
      }
      else {
        document.getElementById('report-msg').classList.remove('text-green-600');
        document.getElementById('report-msg').classList.add('text-red-600');
      }
     console.log(typeof result['status'])
      icon.style.display= "none";
      icon.style.opacity = "0";
      hostelbtn.style.opacity = "1";
      hostelbtn.style.cursor="pointer";
    })
    .catch(error => {
      icon.style.display= "none";
      icon.style.opacity = "0";
      hostelbtn.style.opacity = "1";
      hostelbtn.style.cursor="pointer";
    });
});

function keep_in_front(documentLF){
  const dropdownButton = document.getElementById("user-dropdown");
  let ok = false;
  document.body.addEventListener('click', function(){  
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
keep_in_front( document.getElementById("total_complaint_grid-1"));
keep_in_front(document.getElementById("total_complaint_grid-2"));



var icon = document.getElementById("myIcon");

hostelbtn.addEventListener("click", function() {
    if (hostelbtn.style.opacity === "" || hostelbtn.style.opacity === "1") {
        hostelbtn.style.opacity = "0";
        icon.style.opacity = "1";
        icon.style.display= "block";
        hostelbtn.style.cursor ="none"; 
    }
});