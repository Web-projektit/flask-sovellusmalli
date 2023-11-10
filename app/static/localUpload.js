const url = '/save-local'
console.log(`preview_org:${preview_org},img_org:${img_org}`)

const uploadFile = file => {  
console.log('uploadFile:',file.name)    
document.querySelector('#preview').src = URL.createObjectURL(file);
const postData = new FormData();
const csrfToken = document.querySelector('#csrf_token').value;
postData.append('file', file);
//postData.append('csrf-token', csrfToken);
fetch(url,{
    method:'POST',
    headers: { 'X-CSRF-TOKEN': csrfToken },
    body:postData})
.then(response => {
    if (!response.ok) {
        throw new Error(`HTTP-virhe, status: ${response.status}`)
        }
    return response.json(); // Continue with processing the response if it's OK
    })
.then(success => {
    console.log(success)  
    if (success.virhe) {
        // alert(success.virhe)
        document.querySelector('#invalid-image').innerHTML = success.virhe
        }    
    else if (success.msg){
        // document.querySelector('#img').value = file.name;
        /* Huom. file.name saattaa sisältää merkkejä, jotka secure_filename
           suodattaa pois tiedoston nimestä tiedostoa tallennettaessa. 
           Lomakekenttään img on tietokantaan tallennusta varten sijoitettava 
           tämä suodatettu tiedostonimi. Esim. "DALL·E 2023-10-23 17.04.48 - 
           Large minimalistic fivecon logo in warm tones representing a 
           teacher with a whiteboard, where the board displays a prominent 
           web page layout icon in c.png". */
        document.querySelector('#img').value = success.img
        document.querySelector('#invalid-image').innerHTML = ''
        alert(success.msg)
        }
    })
.catch(error => {
    console.log(error.message)
    // alert('Tiedostoa ei tallennettu.')
    document.querySelector('#invalid-image').innerHTML = error.message
    })
}


/* Function to get the temporary signed request from the Python app.
If request successful, continue to upload the file using this signed
request. */
/* const getRequest = file => {
fetch(`/sign-local?file-name=${file.name}&file-type=${encodeURIComponent(file.type)}`)
.then(response => response.json())
.then(response => {
    console.log('response:',response)
    uploadFile(file, response.url);
    })
.catch(error => {
    console.log(error)
    alert('Tiedostolle ei löytynyt tallennusosoitetta')
    })
}
*/

/* 
Function called when file input updated. If there is a file selected, then
start upload procedure by asking for a signed request from the app.
*/
const initUpload = () => {
const files = document.querySelector('#file-input').files;
const file = files[0];
if(!file){
    return alert('No file selected.');
    }
uploadFile(file);
document.querySelector('#file-clear').disabled = false;
document.querySelector('#file-reload').disabled = false;
}

const clearFile = () => {
document.querySelector('#preview').src = "/static/default_profile.png";
document.querySelector('#img').value = "";
document.querySelector('#file-clear').disabled = true
document.querySelector('#file-reload').disabled = false
document.querySelector('#apulomake').reset()
document.querySelector('#invalid-image').innerHTML = ''
}

const reloadFile = () => {
document.querySelector('#preview').src = preview_org;
document.querySelector('#img').value = img_org;
document.querySelector('#file-reload').disabled = true
document.querySelector('#apulomake').reset()
document.querySelector('#invalid-image').innerHTML = ''
}
    
/* Bind listeners when the page loads.*/
(() => {
    const file_clear = document.querySelector('#file-clear') 
    const file_reload = document.querySelector('#file-reload') 
    if (!document.querySelector("#img").value) {
        file_clear.disabled = true
        }
    document.querySelector('#file-input').onchange = initUpload;
    file_clear.onclick = clearFile;
    file_reload.onclick = reloadFile;
})();