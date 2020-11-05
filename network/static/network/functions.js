// TODO: sort emoji by data-docunt
// TODO: add possibility to delete post
// TODO: possibility to follow user
// TODO: fix default photo not showing
// TODO: add your photo option

// Handles POST request and single post appearance after like
function likeHandling() {
    document.querySelectorAll(".like-panel").forEach((element) => {
        // Handle like post/comment
        element.addEventListener('click', (event) => {
            let emojiType;
            let postNode = event.target;
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

            // Get post node regarding of what triggered it
            while (postNode.className !== "post") { 
                postNode = postNode.parentElement;
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
                    // Show edit button
                    event.target.classList.toggle("hidden");

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
    });
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
        wrapper.innerHTML = emojiNameToHtml(newEmojiType)
        emojiList.appendChild(wrapper.firstChild)
    }

    // Make sure that like counter has correct value
    updateLikeCounter(postNode)
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
            emojiHtml = '<i class="em em---1" aria-role="presentation" aria-label="THUMBS UP SIGN" data-count=1 data-name="like"></i>like';
            break;
        case "dislike":
            emojiHtml = '<i class="em em--1" aria-role="presentation" aria-label="THUMBS DOWN SIGN" data-count=1 data-name="dislike"></i>like';
            break;
        case "smile":
            emojiHtml = '<i class="em em-smile" aria-role="presentation" aria-label="SMILING FACE WITH OPEN MOUTH AND SMILING EYES" data-count=1 data-name="smile"></i>like';
            break;
        case "heart":
            emojiHtml = '<i class="em em-heart" aria-role="presentation" aria-label="HEAVY BLACK HEART" data-count=1 data-name="heart"></i>like';
            break;
        case "thanks":
            emojiHtml = '<i class="em em-bouquet" aria-role="presentation" aria-label="BOUQUET" data-count=1 data-name="thanks"></i>like';
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

