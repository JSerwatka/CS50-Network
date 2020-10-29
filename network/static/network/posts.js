document.addEventListener('DOMContentLoaded', function() {
    editPostControl();
    updateLikeCounter();
    likePanelAnimationControl();

    document.querySelectorAll(".like-panel").forEach((element) => {
        element.addEventListener('click', (event) => {
            let emojiType;
            let postNode = event.target;
            let csrftoken = getCookie('csrftoken');

            if (event.target.name === "like") {
                emojiType = event.target.name;

            }
            else if (typeof event.target.firstChild.name === "string"){
                emojiType = event.target.firstChild.name;
            }  
            else {
                return false;
            }

            // Get post node regarding of what triggered it
            while (postNode.className !== "post") { 
                postNode = postNode.parentElement;
            }

            fetch("/like", {
                method: "POST",
                body: JSON.stringify({
                    post: postNode.id,
                    comment: "",
                    emojiType: emojiType
                }),
                headers: {"X-CSRFToken": csrftoken}
            })
            .then(response => {
                if (response.status === 204) {
                    console.log(`post id: ${postNode.id} liked successfully`)
                }
                else {
                    throw new Error("Post doesn't exist or user is invalid")                        
                }
            })
            .catch(error => {
                alert(error)
            })
        })
    })


})

function editPostControl() {
    let editButtons = document.querySelectorAll("div.post .edit-button")

    editButtons.forEach((button) => {
        button.addEventListener('click', (event) => {
            // hide edit button
            event.target.classList.toggle("hidden");

            // Get post node and post id
            const postNode = event.target.parentElement
            const postID = postNode.id

            // Get content of post to be edited
            let contentNode = postNode.querySelector("div.post-content")
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

            // After cancel - restore orginal post content
            document.querySelector("button.cancel").addEventListener("click", () => {
                contentNode.innerHTML = contentInnerText;

                // show edit button
                event.target.classList.toggle("hidden");
            });

            // After save - update
            document.querySelector("button.save").addEventListener("click", () => {
                // Get content to submit
                const submittedContent = document.querySelector("textarea.new-content").value.trim();
                
                let csrftoken = getCookie('csrftoken');

                // Send PUT request
                fetch("/", {
                    method: "PUT",
                    body: JSON.stringify({
                        id: postID,
                        content: submittedContent,
                    }),
                    headers: {"X-CSRFToken": csrftoken}
                })
                .then(response => {
                    // if success - update post's content
                    if (response.status === 204) {
                        
                        contentNode.innerHTML = submittedContent;

                        console.log(`post id: ${postID} edited successfully`)
                    }
                    // if error -  restore original post's content and throw an error
                    else {
                        contentNode.innerHTML = contentInnerText;

                        throw new Error("Post doesn't exist or user is invalid")                        
                    }
                })
                .catch(error => {
                    alert(error)
                })

                // Show edit button
                event.target.classList.toggle("hidden");
            });
        });
    });
}

function updateLikeCounter() {
    document.querySelectorAll("div.post").forEach((post) => {
        // Get emoji count and current likes count
        const emojiCount = post.querySelector("ul.emoji-list").childElementCount
        const oldLikesCount = parseInt(post.querySelector("span.like-counter").textContent)
        
        if (oldLikesCount > 0) {
            // Update likes count
            post.querySelector("span.like-counter").textContent = `+${oldLikesCount - emojiCount}`
        }
    })
}


function likePanelAnimationControl() {
    document.querySelectorAll(".like-panel").forEach((element) => {
        const emojiPanel = element.querySelector(".emoji-choice");
        let timeoutVar;

        // On hover show like-panel
        element.addEventListener("mouseover", () => {
            clearTimeout(timeoutVar)
            emojiPanel.classList.remove("hidden");
            emojiPanel.classList.add("like-panel-in");
        })

        // On hover out hide like-panel after 1s
        element.addEventListener("mouseout", () => {
            timeoutVar = setTimeout(() => {
                emojiPanel.classList.remove("like-panel-in");
                emojiPanel.classList.add("hidden");
            }, 1000)
        })
    })
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

