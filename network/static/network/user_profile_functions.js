  
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
        // Disable main scroll bar
        document.body.style.overflow = "hidden";

        // Show modal
        modal.style.display = "block";

        // Get img info
        modalImg.src = this.src;
        captionText.innerHTML = this.alt;
    }
    
    // When the user clicks on close (x) or outside photo, close the modal
    modal.addEventListener('click', (event) => {
        let closeButton = document.querySelector(".modal-close");

        if (event.target === modal || event.target === closeButton) {
            // Enable main scroll bar
            document.body.style.overflow = "auto";

            // Hide modal
            modal.style.display = "none";
        }
    })
}