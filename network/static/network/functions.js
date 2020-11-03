// TODO: hide like-comment panel when editing

// Handles POST request and single post appearance after like
function likeHandling() {
    document.querySelectorAll(".like-panel").forEach((element) => {
        // Handle like post/comment
        element.addEventListener('click', (event) => {
            let emojiType;
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

            // Already liked button - update like's emoji type
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
                        updateLikeIcon(postNode);
                        // Update like counter and emoji list
                        // TODO: każda zmiana lika spowoduje dodanie nowego emoji, jeśli go nie ma - naprawić
                        updateEmojiList(postNode, emojiType);
    
                    }
                    else {
                        throw new Error("Unexpected error")  //TODO: Change message                      
                    }
                })
                .catch(error => {
                    alert(error)
                })
            }
            // No liked yet - save liked
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
                        updateLikeIcon(postNode);
                        // Update like counter and emoji list
                        updateEmojiList(postNode, emojiType);
    
                    }
                    else {
                        throw new Error("Post doesn't exist or u already liked this post")                        
                    }
                })
                .catch(error => {
                    alert(error)
                })
            }
                
        })
    })  
}

// Controls asynchronous editing of a post
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

// Adds emoji to like/comment data panel
function updateEmojiList(postNode, emojiType) {
    let emojiList = postNode.querySelector("ul.emoji-list")

    // Check if emoji already in emoji list
    // If yes - just increment the counter
    if (emojiList.querySelector(`a[name=${emojiType}]`)) {
        updateLikeCounter(postNode, 1)
    }
    // If no - add emoji to emoji list
    else {
        let wrapper = document.createElement("div");
        wrapper.innerHTML = emojiNameToHtml(emojiType)
        emojiList.appendChild(wrapper.firstChild)
    }
}

// TODO: this counter doesn't work - fix it
function updateLikeCounter(postNode, change=0) {
    // Get emoji count and current likes count
    let emojiCount = postNode.querySelector("ul.emoji-list").childElementCount
    let oldLikesCount = parseInt(postNode.querySelector("span.like-counter").textContent)

    if (oldLikesCount > 0) {
        // Update likes count
        postNode.querySelector("span.like-counter").textContent = `+${oldLikesCount - emojiCount + change}`
    }
}

function updateLikeIcon(postNode){
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

function emojiNameToHtml(emojiType) {
    let emojiHtml;

    switch (emojiType) {
        case "like":
            emojiHtml = '<i class="em em---1" aria-role="presentation" aria-label="THUMBS UP SIGN"><a name="like"></a></i>like';
            break;
        case "dislike":
            emojiHtml = '<i class="em em--1" aria-role="presentation" aria-label="THUMBS DOWN SIGN"><a name="dislike"></a></i>like';
            break;
        case "smile":
            emojiHtml = '<i class="em em-smile" aria-role="presentation" aria-label="SMILING FACE WITH OPEN MOUTH AND SMILING EYES"><a name="smile"></a></i>like';
            break;
        case "heart":
            emojiHtml = '<i class="em em-heart" aria-role="presentation" aria-label="HEAVY BLACK HEART"><a name="heart"></a></i>like';
            break;
        case "thanks":
            emojiHtml = '<i class="em em-bouquet" aria-role="presentation" aria-label="BOUQUET"><a name="thanks"></a></i>like';
            break;
        default:
            emojiHtml = '';
    }

    return emojiHtml;
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

