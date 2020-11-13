
// Handles POST request and single post appearance after like
function likePostControl(postNode) {
    let element = postNode.querySelector(".like-panel")
    // Handle like post/comment
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
        if (postNode.querySelector(".like-button").classList.contains("liked")) {
            fetch(`/like/post/${postNode.id}`, {
                method: "PUT",
                body: JSON.stringify({
                    emojiType: emojiType
                }),
                headers: {"X-CSRFToken": csrftoken}
            })
            .then(response => {
                // Successful like -> update post view
                if (response.status === 204) {
                    console.log(`post id: ${postNode.id} like updated successfully`)
                    // Update like button emoji and class
                    updatePostLikeIcon(postNode);
                    // Update like counter and emoji list
                    let previousEmojiType = postNode.querySelector(".like-button > i").dataset.name;
                    updateEmojiList(postNode, emojiType, previousEmojiType);
                    // Reconnect like amount indicator event to each emoji
                    likesAmountIndicatorControl(postNode);
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
                    // Update like button emoji and class
                    updatePostLikeIcon(postNode);
                    // Update like counter and emoji list
                    updateEmojiList(postNode, emojiType);
                    // Reconnect like amount indicator event to each emoji
                    likesAmountIndicatorControl(postNode);
                }
                else {
                    throw new Error("Post doesn't exist or u already liked this post");                     
                }
            })
            .catch(error => {
                alert(error);
            })
        }
            
    })
} 

// Controls asynchronous editing of a post
function editPostControl(postNode) {
    let editButton = postNode.querySelector(".edit-button")
    let deleteButton = postNode.querySelector(".delete-edit-panel .btn-danger")
    if (editButton !== null) {
        editButton.addEventListener('click', () => {
            // hide edit/delete button
            editButton.classList.toggle("hidden");
            deleteButton.classList.toggle("hidden");

            // Get post id
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
            postNode.querySelector("button.cancel").addEventListener("click", () => {
                contentNode.innerHTML = contentInnerText;

                // show edit/delete button
                editButton.classList.toggle("hidden");
                deleteButton.classList.toggle("hidden");
            });

            // After save - update
            postNode.querySelector("button.save").addEventListener("click", () => {
                // Get content to submit
                const submittedContent = postNode.querySelector("textarea.new-content").value.trim();
                
                let csrftoken = getCookie('csrftoken');

                // Send PUT request
                fetch("/post-comment/post", {
                    method: "PUT",
                    body: JSON.stringify({
                        id: postID,
                        content: submittedContent,
                    }),
                    headers: {"X-CSRFToken": csrftoken}
                })
                .then(response => {
                    // Show edit/delete button
                    editButton.classList.toggle("hidden");
                    deleteButton.classList.toggle("hidden");

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
            });
        });
    }
}

// Controls deleting of a post
function deletePostControl(postNode) {
    let deleteButton = postNode.querySelector(".modal-footer > .btn-danger");
    if (deleteButton !== null) {
        deleteButton.addEventListener("click", () => {
            let csrftoken = getCookie('csrftoken');

            // Send DELETE request
            fetch("/post-comment/post", {
                method: "DELETE",
                body: JSON.stringify({
                    id: postNode.id,
                }),
                headers: {"X-CSRFToken": csrftoken}
            })
            .then(response => {
                // if success - update post's content and relaod the page
                if (response.status === 204) {
                    console.log(`post id: ${postNode.id} deleted successfully`)
                    location.reload()
                }
                // if error -  restore original post's content and throw an error
                else {
                    throw new Error("Post doesn't exist or user is invalid")                        
                }
            })
            .catch(error => {
                console.log(error)
            })
        })
    }
}

function updatePostLikeIcon(postNode){
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
            likeButton.innerHTML = emojiNameToHtml(result.emojiType);
        }
    })
    .catch(error => {
        alert(error);
    })
}