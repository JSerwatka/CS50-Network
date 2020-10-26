document.addEventListener('DOMContentLoaded', function() {
    editPostControl();

})


function editPostControl() {
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
                // Update post's content
                const submittedContent = document.querySelector("textarea.new-content").value.trim();
                contentNode.innerHTML = submittedContent;

                let csrftoken = getCookie('csrftoken');
                // Send PUT request
                fetch("", {
                    method: "PUT",
                    body: submittedContent,
                    headers: {"X-CSRFToken": csrftoken}
                })
                // .then(response => response.json())
                // .then(result => {
                //     console.log("here we are")
                // })

                // show edit button
                event.target.classList.toggle("hidden");
            });
        });
    });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
