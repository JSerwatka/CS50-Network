
// Handles POST request and single comment appearance after like
function likeHandling(commentNode) {
    let element = postNode.querySelector(".like-panel")
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
                    updateLikeIcon(commentNode);
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
                    updateLikeIcon(commentNode);
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
    let editButton = postNode.querySelector(".edit-button")
    let deleteButton = postNode.querySelector(".delete-edit-panel .btn-danger")
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
                fetch("/", {
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
    let deleteButton = commentNode.querySelector(".modal-footer > .btn-danger");
    if (deleteButton !== null) {
        deleteButton.addEventListener("click", () => {
            console.log(deleteButton)
            console.log(commentNode)
            let csrftoken = getCookie('csrftoken');

            // Send DELETE request
            fetch("/", {
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

// Adds emoji to like data panel
function updateEmojiList(commentNode, newEmojiType, previousEmojiType=null) {
    // PUT request -> update previous emoji count and visibility
    if (previousEmojiType !== null) {
        // Grab node of previous emoji
        let previousEmojiNode = commentNode.querySelector(`.emoji-list > i[data-name=${previousEmojiType}]`);
        // Decrement its value because of emoji change
        previousEmojiNode.dataset.count -= 1;

        // If amount of emojis of this type less than 1 -> delete it from the list
        if (previousEmojiNode.dataset.count < 1) {
            previousEmojiNode.remove();
        }
    }   
    
    // PUT or POST request -> add new emoji node or update its counter
    let emojiList = commentNode.querySelector("ul.emoji-list");
    let newEmojiNode = emojiList.querySelector(`i[data-name=${newEmojiType}]`);

    // Check if emoji already in emoji list
    // If yes - just increment the counter and refresh it
    if (newEmojiNode) {
        newEmojiNode.dataset.count = parseInt(newEmojiNode.dataset.count) + 1;
    }
    // If no - add emoji to emoji list
    else {
        let wrapper = document.createElement("div");
        wrapper.innerHTML = emojiNameToHtml(newEmojiType);
        emojiList.appendChild(wrapper.firstChild);
    }

    // Make sure that like counter has correct value
    updateLikeCounter(commentNode);
    // Sort emojis by amount of likes
    sortEmojiList(commentNode);
}

function updateLikeCounter(commentNode) {
    let additionalLikes = 0;

    // Emoji tags counter
    let emojiTagCount = 0;
    // All emoji types likes counter
    let emojiTypeCount = 0;

    // Get list of emoji tags
    let emojiTagArray = Array.from(commentNode.querySelector("ul.emoji-list").children)

    // Get sum of emoji tags and data-count values
    for (const key in emojiTagArray) {
        emojiTagCount += 1;
        emojiTypeCount += parseInt(emojiTagArray[key].dataset.count);
    }

    // Get count of additional likes
    additionalLikes = emojiTypeCount - emojiTagCount;

    if (additionalLikes > 0) {
        commentNode.querySelector("span.like-counter").textContent = `+${additionalLikes}`;
    }
    else {
        commentNode.querySelector("span.like-counter").textContent = "0"
    }
}

// Sort emojis by amount of likes
function sortEmojiList(commentNode) {
    let emojiList = commentNode.querySelector("ul.emoji-list")

    if (emojiList.children.length > 1) {
        Array.from(emojiList.children)
        .sort(({dataset: {count: a}}, {dataset: {count: b}}) => parseInt(b) - parseInt(a))
        .forEach((emojiTag) => {
            emojiList.appendChild(emojiTag)
        })
    }
}

function updateLikeIcon(commentNode){
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

function emojiNameToHtml(emojiType) {
    let emojiHtml;

    switch (emojiType) {
        case "like":
            emojiHtml = '<i class="em em---1" aria-role="presentation" aria-label="THUMBS UP SIGN" data-count=1 data-name="like"></i>Like';
            break;
        case "dislike":
            emojiHtml = '<i class="em em--1" aria-role="presentation" aria-label="THUMBS DOWN SIGN" data-count=1 data-name="dislike"></i>Like';
            break;
        case "smile":
            emojiHtml = '<i class="em em-smile" aria-role="presentation" aria-label="SMILING FACE WITH OPEN MOUTH AND SMILING EYES" data-count=1 data-name="smile"></i>Like';
            break;
        case "heart":
            emojiHtml = '<i class="em em-heart" aria-role="presentation" aria-label="HEAVY BLACK HEART" data-count=1 data-name="heart"></i>Like';
            break;
        case "thanks":
            emojiHtml = '<i class="em em-bouquet" aria-role="presentation" aria-label="BOUQUET" data-count=1 data-name="thanks"></i>Like';
            break;
        default:
            emojiHtml = '';
    }

    return emojiHtml;
}

// Shows little number indicator if you hover over emoji in emoji list
function likesAmountIndicatorControl(commentNode) {
    commentNode.querySelectorAll(".emoji-list > i.em").forEach(emojiTag => {
        // Create a like amount indicator element
        let likesAmountIndicator = document.createElement("li");
        likesAmountIndicator.className = "likes-indicator";

        // Show like amount indicator
        emojiTag.onmouseover = (event) => {
            // Make sure that the appended child doesn't inherit this eventlistener
            if (event.target.classList.contains("em")) {
                likesAmountIndicator.innerHTML = event.target.dataset.count;
                event.target.appendChild(likesAmountIndicator);
            }
        }

        // Remove like amount indicator
        emojiTag.onmouseout = () => {
            likesAmountIndicator.remove();
        }

    })
}

function likePanelAnimationControl(commentNode) {
    let likePanel = commentNode.querySelector(".like-panel")
    const emojiPanel = likePanel.querySelector(".emoji-choice");
    let timeoutVar;

    // On hover show like-panel
    likePanel.addEventListener("mouseover", () => {
        clearTimeout(timeoutVar)
        emojiPanel.classList.remove("hidden");
        emojiPanel.classList.add("like-panel-in");
    })

    // On hover out hide like-panel after 1s
    likePanel.addEventListener("mouseout", () => {
        timeoutVar = setTimeout(() => {
            emojiPanel.classList.remove("like-panel-in");
            emojiPanel.classList.add("hidden");
        }, 1000)
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

// Show show-more button if comment's content overflowing
function showMoreButtonControl(commentNode) {
    let commentContent = commentNode.querySelector(".comment-content")
    let showMore = commentContent.nextElementSibling

    let isOverflowing = (commentContent.clientWidth < commentContent.scrollWidth)
                        || (commentContent.clientHeight < commentContent.scrollHeight); 
                    
    // Text overflowing -> show show-more button and handle click event
    if (isOverflowing) {
        showMore.classList.remove("hidden")

        showMore.onclick = () => {
            // Make comment content short or full height
            commentContent.classList.remove("short");
            showMore.classList.add("hidden")
        }
    }
    // Text not overflowing -> hide show-more button
    else {
        showMore.classList.add("hidden")
    }
}