function attachCheckboxListeners(checklistId, endpointUrl) {
  const checklist = document.getElementById(checklistId);

  // Attach event listener to checkboxes
  checklist.addEventListener('change', (event) => {
    const item = event.target;
    const isChecked = item.checked;
    const name = item.name;
    // Send AJAX request to Flask
    const xhr = new XMLHttpRequest();
    xhr.open('POST', endpointUrl);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.onload = () => {
      if (xhr.status === 200) {
        console.log(xhr.responseText);
      }
    };
    xhr.send(JSON.stringify({ name: name, isChecked: isChecked }));
  });
}
