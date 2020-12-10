document.addEventListener('DOMContentLoaded', function() {
    uploadImageValidation();
});
 
function uploadImageValidation() {
    let fileInput = document.querySelector("form input[type=file]");
    let fileInputLabel = document.querySelector(".custom-file-label")
    
    fileInput.addEventListener("change", (event) => {
        let file =  event.target.files[0];
        let fileSize = file.size / 1024 / 1024;
        let fileType = file.type;
        let fileName = file.name;
    
        // Check if file is an image
        if (typeof fileType == "undefined" || fileType.indexOf("image") === -1) {
            document.getElementById("file-type-error").classList.remove("hidden");
            // Clear file button value
            fileInput.value = null;
            // Clear file button placeholder
            fileInputLabel.innerHTML = fileInputLabel.dataset.default;        
        }
        // Check if file exceeds file size limit
        else if (fileSize > 5) {
            document.getElementById("file-size-error").classList.remove("hidden");
            // Clear file button value
            fileInput.value = null;
            // Clear file button placeholder
            fileInputLabel.innerHTML = fileInputLabel.dataset.default;
        }
        // Change file button placeholder to file name
        else {
            fileInputLabel.innerHTML = fileName;
        }
    });
} 

