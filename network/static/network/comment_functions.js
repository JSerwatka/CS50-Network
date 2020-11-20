
// Handles POST request and single comment appearance after like
function likeCommentControl(commentNode) {
    let element = commentNode.querySelector(".like-panel")
    // Handle like comment
    element.addEventListener('click', (event) => {
        let csrftoken = getCookie('csrftoken');
        let emojiType;

        // Look for event's emoji type
        // Check if like button is a target
        if (event.target.name === "like") {
            emojiType = event.target.name;
        }
        // Check if emoji list is a target
        else if (typeof event.target.dataset.name === "string"){
            emojiType = event.target.dataset.name;
        }  
        // Something else is a target
        else {
            return false;
        }
        // Already liked - update like's emoji type
        if (commentNode.querySelector(".like-button").classList.contains("liked")) {
            fetch(`/like/comment/${commentNode.id.substr(8)}`, {
                method: "PUT",
                body: JSON.stringify({
                    emojiType: emojiType
                }),
                headers: {"X-CSRFToken": csrftoken}
            })
            .then(async(response) => {
                // Successful like -> update comment view
                if (response.status === 201) {
                    console.log(`comment id: ${commentNode.id.substr(8)} like updated successfully`)
                    // Update like button emoji and class
                    updateCommentLikeIcon(commentNode);
                    // Update like counter and emoji list
                    let previousEmojiType = commentNode.querySelector(".like-button > i").dataset.name;
                    updateEmojiList(commentNode, emojiType, previousEmojiType);
                    // Reconnect like amount indicator event to each emoji
                    likesAmountIndicatorControl(commentNode);
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
            fetch(`/like/comment/${commentNode.id.substr(8)}`, {
                method: "POST",
                body: JSON.stringify({
                    emojiType: emojiType
                }),
                headers: {"X-CSRFToken": csrftoken}
            })
            .then(async(response) => {
                // Successful like -> update comment view
                if (response.status === 201) {
                    console.log(`comment id: ${commentNode.id.substr(8)} liked successfully`)
                    // Update like button emoji and class
                    updateCommentLikeIcon(commentNode);
                    // Update like counter and emoji list
                    updateEmojiList(commentNode, emojiType);
                    // Reconnect like amount indicator event to each emoji
                    likesAmountIndicatorControl(commentNode);
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

// Controls asynchronous editing of a comment
function editCommentControl(commentNode) {
    let modalDialog = commentNode.querySelector(".edit-modal");

    if (modalDialog !== null) {
        $(modalDialog).on('show.bs.modal', () => {
            // Get save button and modal body
            let saveButton = modalDialog.querySelector(".modal-footer > .btn-primary");
            let modalBody = modalDialog.querySelector(".modal-body");

            // Get comment id
            const commentID = commentNode.id.substr(8);

            // Get content of comment to be edited
            let contentNode = commentNode.querySelector("div.comment-content");
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
                fetch("/post-comment/comment", {
                    method: "PUT",
                    body: JSON.stringify({
                        id: commentID,
                        content: submittedContent,
                    }),
                    headers: {"X-CSRFToken": csrftoken}
                })
                .then(async(response) => {
                    // if success - update comment's content
                    if (response.status === 201) {
                        showMoreButtonControl(commentNode);
                        contentNode.innerHTML = submittedContent;
                        console.log(`comment id: ${commentID} edited successfully`);
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
                    id: commentNode.id.substr(8),
                }),
                headers: {"X-CSRFToken": csrftoken}
            })
            .then(async(response) => {
                // if success - update comment's content and relaod the page
                if (response.status === 204) {
                    console.log(`Comment id: ${commentNode.id.substr(8)} deleted successfully`)
                    location.reload()
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
        })
    }
}

function updateCommentLikeIcon(commentNode){
    // Show user's like type on like button
    fetch(`/like/comment/${commentNode.id.substr(8)}`)
    .then(async(response) => {
        let response_body = await response.json();

        if (response.status === 200) {
            if (response_body.like === "True"){
                const likeButton = commentNode.querySelector(".like-button");
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