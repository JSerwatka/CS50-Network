
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
        // Incorrect target
        else {
            return false;
        }
        // Already liked - update like's emoji type
        if (postNode.querySelector(".like-button").classList.contains("liked")) {
            fetch(`/like/post/${postNode.id.substr(5)}`, {
                method: "PUT",
                body: JSON.stringify({
                    emojiType: emojiType
                }),
                headers: {"X-CSRFToken": csrftoken}
            })
            .then(async(response) => {
                // Successful like -> update post view
                if (response.status === 201) {
                    console.log(`post id: ${postNode.id.substr(5)} like updated successfully`)
                    // Update like button emoji and class
                    updatePostLikeIcon(postNode);
                    // Update like counter and emoji list
                    let previousEmojiType = postNode.querySelector(".like-button > i").dataset.name;
                    updateEmojiList(postNode, emojiType, previousEmojiType);
                    // Reconnect like amount indicator event to each emoji
                    likesAmountIndicatorControl(postNode);
                }
                else {
                    let response_body = await response.json();

                    throw new Error(response_body.error) ;                     
                }
            })
            .catch(error => {
                alert(error);
                location.reload();
            })
        }
        // No liked yet - save like
        else {
            fetch(`/like/post/${postNode.id.substr(5)}`, {
                method: "POST",
                body: JSON.stringify({
                    emojiType: emojiType
                }),
                headers: {"X-CSRFToken": csrftoken}
            })
            .then(async(response) => {
                // Successful like -> update post view
                if (response.status === 201) {
                    console.log(`post id: ${postNode.id.substr(5)} liked successfully`)
                    // Update like button emoji and class
                    updatePostLikeIcon(postNode);
                    // Update like counter and emoji list
                    updateEmojiList(postNode, emojiType);
                    // Reconnect like amount indicator event to each emoji
                    likesAmountIndicatorControl(postNode);
                }
                else {
                    let response_body = await response.json();

                    throw new Error(response_body.error) ;                     
                }
            })
            .catch(error => {
                alert(error);
                location.reload();
            })
        }
            
    })
} 

// Controls asynchronous editing of a post
function editPostControl(postNode) {
    let modalDialog = postNode.querySelector(".edit-modal");

    if (modalDialog !== null) {
        $(modalDialog).on('show.bs.modal', () => {
            // Get save button and modal body
            let saveButton = modalDialog.querySelector(".modal-footer > .btn-primary");
            let modalBody = modalDialog.querySelector(".modal-body");

            // Get post id
            const postID = postNode.id.substr(5);

            // Get content of post to be edited
            let contentNode = postNode.querySelector("div.post-content");
            const contentInnerText = contentNode.textContent.trim();
            
            // Populate content with form to fill
            modalBody.innerHTML = `<textarea class="new-content form-control">${contentInnerText}</textarea>`;

            // After save - update
            saveButton.addEventListener("click", () => {
                // Get content to submit
                const submittedContent = modalBody.querySelector("textarea.new-content").value.trim();
                
                let csrftoken = getCookie('csrftoken');

                // Hide modal
                $(modalDialog).modal('hide');

                // Send PUT request
                fetch("/post-comment/post", {
                    method: "PUT",
                    body: JSON.stringify({
                        id: postID,
                        content: submittedContent,
                    }),
                    headers: {"X-CSRFToken": csrftoken}
                })
                .then(async(response) => {
                    // if success - update post's content
                    if (response.status === 201) {
                        showMoreButtonControl(postNode);
                        contentNode.innerHTML = submittedContent;
                        console.log(`post id: ${postID} edited successfully`);
                    }
                    // if error - show alert and reload the page
                    else {
                        let response_body = await response.json();

                        throw new Error(response_body.error);                        
                    }
                })
                .catch(error => {
                    alert(error);
                    location.reload();
                })
            });
        });
    }
}

// Controls deleting of a post
function deletePostControl(postNode) {
    let deleteButton = postNode.querySelector(".delete-modal .modal-footer > .btn-danger");
    if (deleteButton !== null) {
        deleteButton.addEventListener("click", () => {
            let csrftoken = getCookie('csrftoken');

            // Send DELETE request
            fetch("/post-comment/post", {
                method: "DELETE",
                body: JSON.stringify({
                    id: postNode.id.substr(5),
                }),
                headers: {"X-CSRFToken": csrftoken}
            })
            .then(async(response) => {
                // if success - update post's content and relaod the page
                if (response.status === 204) {
                    console.log(`post id: ${postNode.id.substr(5)} deleted successfully`);
                    location.reload();
                }
                // if error - show alert and reload the page
                else {
                    let response_body = await response.json();

                    throw new Error(response_body.error);                        
                }
            })
            .catch(error => {
                alert(error);
                location.reload();
            })
        });
    }
}

function updatePostLikeIcon(postNode){
    // Show user's like type on like button
    fetch(`/like/post/${postNode.id.substr(5)}`)
    .then(async(response) => {
        let response_body = await response.json();

        if (response.status === 200) {
            if (response_body.like === "True"){
                const likeButton = postNode.querySelector(".like-button");
                likeButton.classList.add("liked");
                // Add emoji of user's like type to like button
                likeButton.innerHTML = emojiNameToHtml(response_body.emojiType);
            }
        }
        else {
            throw new Error(response_body.error);
        }
    })
    .catch(error => {
        alert(error);
        location.reload();
    })
}

