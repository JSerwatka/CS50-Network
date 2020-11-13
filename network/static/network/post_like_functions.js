
// Handles POST request and single post appearance after like
function likeHandling(postNode) {
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
                    updateLikeIcon(postNode);
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
                    updateLikeIcon(postNode);
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
            console.log(deleteButton)
            console.log(postNode)
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

// Adds emoji to like/comment data panel
function updateEmojiList(postNode, newEmojiType, previousEmojiType=null) {
    // PUT request -> update previous emoji count and visibility
    if (previousEmojiType !== null) {
        // Grab node of previous emoji
        let previousEmojiNode = postNode.querySelector(`.emoji-list > i[data-name=${previousEmojiType}]`);
        // Decrement its value because of emoji change
        previousEmojiNode.dataset.count -= 1;

        // If amount of emojis of this type less than 1 -> delete it from the list
        if (previousEmojiNode.dataset.count < 1) {
            previousEmojiNode.remove();
        }
    }   
    
    // PUT or POST request -> add new emoji node or update its counter
    let emojiList = postNode.querySelector("ul.emoji-list");
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
    updateLikeCounter(postNode);
    // Sort emojis by amount of likes
    sortEmojiList(postNode);
}

function updateLikeCounter(postNode) {
    let additionalLikes = 0;

    // Emoji tags counter
    let emojiTagCount = 0;
    // All emoji types likes counter
    let emojiTypeCount = 0;

    // Get list of emoji tags
    let emojiTagArray = Array.from(postNode.querySelector("ul.emoji-list").children)

    // Get sum of emoji tags and data-count values
    for (const key in emojiTagArray) {
        emojiTagCount += 1;
        emojiTypeCount += parseInt(emojiTagArray[key].dataset.count);
    }

    // Get count of additional likes
    additionalLikes = emojiTypeCount - emojiTagCount;

    if (additionalLikes > 0) {
        postNode.querySelector("span.like-counter").textContent = `+${additionalLikes}`;
    }
    else {
        postNode.querySelector("span.like-counter").textContent = "0"
    }
}

// Sort emojis by amount of likes
function sortEmojiList(postNode) {
    let emojiList = postNode.querySelector("ul.emoji-list")

    if (emojiList.children.length > 1) {
        Array.from(emojiList.children)
        .sort(({dataset: {count: a}}, {dataset: {count: b}}) => parseInt(b) - parseInt(a))
        .forEach((emojiTag) => {
            emojiList.appendChild(emojiTag)
        })
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
function likesAmountIndicatorControl(postNode) {
    postNode.querySelectorAll(".emoji-list > i.em").forEach(emojiTag => {
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

function likePanelAnimationControl(postNode) {
    let likePanel = postNode.querySelector(".like-panel")
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

// Show show-more button if post's content overflowing
function showMoreButtonControl(postNode) {
    let postContent = postNode.querySelector(".post-content")
    let showMore = postContent.nextElementSibling

    let isOverflowing = (postContent.clientWidth < postContent.scrollWidth)
                        || (postContent.clientHeight < postContent.scrollHeight); 
                    
    // Text overflowing -> show show-more button and handle click event
    if (isOverflowing) {
        showMore.classList.remove("hidden")

        showMore.onclick = () => {
            // Make post content short or full height
            postContent.classList.remove("short");
            showMore.classList.add("hidden")
        }
    }
    // Text not overflowing -> hide show-more button
    else {
        showMore.classList.add("hidden")
    }
}

