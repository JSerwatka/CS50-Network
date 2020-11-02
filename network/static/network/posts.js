document.addEventListener('DOMContentLoaded', function() {
    editPostControl();
    updateLikeCounter();
    likePanelAnimationControl();

    document.querySelectorAll(".like-panel").forEach((element) => {
        const postNode = element.parentElement.parentElement;

        // Show user's like type on like button
        fetch(`/like/post/${postNode.id}`)
        .then(response => {
            if (response.status === 201) {
                return response.json();
            }
            else {
                throw new Error("Something went wrong"); //TODO: update message
            }
        })
        .then(result => {
            if (result.like === "True"){
                const likeButton = postNode.querySelector(".like-button");
                likeButton.classList.add("liked");
                
                // Add emoji of user's like type to like button
                switch (result.emojiType) {
                    case "like":
                        likeButton.innerHTML = '<i class="em em---1" aria-role="presentation" aria-label="THUMBS UP SIGN"></i>like';
                        break;
                    case "dislike":
                        likeButton.innerHTML = '<i class="em em--1" aria-role="presentation" aria-label="THUMBS DOWN SIGN"></i>like';
                        break;
                    case "smile":
                        likeButton.innerHTML = '<i class="em em-smile" aria-role="presentation" aria-label="SMILING FACE WITH OPEN MOUTH AND SMILING EYES"></i>like';
                        break;
                    case "heart":
                        likeButton.innerHTML = '<i class="em em-heart" aria-role="presentation" aria-label="HEAVY BLACK HEART"></i>like';
                        break;
                    case "thanks":
                        likeButton.innerHTML = '<i class="em em-bouquet" aria-role="presentation" aria-label="BOUQUET" ></i>like';
                        break;
                    default:
                        likeButton.innerHTML = 'like';
                }
            }
        })
        .catch(error => {
            alert(error);
        })

        // Handle like post/comment
        element.addEventListener('click', (event) => {
            let emojiType;
            // let likeButtonNode;
            let postNode = event.target;
            let csrftoken = getCookie('csrftoken');

            // Look for event's emoji type
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

            // Get like button
            // likeButtonNode = postNode.querySelector(".like-button")
                
            fetch(`/like/post/${postNode.id}`, {
                method: "POST",
                body: JSON.stringify({
                    emojiType: emojiType
                }),
                headers: {"X-CSRFToken": csrftoken}
            })
            .then(response => {
                // Successful like -> update post view
                if (response.status === 204) {
                    console.log(`post id: ${postNode.id} liked successfully`)
                    // TODO: update like button emoji
                    // TODO: update like button class
                    // TODO: update like counter and emoji list
                }
                else {
                    throw new Error("Post doesn't exist or u already liked this post")                        
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
    document.querySelectorAll("div.post").forEach((postNode) => {
        // Get emoji count and current likes count
        const emojiCount = postNode.querySelector("ul.emoji-list").childElementCount
        const oldLikesCount = parseInt(postNode.querySelector("span.like-counter").textContent)
        
        if (oldLikesCount > 0) {
            // Update likes count
            postNode.querySelector("span.like-counter").textContent = `+${oldLikesCount - emojiCount}`
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

