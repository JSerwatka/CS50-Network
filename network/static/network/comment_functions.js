
// Handles POST request and single comment appearance after like
function likeCommentControl(commentNode) {
    let element = commentNode.querySelector(".like-panel")
    // Handle like comment
    element.addEventListener('click', (event) => {
        let emojiType;
        let csrftoken = getCookie('csrftoken');

        // Look for event's emoji type
        // Check if like button is a target
        if (event.target.name === "like") {
            emojiType = event.target.name;
        }
        // Check if emoji list is a target
        else if (typeof event.target.dataset.name === "string"){
            emojiType = event.target.dataset.name;
        }  
        // Something is a target
        else {
            return false;
        }
        // Already liked - update like's emoji type
        if (commentNode.querySelector(".like-button").classList.contains("liked")) {
            fetch(`/like/comment/${commentNode.id}`, {
                method: "PUT",
                body: JSON.stringify({
                    emojiType: emojiType
                }),
                headers: {"X-CSRFToken": csrftoken}
            })
            .then(response => {
                // Successful like -> update comment view
                if (response.status === 204) {
                    console.log(`comment id: ${commentNode.id} like updated successfully`)
                    // Update like button emoji and class
                    updateCommentLikeIcon(commentNode);
                    // Update like counter and emoji list
                    let previousEmojiType = commentNode.querySelector(".like-button > i").dataset.name;
                    updateEmojiList(commentNode, emojiType, previousEmojiType);
                    // Reconnect like amount indicator event to each emoji
                    likesAmountIndicatorControl(commentNode);
                }
                else {
                    throw new Error("Unexpected error")  //TODO: Change message                      
                }
            })
            .catch(error => {
                alert(error)
            })
        }
        // No liked yet - save like
        else {
            fetch(`/like/comment/${commentNode.id}`, {
                method: "POST",
                body: JSON.stringify({
                    emojiType: emojiType
                }),
                headers: {"X-CSRFToken": csrftoken}
            })
            .then(response => {
                // Successful like -> update comment view
                if (response.status === 204) {
                    console.log(`comment id: ${commentNode.id} liked successfully`)
                    // Update like button emoji and class
                    updateCommentLikeIcon(commentNode);
                    // Update like counter and emoji list
                    updateEmojiList(commentNode, emojiType);
                    // Reconnect like amount indicator event to each emoji
                    likesAmountIndicatorControl(commentNode);
                }
                else {
                    throw new Error("Comment doesn't exist or u already liked this comment");                     
                }
            })
            .catch(error => {
                alert(error);
            })
        }
            
    })
}

// Controls asynchronous editing of a comment
function editCommentControl(commentNode) {
    let editButton = commentNode.querySelector(".edit-button")
    let deleteButton = commentNode.querySelector(".delete-edit-panel .btn-danger")
    if (editButton !== null) {
        editButton.addEventListener('click', () => {
            // hide edit/delete button
            editButton.classList.toggle("hidden");
            deleteButton.classList.toggle("hidden");

            // Get comment id
            const commentID = commentNode.id

            // Get content of comment to be edited
            let contentNode = commentNode.querySelector("div.comment-content")
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

            // After cancel - restore orginal comment content
            commentNode.querySelector("button.cancel").addEventListener("click", () => {
                contentNode.innerHTML = contentInnerText;

                // Show edit/delete button
                editButton.classList.toggle("hidden");
                deleteButton.classList.toggle("hidden");
            });

            // After save - update
            commentNode.querySelector("button.save").addEventListener("click", () => {
                // Get content to submit
                const submittedContent = commentNode.querySelector("textarea.new-content").value.trim();
                
                let csrftoken = getCookie('csrftoken');

                // Send PUT request
                fetch("/post-comment/comment", {
                    method: "PUT",
                    body: JSON.stringify({
                        id: commentID,
                        content: submittedContent,
                    }),
                    headers: {"X-CSRFToken": csrftoken}
                })
                .then(response => {
                    // Show edit/delete button
                    editButton.classList.toggle("hidden");
                    deleteButton.classList.toggle("hidden");


                    // if success - update comment's content
                    if (response.status === 204) {
                        contentNode.innerHTML = submittedContent;
                        console.log(`comment id: ${commentID} edited successfully`)
                    }
                    // if error -  restore original comment's content and throw an error
                    else {
                        contentNode.innerHTML = contentInnerText;
                        throw new Error("Comment doesn't exist or user is invalid")                        
                    }
                })
                .catch(error => {
                    alert(error)
                })
            });
        });
    }
}

// Controls deleting of a comment
function deleteCommentControl(commentNode) {
    deleteButton = commentNode.querySelector(".modal-footer > .btn-danger");
    if (deleteButton !== null) {
        deleteButton.addEventListener("click", () => {
            let csrftoken = getCookie('csrftoken');

            // Send DELETE request
            fetch("/post-comment/comment", {
                method: "DELETE",
                body: JSON.stringify({
                    id: commentNode.id,
                }),
                headers: {"X-CSRFToken": csrftoken}
            })
            .then(response => {
                // if success - update comment's content and relaod the page
                if (response.status === 204) {
                    console.log(`Comment id: ${commentNode.id} deleted successfully`)
                    location.reload()
                }
                // if error -  restore original comment's content and throw an error
                else {
                    throw new Error("Comment doesn't exist or user is invalid")                        
                }
            })
            .catch(error => {
                console.log(error)
            })
        })
    }
}

function updateCommentLikeIcon(commentNode){
    // Show user's like type on like button
    fetch(`/like/comment/${commentNode.id}`)
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
            const likeButton = commentNode.querySelector(".like-button");
            likeButton.classList.add("liked");
            // Add emoji of user's like type to like button
            likeButton.innerHTML = emojiNameToHtml(result.emojiType);
        }
    })
    .catch(error => {
        alert(error);
    })
}