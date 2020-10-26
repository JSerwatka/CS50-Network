document.addEventListener('DOMContentLoaded', function() {
    let editButtons = document.querySelectorAll("div.post .edit-button")

    editButtons.forEach((button) => {
        button.addEventListener('click', (event) => {
            // hide edit button
            event.target.classList.toggle("hidden");


            // Get content of post to be edit
            let contentNode = event.target.previousElementSibling;
            const contentInnerText = contentNode.textContent.trim();
            
            // Populate content with form to fill
            contentNode.innerHTML = `
                <div class="form-group">
                    <textarea class="new-content form-control">${contentInnerText}</textarea>
                </div>
                <div class="form-group">
                    <button class="btn btn-primary cancel">Cancel</button>
                    <button class="btn btn-primary save">Save</button>
                </div>`;

            document.querySelector("button.cancel").addEventListener("click", () => {
                contentNode.innerHTML = contentInnerText;

                // show edit button
                event.target.classList.toggle("hidden");
            });

            document.querySelector("button.save").addEventListener("click", () => {
                const submittedContent = document.querySelector("textarea.new-content").value.trim();
                console.log(submittedContent)
                contentNode.innerHTML = submittedContent;

                // show edit button
                event.target.classList.toggle("hidden");
            });
        });
    });
})