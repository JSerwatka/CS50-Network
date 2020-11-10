  
document.addEventListener('DOMContentLoaded', function() {
    uploadImageValidation();
});
 
function uploadImageValidation() {
    let fileInput = document.querySelector("form input[type=file]");
    
    fileInput.addEventListener("change", (event) => {
        let file =  event.target.files[0];
        let fileSize = file.size / 1024 / 1024;
        let fileType = file.type;
    
        // Check if file is an image
        if (typeof fileType == "undefined" || fileType.indexOf("image") === -1) {
            document.getElementById("file-type-error").classList.remove("hidden")
            fileInput.value = null ;              
        }
        // Check if file exceeds file size limit
        else if (fileSize > 5) {
            document.getElementById("file-size-error").classList.remove("hidden")
            fileInput.value = null;
        }
    });
} 
