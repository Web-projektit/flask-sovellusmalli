const poista_is_invalid = event => {
    let element = event.target;
    if (element.classList.contains('is-invalid')){
      element.classList.remove("is-invalid");    
      element.removeEventListener("input", poista_is_invalid);
      }
    }  
  
/* 
document.addEventListener('DOMContentLoaded', () => {});
*/  
  
(() => {
    'use strict'
    /* Quick_form lisää palvelimen validointivirheestä has-danger-classin ja invalid-feedback-elementin, 
        joka näkyy, jos form-control-classiin lisätään is-invalid ja häipyy, kun is-invalid poistetaan. */
    /*document.querySelectorAll(".has-danger .form-control").forEach(
        element => {
            element.classList.add('is-invalid');
            element.addEventListener("input", poista_is_invalid)
            }
          )*/

    document.querySelectorAll(".is-invalid,:invalid").forEach(
      element => element.addEventListener("input", poista_is_invalid)
      )
    

    const forms = document.querySelectorAll('.needs-validation')
    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
      form.addEventListener('submit', event => {
        if (!form.checkValidity()) {
          event.preventDefault()
          event.stopPropagation()     
          /* 
          Palvelimen lomakekäsittelyn jälkeen validointi palautetaan selaimelle lomaketta
          lähetettäessä. Tällöin selaimen oma validointiviesti asetetaan 
          .invalid-feedback-elementteihin. Huom. invalid-feedback-elementin tulee tässä olla 
          virheellisen elementin sibling. Validointiviesti päivitetään onblur-tapahtumasta. 
          Jos kentän arvo ei läpäise selainvalidointia, selain asettaa kentän :invalid-tilaan,
          jolloin Bootstrap tuo .invalid-feedback-elementin näkyviin, ja tekstinä näkyy näin
          selaimen oma validointivirhetyyppikohtainen validointiviesti (selaimen kielellä). 
          */
          
          /* Quick_form ei lisää Selaimen validointivirheestä invalid-feedback-elementtiä,
             joten se lisätään, jos selain asettaa kentän :invalid-tilaan eikä sitä ole
             lisätty ennestään. */ 
          document.querySelectorAll("input:invalid")
          .forEach(element => {
            console.log(element.name+':'+element.validationMessage)
            /*if (!element.nextElementSibling){
                let feedback = document.createElement('div')
                feedback.classList.add('invalid-feedback')
                element.parentElement.appendChild(feedback)
                }*/
            element.nextElementSibling.innerHTML = element.validationMessage
            element.addEventListener('input', () => 
              element.nextElementSibling.innerHTML = element.validationMessage)
            })    
          }
        form.classList.add('was-validated')
        }, false)
      })
    })()   
  