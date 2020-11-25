  
document.addEventListener('DOMContentLoaded', function() {
    imgModal();
});
 
function imgModal() {
    // Get the modal
    let modal = document.querySelector(".img-modal");
    
    // Get the image and insert it inside the modal - use its "alt" text as a caption
    let img = document.querySelector(".profile-picture > img.round-picture");
    let modalImg = document.querySelector(".img-modal .modal-content");
    let captionText = document.getElementById("modal-img-caption");
    img.onclick = function(){
        modal.style.display = "block";
        modalImg.src = this.src;
        captionText.innerHTML = this.alt;
    }
    
    // Get the element that closes the modal
    let closeButton = document.querySelector(".modal-close");
    
    // When the user clicks on close (x), close the modal
    closeButton.onclick = function() {
        modal.style.display = "none";
    }
}