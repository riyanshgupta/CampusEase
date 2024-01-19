const button = document.querySelector('#reset-btn')
const email = document.querySelector('#email')
const recover_mail = () => {
  console.log('function called recover_mail')
  const element = document.getElementById('existence');
  if (email.length==0){
    return
  }
  let data = {'email': email.value}
  fetch('/reset-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
  .then(response =>{
    return response.json()
  })
  .then(result => {
    let status= result['status'];
    console.log(result)
    if(status){
      element.innerText = "A recovery mail has been sent to your email address";
      if(element.classList.contains("text-red-600")) element.classList.remove("text-red-600");
      if(element.classList.contains("text-yellow-600")) element.classList.remove("text-yellow-600");
      element.classList.add("text-blue-600");
      email.style.borderColor = "rgb(96 165 250)";
    }
    else {
      element.innerText = "Email doesn't exist";
      if(element.classList.contains("text-blue-600")) element.classList.remove("text-blue-600");
      if(element.classList.contains("text-yellow-600")) element.classList.remove("text-yellow-600");
      element.classList.add("text-red-600");
      email.style.border = "1px solid red";
    }

  })
  .catch(error => {
    console.log(error);
    if(element.classList.contains("text-blue-600")) element.classList.remove("text-blue-600");
    if(element.classList.contains("text-red-600")) element.classList.remove("text-red-600");
    element.innerText = "Something went wrong";
    element.classList.add("text-yellow-600");
    email.style.border = "1px solid yellow";
  })
}
button.addEventListener('click', recover_mail);
document.getElementById('container').addEventListener('keypress',(e)=>{if (e.key === 'Enter') button.click();});
button.disabled = true;
button.style.cursor = "not-allowed";
button.style.opacity = "0.5";

function enable_disable(value){
    if(value.slice(-10)=="@gmail.com"){
      button.disabled = false;
      button.style.cursor = "pointer";
      button.style.opacity = "1";
    }
    else {
      button.disabled = true;
      button.style.cursor = "not-allowed";
      button.style.opacity = "0.5";
    }
}
email.addEventListener('keydown',(e)=>{
  setTimeout(()=>{
    enable_disable(email.value)
  }, 0.1);
})