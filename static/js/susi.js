//switch modal 
function switchModal(elementID) {
    var modal = document.getElementById(elementID);
    if (modal.style.display === "block") {
        modal.style.display = "none";
      } else {
        modal.style.display = "block";
      }
  }
  
  //hide modal 
  function hideModal(elementID) {
    var modal = document.getElementById(elementID);
    modal.style.display = "none";
  }

// When the user clicks anywhere outside of the modal, close it
  function addModalClickListener(elementID) {
  document.addEventListener('click', function(event) {
    var modal = document.getElementById(elementID);
    if (event.target == modal) {
      modal.style.display = "none";
    }
  });
}


function addSendToBackendOld(formId, submitId,endpoint) {
    const form = document.getElementById(formId);
    const submit = document.getElementById(submitId);
  
    submit.addEventListener('click', (event) => {
      event.preventDefault(); // prevent the default form submission behavior
      const formData = new FormData(form); // create a new FormData object from the form
      const xhr = new XMLHttpRequest();
      xhr.open('POST', endpoint); // change the endpoint URL to your Flask endpoint
      xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
      xhr.onload = () => {
        if (xhr.status === 200) {
          console.log(xhr.responseText);
        }
      };
      xhr.send(JSON.stringify(Object.fromEntries(formData.entries()))); // convert the FormData object to a plain object and send it as JSON
    });
  }
  

  function addSendToBackend(modalID, formId, submitId, endpoint) {
    const form = document.getElementById(formId);
    const submit = document.getElementById(submitId);
  
    submit.addEventListener('click', (event) => {
      event.preventDefault(); // prevent the default form submission behavior
      const formData = new FormData(form); // create a new FormData object from the form
      const usr = formData.get('email');
      const xhr = new XMLHttpRequest();
      xhr.open('POST', endpoint);
      xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
      xhr.onload = () => {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          if (response.success) { // susi success 

            document.getElementById('user').textContent = 'Logged in as: '+usr;
            document.getElementById(modalID).style.display = "none";
            console.log(response.message);

            // make the form green
            // const formInputs = document.getElementsByClassName("form-input");
            // for (let i = 0; i < formInputs.length; i++) {
            //   formInputs[i].style.backgroundColor = 'rgba(144,238,144,0.8)';
            // };
          } else { // susi fail 
            document.getElementById('user').textContent = 'Logged in as: Guest';
            // document.getElementById('signin-form').style.backgroundColor = 'red';
            const formInputs = document.getElementsByClassName("form-input");
            for (let i = 0; i < formInputs.length; i++) {
              formInputs[i].style.backgroundColor = 'rgba(255, 192, 203, 0.5)';
            };


        }
        }
      };
      xhr.send(JSON.stringify(Object.fromEntries(formData.entries())));
    });
  }
  
